import pandas as pd
import numpy as np
import os
import streamlit as st

st.set_page_config(layout="wide")

st.title("Aplicación de Distribución de Inventario")

# Initialize DataFrames
df_stores = None
df_distribution = None

# --- File Uploads ---
st.header("Cargar Archivos de Datos")

upload_container = st.container()

with upload_container:
    stores_file = st.file_uploader("Sube el archivo de información de Tiendas (CSV)", type=["csv"], key="stores_upload")
    distribution_file = st.file_uploader("Sube el archivo de Cantidades e Inner Pack (CSV)", type=["csv"], key="distribution_upload")

# Process files if both are uploaded
if stores_file is not None and distribution_file is not None:
    try:
        # Read stores file
        # Assuming semicolon delimiter based on previous interactions
        df_stores = pd.read_csv(stores_file, sep=';', header=0)
        st.success("Archivo de tiendas cargado exitosamente.")

        # Validate required columns in df_stores
        if not all(col in df_stores.columns for col in ['Nombre', 'Formato', 'Participacion']):
             st.error("Error en el archivo de tiendas: Debe contener las columnas 'Nombre', 'Formato' y 'Participacion'.")
             df_stores = None
        else:
             # Ensure participation column is numeric
             df_stores['Participacion'] = pd.to_numeric(df_stores['Participacion'], errors='coerce').fillna(0)

    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo de tiendas: {e}")
        df_stores = None

    try:
        # Read distribution file
        # Assuming semicolon delimiter based on previous interactions
        df_distribution = pd.read_csv(distribution_file, sep=';', header=0)
        st.success("Archivo de cantidades e Inner Pack cargado exitosamente.")

        # Handle Inner Pack and Cantidades en sistema columns
        if 'Inner Pack' not in df_distribution.columns:
            st.error("Error en el archivo de distribución: Columna 'Inner Pack' no encontrada.")
            df_distribution = None
        elif 'Cantidades en sistema' not in df_distribution.columns:
             st.error("Error en el archivo de distribución: Columna 'Cantidades en sistema' no encontrada.")
             df_distribution = None
        else:
            df_distribution['Inner Pack'] = pd.to_numeric(df_distribution['Inner Pack'], errors='coerce').fillna(1).astype(int)
            df_distribution['Cantidades en sistema'] = pd.to_numeric(df_distribution['Cantidades en sistema'], errors='coerce')
            # Remove rows where 'Cantidades en sistema' is NaN after conversion
            df_distribution.dropna(subset=['Cantidades en sistema'], inplace=True)

    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo de distribución: {e}")
        df_distribution = None

    # --- Run Distribution Logic if both DataFrames are loaded and validated ---
    if df_stores is not None and df_distribution is not None:
        st.header("Resultados de la Distribución")

        # Definir la cantidad mínima por tienda
        minimum_quantity = 6

        # Identify store names and priorities
        store_columns = df_stores['Nombre'].tolist()
        prioritized_store_names = df_stores[df_stores['Formato'].isin(['Grande', 'Mediano'])]['Nombre'].tolist()
        non_prioritized_store_names = df_stores[df_stores['Formato'] == 'Pequeño']['Nombre'].tolist()
        all_store_names = prioritized_store_names + non_prioritized_store_names

        # --- Distribution Logic ---
        # 3. Calculate Adjusted Total Quantity (used internally for initial calc basis)
        df_distribution['Adjusted Total Quantity'] = 0

        for index, row in df_distribution.iterrows():
            quantity = row['Cantidades en sistema']
            inner_pack = row['Inner Pack']

            if pd.isna(quantity) or quantity <= 0:
                df_distribution.loc[index, 'Adjusted Total Quantity'] = 0
            elif inner_pack <= 0:
                df_distribution.loc[index, 'Adjusted Total Quantity'] = int(round(quantity))
            else:
                try:
                    quantity_numeric = float(quantity)
                    inner_pack_numeric = int(inner_pack)
                    adjusted_quantity = (quantity_numeric // inner_pack_numeric) * inner_pack_numeric
                    df_distribution.loc[index, 'Adjusted Total Quantity'] = adjusted_quantity
                except (ValueError, TypeError) as e:
                    st.warning(f"Advertencia (Ajuste Total): No se pudo procesar la fila {index} para ajuste total: {e}. Asignando 0.")
                    df_distribution.loc[index, 'Adjusted Total Quantity'] = 0

        df_distribution['Adjusted Total Quantity'] = df_distribution['Adjusted Total Quantity'].astype(int)

        # 4. Initial Distribution (Distributing Inner Packs or units if Inner Pack <= 0)
        for store_name in store_columns:
            if store_name not in df_distribution.columns:
                df_distribution[store_name] = 0.0

        for index, row in df_distribution.iterrows():
            original_quantity = row['Cantidades en sistema']
            inner_pack = row['Inner Pack']

            if pd.isna(original_quantity) or original_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0.0
                continue

            if inner_pack > 0:
                inner_pack_numeric = int(inner_pack)
                total_units_to_distribute = int(round(original_quantity / inner_pack_numeric))
                unit_size = inner_pack_numeric
            else:
                total_units_to_distribute = int(round(original_quantity))
                unit_size = 1

            if total_units_to_distribute <= 0:
                 for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0.0
                 continue

            initial_distributed_units = {}
            for store_index, store in df_stores.iterrows():
                store_name = store['Nombre']
                participation = store['Participacion']
                initial_theoretical_units = total_units_to_distribute * participation
                initial_distributed_units[store_name] = int(round(initial_theoretical_units))

            for store_name in store_columns:
                 df_distribution.loc[index, store_name] = initial_distributed_units[store_name] * unit_size

        # 5. Apply Minimum Quantity (6)
        for index, row in df_distribution.iterrows():
            for store_name in store_columns:
                initial_calculated_quantity = row[store_name]
                if initial_calculated_quantity < minimum_quantity:
                    df_distribution.loc[index, store_name] = 0.0

        # 6. Final Balancing to match ORIGINAL Total and ensure integers
        st.subheader("Proceso de Balanceo Final")

        for index, row in df_distribution.iterrows():
            original_quantity = row['Cantidades en sistema']

            if pd.isna(original_quantity) or original_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0
                continue

            current_distributed_sum = row[store_columns].sum()
            balancing_difference = int(round(original_quantity - current_distributed_sum))

            if balancing_difference != 0:
                stores_eligible_for_balance = [
                    store_name for store_name in store_columns
                    if df_distribution.loc[index, store_name] > 0
                ]

                if balancing_difference < 0:
                     balancing_order = [name for name in non_prioritized_store_names if name in stores_eligible_for_balance and df_distribution.loc[index, name] > 0] + \
                                       [name for name in prioritized_store_names if name in stores_eligible_for_balance and df_distribution.loc[index, name] > minimum_quantity]
                else:
                     balancing_order = [name for name in prioritized_store_names if name in stores_eligible_for_balance] + \
                                       [name for name in non_prioritized_store_names if name in stores_eligible_for_balance]

                balance_index = 0
                max_iterations = len(all_store_names) * abs(balancing_difference) + 20

                while balancing_difference != 0 and balancing_order and max_iterations > 0:
                    store_name = balancing_order[balance_index % len(balancing_order)]

                    if balancing_difference > 0:
                        df_distribution.loc[index, store_name] += 1
                        balancing_difference -= 1
                        max_iterations -= 1
                    else:
                        can_subtract = False
                        if df_distribution.loc[index, store_name] > 0:
                            if store_name in prioritized_store_names:
                                if df_distribution.loc[index, store_name] > minimum_quantity:
                                    can_subtract = True
                            else:
                                 can_subtract = True

                        if can_subtract:
                            df_distribution.loc[index, store_name] -= 1
                            balancing_difference += 1
                            max_iterations -= 1

                    balance_index += 1
                    if balancing_difference != 0 and balance_index % len(balancing_order) == 0:
                         stores_eligible_for_balance = [name for name in store_columns if df_distribution.loc[index, name] > 0]
                         if balancing_difference < 0:
                              balancing_order = [name for name in non_prioritized_store_names if name in stores_eligible_for_balance and df_distribution.loc[index, name] > 0] + \
                                                [name for name in prioritized_store_names if name in stores_eligible_for_balance and df_distribution.loc[index, name] > minimum_quantity]
                         else:
                              balancing_order = [name for name in prioritized_store_names if name in stores_eligible_for_balance] + \
                                                [name for name in non_prioritized_store_names if name in stores_eligible_for_balance]
                         if not balancing_order and balancing_difference != 0:
                             st.warning(f"Advertencia: No se pudo balancear completamente la distribución para la fila {index}. Diferencia restante: {balancing_difference}")
                             break

            if balancing_difference != 0:
                 st.warning(f"Advertencia: Balanceo final para la fila {index} al total original no exitoso. Diferencia restante: {balancing_difference}")

        for store_name in store_columns:
            if df_distribution.loc[index, store_name] < 0:
                df_distribution.loc[index, store_name] = 0
            df_distribution.loc[index, store_name] = int(df_distribution.loc[index, store_name])

        # --- Verification and Final Table ---
        df_distribution['Suma Distribuida'] = df_distribution[store_columns].sum(axis=1)
        df_distribution['Validacion (Cant. Sistema - Suma Dist.)'] = df_distribution['Cantidades en sistema'] - df_distribution['Suma Distribuida']

        st.subheader("Verificación de Sumas Finales contra Cantidades en Sistema Original")
        mismatched_rows_final = df_distribution[df_distribution['Validacion (Cant. Sistema - Suma Dist.)'] != 0]

        if not mismatched_rows_final.empty:
            st.warning("¡Advertencia: Se encontraron diferencias entre 'Cantidades en sistema' original y la suma de cantidades distribuidas en las siguientes filas!")
            st.dataframe(mismatched_rows_final[['Cantidades en sistema', 'Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']])
        else:
            st.success("Verificación de sumas finales completada: Todas las sumas de distribución coinciden con la 'Cantidades en sistema' original.")

        st.subheader("Tabla de Distribución Final")

        store_columns_with_format = [f"{row['Nombre']} ({row['Formato']})" for index, row in df_stores.iterrows()]
        final_df_columns = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns_with_format + ['Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']

        columns_to_select = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns + ['Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']
        if all(col in df_distribution.columns for col in columns_to_select):
            df_final_tabulated_distribution = df_distribution[columns_to_select].copy()

            rename_dict = {store_name: f"{store_name} ({df_stores.loc[df_stores['Nombre'] == store_name, 'Formato'].iloc[0]})" for store_name in store_columns}
            df_final_tabulated_distribution.rename(columns=rename_dict, inplace=True)

            df_final_tabulated_distribution = df_final_tabulated_distribution[final_df_columns]

            st.dataframe(df_final_tabulated_distribution)

            csv = df_final_tabulated_distribution.to_csv(index=False, sep=';').encode('utf-8')
            st.download_button(
                label="Descargar tabla de distribución final (CSV)",
                data=csv,
                file_name='distribucion_final_con_validación.csv',
                mime='text/csv'
            )
        else:
            st.error("Error: No se encontraron todas las columnas requeridas para la tabla final.")

    elif stores_file is not None or distribution_file is not None:
         st.info("Por favor, sube ambos archivos para iniciar la distribución.")

else:
    st.info("Sube tus archivos para iniciar la distribución.")
