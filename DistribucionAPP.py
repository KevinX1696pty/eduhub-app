import pandas as pd
import numpy as np
import os # Import os module to check for file existence

# --- 1. Definir la estructura de las tiendas (Leer desde archivo) ---
# Especifica la ruta del archivo de tiendas que subirás
stores_file_path = '/content/df_stores.csv' # Cambia 'df_stores.csv' si tu archivo tiene otro nombre

# Verifica si el archivo de tiendas existe antes de intentar leerlo
if not os.path.exists(stores_file_path):
    print(f"Error: No se encontró el archivo de tiendas en {stores_file_path}. Por favor, sube el archivo.")
    # Si el archivo no se encuentra, no podemos continuar. Puedes agregar un 'exit()' aquí si es crítico.
    # Por ahora, imprimimos el error y el script intentará cargar el otro archivo, lo que probablemente fallará después.
else:
    try:
        # Cargar la información de las tiendas desde el archivo (asumiendo CSV con ';')
        df_stores = pd.read_csv(stores_file_path, sep=';', header=0)
        print("Archivo de tiendas cargado exitosamente.")
        # Validar que las columnas necesarias existan en df_stores
        if not all(col in df_stores.columns for col in ['Nombre', 'Formato', 'Participacion']):
             print("Error: El archivo de tiendas debe contener las columnas 'Nombre', 'Formato' y 'Participacion'.")
             df_stores = None # Set df_stores to None to indicate failure
        else:
             # Asegurar que la columna de participación sea numérica
             df_stores['Participacion'] = pd.to_numeric(df_stores['Participacion'], errors='coerce').fillna(0)


    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de tiendas en {stores_file_path}. Por favor, verifica la ruta del archivo.")
        df_stores = None
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo de tiendas CSV: {e}")
        df_stores = None


