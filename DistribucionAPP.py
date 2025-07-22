import pandas as pd
import numpy as np
import os # Import os module to check for file existence
import streamlit as st # Import Streamlit library

st.title("Aplicación de Distribución de Inventario")

# Initialize df_stores and df_distribution to None
df_stores = None
df_distribution = None

# --- Carga de archivos usando Streamlit ---
st.header("Cargar Archivos de Datos")

stores_file = st.file_uploader("Sube el archivo de información de Tiendas (CSV)", type=["csv"], key="stores_upload")
distribution_file = st.file_uploader("Sube el archivo de Cantidades e Inner Pack (CSV)", type=["csv"], key="distribution_upload")

# Process files only if both are uploaded
if stores_file is not None and distribution_file is not None:
    try:
        # Read stores file
        # Assuming semicolon delimiter based on previous interactions
        df_stores = pd.read_csv(stores_file, sep=';', header=0)
        st.success("Archivo de tiendas cargado exitosamente.")

        # Validate required columns in df_stores
        if not all(col in df_stores.columns for col in ['Nombre', 'Formato', 'Participacion']):
             st.error("Error en el archivo de tiendas: Debe contener las columnas 'Nombre', 'Formato' y 'Participacion'.")
             df_stores = None # Indicate failure by setting df_stores to None
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


    # --- Ejecutar lógica de distribución solo si ambos DataFrames se cargaron y validaron correctamente ---
    if df_stores is not None and df_distribution is not None:
        st.header("Resultados de la Distribución")

        # Definir la cantidad mínima por tienda
        minimum_quantity = 6

        # Identify store names and priorities
        store_columns = df_stores['Nombre'].tolist()
        prioritized_store_names = df_stores[df_stores['Formato'].isin(['Grande', 'Mediano'])]['Nombre'].tolist()
        non_prioritized_store_names = df_stores[df_stores['Formato'] == 'Pequeño']['Nombre'].tolist()
        all_store_names = prioritized_store_names + non_prioritized_store_names


        # --- 3. Ajustar la cantidad total a distribuir (múltiplo de Inner Pack o Cantidad en sistema) ---
        df_distribution['Adjusted Total Quantity'] = 0 # Initialize as integer

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


        # --- 4. Modificar la distribución inicial (considerando Inner Pack o distribucion unitaria) ---
        for store_name in store_columns:
            if store_name not in df_distribution.columns:
                df_distribution[store_name] = 0.0 # Initialize as float for calculations

        for index, row in df_distribution.iterrows():
            adjusted_total_quantity = row['Adjusted Total Quantity']
            inner_pack = row['Inner Pack']

            inner_pack_for_distribution = int(inner_pack) if inner_pack > 0 else 1

            if adjusted_total_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0.0 # Keep as float during calculations
                continue

            for store_index, store in df_stores.iterrows():
                store_name = store['Nombre']
                participation = store['Participacion']

                initial_theoretical_quantity = adjusted_total_quantity * participation
                rounded_quantity = round(initial_theoretical_quantity / inner_pack_for_distribution) * inner_pack_for_distribution
                adjusted_initial_quantity = max(0.0, rounded_quantity) # Keep as float


                df_distribution.loc[index, store_name] = adjusted_initial_quantity


        # --- 5. Aplicar cantidad mínima (6) ---
        # Apply minimum in-place
        for index, row in df_distribution.iterrows():
            for store_name in store_columns:
                initial_calculated_quantity = row[store_name]
                if initial_calculated_quantity < minimum_quantity:
                    df_distribution.loc[index, store_name] = 0.0 # Keep as float


        # --- 6. Balanceo Final para mantener el total ORIGINAL y asegurar enteros ---
        st.subheader("Proceso de Balanceo Final")

        mismatched_rows_original_balance = [] # To track rows with balancing issues before integer conversion

        for index, row in df_distribution.iterrows():
            original_quantity = row['Cantidades en sistema']

            if pd.isna(original_quantity) or original_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0.0 # Ensure 0 and float
                continue

            current_distributed_sum = row[store_columns].sum()
            balancing_difference = int(round(original_quantity - current_distributed_sum)) # Balance against ORIGINAL total, rounded to integer


            if balancing_difference != 0:
                stores_with_non_zero = [
                    store_name for store_name in store_columns
                    if df_distribution.loc[index, store_name] > 0
                ]

                # Balancing order: subtract from non-prioritized (>0), then prioritized (>min_qty). Add to prioritized, then non-prioritized.
                if balancing_difference < 0:
                     balancing_order = [name for name in non_prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > 0] + \
                                       [name for name in prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > minimum_quantity]
                else: # balancing_difference > 0
                     balancing_order = [name for name in prioritized_store_names if name in stores_with_non_zero] + \
                                       [name for name in non_prioritized_store_names if name in stores_with_non_zero]


                balance_index = 0
                max_iterations = len(all_store_names) * abs(balancing_difference) + 20 # Safeguarda

                initial_balancing_difference = balancing_difference # Store initial difference for warning

                while balancing_difference != 0 and balancing_order and max_iterations > 0:
                    store_name = balancing_order[balance_index % len(balancing_order)]

                    if balancing_difference > 0:
                        df_distribution.loc[index, store_name] += 1.0 # Add 1 as float
                        balancing_difference -= 1
                        max_iterations -= 1
                    else: # balancing_difference < 0
                        can_subtract = False
                        if df_distribution.loc[index, store_name] > 0:
                            if store_name in prioritized_store_names:
                                if df_distribution.loc[index, store_name] > minimum_quantity:
                                    can_subtract = True
                            else: # Non-prioritized store
                                 can_subtract = True

                        if can_subtract:
                            df_distribution.loc[index, store_name] -= 1.0 # Subtract 1 as float
                            balancing_difference += 1
                            max_iterations -= 1

                    balance_index += 1
                    # Recreate balancing_order if needed
                    if balancing_difference != 0 and balance_index % len(balancing_order) == 0:
                         stores_with_non_zero = [name for name in store_columns if df_distribution.loc[index, name] > 0]
                         if balancing_difference < 0:
                              balancing_order = [name for name in non_prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > 0] + \
                                                [name for name in prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > minimum_quantity]
                         else: # balancing_difference > 0
                              balancing_order = [name for name in prioritized_store_names if name in stores_with_non_zero] + \
                                                [name for name in non_prioritized_store_names if name in stores_with_non_zero]
                         if not balancing_order and balancing_difference != 0:
                             st.warning(f"Advertencia (Balanceo): No se pudo balancear completamente la distribución para la fila {index}. Diferencia restante: {balancing_difference}")
                             mismatched_rows_original_balance.append({'Index': index, 'Original Quantity': original_quantity, 'Final Sum Before Int Conv': row[store_columns].sum(), 'Difference': initial_balancing_difference})
                             break # Exit if no valid stores left to balance

            # Final check after balancing loop
            if balancing_difference != 0:
                 st.warning(f"Advertencia (Balanceo Final): Balanceo para la fila {index} al total original no exitoso. Diferencia restante: {balancing_difference}")
                 # Add to mismatched_rows list if not already added
                 if index not in [row['Index'] for row in mismatched_rows_original_balance]:
                      mismatched_rows_original_balance.append({'Index': index, 'Original Quantity': original_quantity, 'Final Sum Before Int Conv': row[store_columns].sum(), 'Difference': initial_balancing_difference})


        # Ensure all store quantities are non-negative integers
        for store_name in store_columns:
            if df_distribution.loc[index, store_name] < 0:
                df_distribution.loc[index, store_name] = 0
            df_distribution.loc[index, store_name] = int(df_distribution.loc[index, store_name]) # Convert to integer


        # --- Agregar verificación de suma total contra Cantidades en sistema ORIGINAL ---
        # This verification is now against Original Quantity
        df_distribution['Suma Distribuida'] = df_distribution[store_columns].sum(axis=1)
        df_distribution['Validacion (Cant. Sistema - Suma Dist.)'] = df_distribution['Cantidades en sistema'] - df_distribution['Suma Distribuida']


        st.subheader("Verificación de Sumas Finales contra Cantidades en Sistema Original")
        mismatched_rows_final = df_distribution[df_distribution['Validacion (Cant. Sistema - Suma Dist.)'] != 0]

        if not mismatched_rows_final.empty:
            st.warning("¡Advertencia: Se encontraron diferencias entre 'Cantidades en sistema' original y la suma de cantidades distribuidas en las siguientes filas!")
            st.dataframe(mismatched_rows_final[['Cantidades en sistema', 'Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']])
        else:
            st.success("Verificación de sumas finales completada: Todas las sumas de distribución coinciden con la 'Cantidades en sistema' original.")

        # --- 7. Generar y mostrar la tabla de resultados ---
        store_columns_with_format = [f"{row['Nombre']} ({row['Formato']})" for index, row in df_stores.iterrows()]
        final_df_columns = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns_with_format + ['Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']

        columns_to_select = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns + ['Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']
        if all(col in df_distribution.columns for col in columns_to_select):
            df_final_tabulated_distribution = df_distribution[columns_to_select].copy()

            rename_dict = {store_name: f"{store_name} ({df_stores.loc[df_stores['Nombre'] == store_name, 'Formato'].iloc[0]})" for store_name in store_columns}
            df_final_tabulated_distribution.rename(columns=rename_dict, inplace=True)

            df_final_tabulated_distribution = df_final_tabulated_distribution[final_df_columns]

            st.subheader("Tabla de Distribución Final")
            st.dataframe(df_final_tabulated_distribution)

            # Option to download the table
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