# Continuar solo si df_stores se cargó correctamente
if df_stores is not None:

    # Definir la cantidad mínima por tienda
    minimum_quantity = 6

    # Identificar la lista de nombres de tiendas
    store_columns = df_stores['Nombre'].tolist()
    prioritized_store_names = df_stores[df_stores['Formato'].isin(['Grande', 'Mediano'])]['Nombre'].tolist()
    non_prioritized_store_names = df_stores[df_stores['Formato'] == 'Pequeño']['Nombre'].tolist()
    all_store_names = prioritized_store_names + non_prioritized_store_names # Lista para iterar en orden

    # --- 2. Cargar los datos con 'Inner Pack' (Leer desde archivo) ---
    distribution_file_path = '/content/Cantidades&Innerpack.csv' # Especifica la ruta de tu archivo de cantidades

    # Verifica si el archivo de distribución existe antes de intentar leerlo
    if not os.path.exists(distribution_file_path):
        print(f"Error: No se encontró el archivo de distribución en {distribution_file_path}. Por favor, sube el archivo.")
        df_distribution = None # Set df_distribution to None to indicate failure
    else:
        try:
            # Cargar los datos del archivo CSV con delimitador de punto y coma y encabezado
            df_distribution = pd.read_csv(distribution_file_path, sep=';', header=0)
            print("Archivo de datos cargado exitosamente.")

            # Manejar la columna 'Inner Pack'
            if 'Inner Pack' not in df_distribution.columns:
                print("Error: Columna 'Inner Pack' no encontrada en el archivo de distribución.")
                df_distribution = None
            else:
                df_distribution['Inner Pack'] = pd.to_numeric(df_distribution['Inner Pack'], errors='coerce').fillna(1).astype(int)
                if 'Cantidades en sistema' not in df_distribution.columns:
                    print("Error: Columna 'Cantidades en sistema' no encontrada en el archivo de distribución.")
                    df_distribution = None
                else:
                    df_distribution['Cantidades en sistema'] = pd.to_numeric(df_distribution['Cantidades en sistema'], errors='coerce')
                    # Eliminar filas donde 'Cantidades en sistema' es NaN después de la conversión
                    df_distribution.dropna(subset=['Cantidades en sistema'], inplace=True)

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo en {distribution_file_path}. Por favor, verifica la ruta del archivo.")
            df_distribution = None
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo de distribución CSV: {e}")
            df_distribution = None


    # Continuar con la lógica de distribución solo si ambos DataFrames se cargaron correctamente
    if df_distribution is not None:

        # --- 3. Ajustar la cantidad total a distribuir (múltiplo de Inner Pack o Cantidad en sistema) ---
        # Esta columna 'Adjusted Total Quantity' ahora se usa internamente para la lógica de redondeo inicial
        # y balanceo cuando el Inner Pack es válido, o como Cantidades en sistema si Inner Pack <= 0.
        df_distribution['Adjusted Total Quantity'] = 0.0

        for index, row in df_distribution.iterrows():
            quantity = row['Cantidades en sistema']
            inner_pack = row['Inner Pack']

            if pd.isna(quantity):
                df_distribution.loc[index, 'Adjusted Total Quantity'] = 0
            elif inner_pack <= 0:
                # Si Inner Pack es <= 0, usar la Cantidad en sistema original como cantidad total ajustada
                df_distribution.loc[index, 'Adjusted Total Quantity'] = int(round(quantity))
            else:
                try:
                    quantity_numeric = float(quantity)
                    inner_pack_numeric = int(inner_pack)
                    adjusted_quantity = (quantity_numeric // inner_pack_numeric) * inner_pack_numeric
                    df_distribution.loc[index, 'Adjusted Total Quantity'] = adjusted_quantity
                except (ValueError, TypeError) as e:
                    print(f"Advertencia: No se pudo procesar la fila {index} para ajuste total: {e}. Asignando 0.")
                    df_distribution.loc[index, 'Adjusted Total Quantity'] = 0

        df_distribution['Adjusted Total Quantity'] = df_distribution['Adjusted Total Quantity'].astype(int)


        # --- 4. Modificar la distribución inicial (considerando Inner Pack o distribucion unitaria) ---
        # Añadir columnas de tiendas al DataFrame de distribución si no existen
        for store_name in store_columns:
            if store_name not in df_distribution.columns:
                df_distribution[store_name] = 0.0

        for index, row in df_distribution.iterrows():
            adjusted_total_quantity = row['Adjusted Total Quantity'] # Usa Adjusted Total Quantity (que puede ser la original si Inner Pack <= 0)
            inner_pack = row['Inner Pack'] # Inner pack original

            # Determinar el inner pack a usar para los cálculos de redondeo en esta etapa
            # Si el inner pack original es <= 0, tratamos el inner pack para distribución como 1 (distribucion unitaria)
            inner_pack_for_distribution = int(inner_pack) if inner_pack > 0 else 1


            if adjusted_total_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0
                continue


            # Para cada store, calcular la cantidad inicial y redondearla (considerando inner_pack_for_distribution)
            for store_index, store in df_stores.iterrows():
                store_name = store['Nombre']
                participation = store['Participacion']

                initial_theoretical_quantity = adjusted_total_quantity * participation

                # Redondear la cantidad teórica al múltiplo más cercano del inner_pack_for_distribution
                rounded_quantity = round(initial_theoretical_quantity / inner_pack_for_distribution) * inner_pack_for_distribution

                # Asegurar que el resultado sea no negativo y entero
                adjusted_initial_quantity = max(0, int(rounded_quantity))

                # Asignar la cantidad calculada a la columna de la tienda para esta fila
                df_distribution.loc[index, store_name] = adjusted_initial_quantity


        # --- 5. Aplicar cantidad mínima (6) ---
        # Aplicar el mínimo in-place. El remanente se manejará en el balanceo final contra la cantidad original.
        for index, row in df_distribution.iterrows():
            for store_name in store_columns:
                initial_calculated_quantity = row[store_name]
                if initial_calculated_quantity < minimum_quantity:
                    df_distribution.loc[index, store_name] = 0


        # --- 6. Balanceo Final para mantener el total ORIGINAL y asegurar enteros ---
        # Este paso balancea la suma actual con la Cantidades en sistema ORIGINAL

        print("\nIniciando paso de balanceo final al Total Original...")

        for index, row in df_distribution.iterrows():
            original_quantity = row['Cantidades en sistema']

            if pd.isna(original_quantity) or original_quantity <= 0:
                for store_name in store_columns:
                    df_distribution.loc[index, store_name] = 0
                continue

            current_distributed_sum = row[store_columns].sum()
            balancing_difference = int(round(original_quantity - current_distributed_sum)) # Balancear contra el total ORIGINAL


            if balancing_difference != 0:
                stores_with_non_zero = [
                    store_name for store_name in store_columns
                    if df_distribution.loc[index, store_name] > 0
                ]

                # Orden de balanceo: restar de no prioritarias (si > 0), luego de prioritarias (si > min_qty). Sumar a prioritarias, luego a no prioritarias.
                if balancing_difference < 0:
                     balancing_order = [name for name in non_prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > 0] + \
                                       [name for name in prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > minimum_quantity]
                else: # balancing_difference > 0
                     balancing_order = [name for name in prioritized_store_names if name in stores_with_non_zero] + \
                                       [name for name in non_prioritized_store_names if name in stores_with_non_zero]


                balance_index = 0
                max_iterations = len(all_store_names) * abs(balancing_difference) + 20 # Salvaguarda

                while balancing_difference != 0 and balancing_order and max_iterations > 0:
                    store_name = balancing_order[balance_index % len(balancing_order)]

                    if balancing_difference > 0:
                        df_distribution.loc[index, store_name] += 1
                        balancing_difference -= 1
                        max_iterations -= 1
                    else: # balancing_difference < 0
                        can_subtract = False
                        if df_distribution.loc[index, store_name] > 0:
                            if store_name in prioritized_store_names:
                                if df_distribution.loc[index, store_name] > minimum_quantity:
                                    can_subtract = True
                            else: # Tienda no prioritaria
                                 can_subtract = True

                        if can_subtract:
                            df_distribution.loc[index, store_name] -= 1
                            balancing_difference += 1
                            max_iterations -= 1

                    balance_index += 1
                    # Recrear balancing_order si es necesario
                    if balancing_difference != 0 and balance_index % len(balancing_order) == 0:
                         stores_with_non_zero = [name for name in store_columns if df_distribution.loc[index, name] > 0]
                         if balancing_difference < 0:
                              balancing_order = [name for name in non_prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > 0] + \
                                                [name for name in prioritized_store_names if name in stores_with_non_zero and df_distribution.loc[index, name] > minimum_quantity]
                         else: # balancing_difference > 0
                              balancing_order = [name for name in prioritized_store_names if name in stores_with_non_zero] + \
                                                [name for name in non_prioritized_store_names if name in stores_with_non_zero]
                         if not balancing_order and balancing_difference != 0:
                             print(f"Advertencia: No se pudo balancear completamente la distribución para la fila {index}. Diferencia restante: {balancing_difference}")
                             break

            # Final check after balancing loop
            if balancing_difference != 0:
                 print(f"Advertencia: Balanceo final para la fila {index} al total original no exitoso. Diferencia restante: {balancing_difference}")


        # Asegurar que todas las cantidades de las tiendas sean enteros no negativos
        for store_name in store_columns:
            if df_distribution.loc[index, store_name] < 0:
                df_distribution.loc[index, store_name] = 0
            df_distribution.loc[index, store_name] = int(df_distribution.loc[index, store_name])

        # --- Agregar verificación de suma total contra Cantidades en sistema ORIGINAL ---
        # Esta verificación ahora se realiza contra Cantidades en sistema
        df_distribution['Final Distributed Sum'] = df_distribution[store_columns].sum(axis=1)

        print("\nVerificando sumas finales contra Cantidades en sistema original...")
        mismatched_rows_original = []
        for index, row in df_distribution.iterrows():
            original_qty = row['Cantidades en sistema']
            final_sum = row['Final Distributed Sum']
            if final_sum != original_qty:
                 mismatched_rows_original.append({'Index': index, 'Original Quantity': original_qty, 'Final Sum': final_sum, 'Difference': original_qty - final_sum})

        if mismatched_rows_original:
            print("¡Advertencia: Se encontraron diferencias entre 'Cantidades en sistema' original y la suma de cantidades distribuidas en las siguientes filas!")
            for mismatch in mismatched_rows_original:
                print(f"  Fila {mismatch['Index']}: Original Quantity = {mismatch['Original Quantity']}, Final Sum = {mismatch['Final Sum']}, Diferencia = {mismatch['Difference']}")
        else:
            print("Verificación de sumas finales completada: Todas las sumas de distribución coinciden con la 'Cantidades en sistema' original.")


        # --- 7. Generar y mostrar la tabla de resultados ---
        # Crear nombres de columna para la tabla final
        store_columns_with_format = [f"{row['Nombre']} ({row['Formato']})" for index, row in df_stores.iterrows()]
        # Incluir Adjusted Total Quantity y Inner Pack en la tabla final
        final_df_columns = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns_with_format + ['Suma Distribuida', 'Validacion (Cant. Sistema - Suma Dist.)']


        # Seleccionar las columnas relevantes del DataFrame de distribución final
        # Nos aseguramos de incluir 'Adjusted Total Quantity' y 'Inner Pack'
        columns_to_select = ['Cantidades en sistema', 'Adjusted Total Quantity', 'Inner Pack'] + store_columns
        if all(col in df_distribution.columns for col in columns_to_select):
            df_final_tabulated_distribution = df_distribution[columns_to_select].copy()

            # Renombrar las columnas de tiendas para incluir el formato
            rename_dict = {store_name: f"{store_name} ({df_stores.loc[df_stores['Nombre'] == store_name, 'Formato'].iloc[0]})" for store_name in store_columns}
            df_final_tabulated_distribution.rename(columns=rename_dict, inplace=True)

            # Calcular Suma Distribuida y Validacion para la tabla final
            df_final_tabulated_distribution['Suma Distribuida'] = df_final_tabulated_distribution[store_columns_with_format].sum(axis=1)
            df_final_tabulated_distribution['Validacion (Cant. Sistema - Suma Dist.)'] = df_final_tabulated_distribution['Cantidades en sistema'] - df_final_tabulated_distribution['Suma Distribuida']


            # Reorder columns to match final_df_columns if necessary
            df_final_tabulated_distribution = df_final_tabulated_distribution[final_df_columns]


            print("\nTabla de Distribución Final:")
            display(df_final_tabulated_distribution)

        else:
            print("Error: One or more required columns for the final table not found in df_distribution.")

        # Opcional: Guardar la tabla a un archivo CSV
        # output_file_path = '/content/distribucion_final_con_innerpack_validated.csv'
        # df_final_tabulated_distribution.to_csv(output_file_path, index=False)
        # print(f"\nTabla de distribución final guardada en: {output_file_path}")
