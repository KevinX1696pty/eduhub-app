# To run this code, you would need to install the required libraries.
# Create a requirements.txt file with the following content:
# streamlit
# pandas
# openpyxl

import streamlit as st
import pandas as pd
import numpy as np

def load_store_data(uploaded_file):
    """
    Loads store information from an uploaded file (Excel or CSV).

    Args:
        uploaded_file (UploadedFile): The file uploaded by the user.

    Returns:
        pd.DataFrame: DataFrame with store information, or None if an error occurs.
    """
    if uploaded_file is not None:
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.lower().endswith('.xlsx'):
                # Assuming the store data is in a sheet named 'stores' and starts from the first row (header)
                # Adjust sheet_name and header if your file is different
                df_stores = pd.read_excel(uploaded_file, sheet_name='stores', header=0)
            elif uploaded_file.name.lower().endswith('.csv'):
                # Assuming semicolon delimiter for CSV and header in the first row
                 df_stores = pd.read_csv(uploaded_file, sep=';', header=0)
            else:
                st.error("Unsupported file format for store data. Please upload an .xlsx or .csv file.")
                return None

            # Ensure required columns exist
            required_columns = ['Nombre', 'Formato', 'Participacion']
            if not all(col in df_stores.columns for col in required_columns):
                st.error(f"Error: The store file must contain the columns: {required_columns}")
                return None
            else:
                 # Ensure 'Participacion' is numeric
                 df_stores['Participacion'] = pd.to_numeric(df_stores['Participacion'], errors='coerce').fillna(0)
                 st.success("Store information loaded successfully.")
                 return df_stores

        except Exception as e:
            st.error(f"An error occurred while loading the store information file: {e}")
            return None
    return None


def load_quantities_data(uploaded_file, quantity_column='cantidad', skiprows=0):
    """
    Loads quantity data from an uploaded file (Excel or CSV).

    Args:
        uploaded_file (UploadedFile): The file uploaded by the user.
        quantity_column (str): The name of the column containing quantities.
        skiprows (int): Number of rows to skip at the beginning of the file.

    Returns:
        pd.DataFrame: DataFrame with quantity data, or None if an error occurs.
    """
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith('.xlsx'):
                 # Adjust sheet_name and header if your file is different
                 df_data = pd.read_excel(uploaded_file, sheet_name='distribucion bultos abiertos', skiprows=skiprows)
            elif uploaded_file.name.lower().endswith('.csv'):
                 df_data = pd.read_csv(uploaded_file, skiprows=skiprows, sep=';') # Assuming semicolon delimiter for CSV
            else:
                 st.error("Unsupported file format for quantity data. Please upload an .xlsx or .csv file.")
                 return None

            # Ensure the quantity column exists
            if quantity_column not in df_data.columns:
                 st.error(f"Error: Quantity column '{quantity_column}' not found in the data file.")
                 return None

            # Ensure the quantity column is numeric
            df_data[quantity_column] = pd.to_numeric(df_data[quantity_column], errors='coerce')
            # Drop rows where the quantity is NaN after coercion
            df_data.dropna(subset=[quantity_column], inplace=True)

            st.success(f"Quantity data loaded successfully. Found {len(df_data)} quantities.")

            # Assuming 'Referencia' is the first column after skipping rows, adjust if needed
            # If 'Referencia' is not consistently in the first column, you might need to
            # provide its column name as a parameter as well.
            if 'Referencia' in df_data.columns:
                 return df_data[['Referencia', quantity_column]]
            else:
                 st.warning("'Referencia' column not found. Proceeding with only quantity data.")
                 return df_data[[quantity_column]]


        except Exception as e:
            st.error(f"An error occurred while loading the quantity data file: {e}")
            return None
    return None


def distribute_quantity(total_quantity, df_stores, minimum_quantity=6):
    """
    Distributes a total quantity among stores based on format, minimums, and prioritization.

    Args:
        total_quantity (int): The total quantity to distribute.
        df_stores (pd.DataFrame): DataFrame with store information ('Nombre', 'Formato', 'Participacion').
        minimum_quantity (int): The minimum quantity allowed per store.

    Returns:
        dict: A dictionary with store names as keys and distributed quantities as values.
    """
    adjusted_quantities = {}

    # Calculate initial quantity per store based on original participation
    initial_quantity_by_store = {}
    for index, store in df_stores.iterrows():
        store_name = store['Nombre']
        participation = store['Participacion']
        initial_quantity_by_store[store_name] = float(total_quantity) * participation


    # Apply minimum quantity rule and round to integers initially
    initial_distributed_sum = 0
    stores_that_met_minimum = [] # Stores that initially received >= minimum after rounding

    for index, store in df_stores.iterrows():
        store_name = store['Nombre']
        store_format = store['Formato']

        # Get the initial calculated quantity for this store
        initial_quantity = initial_quantity_by_store.get(store_name, 0.0)

        # Round the initial quantity to the nearest integer
        rounded_quantity = int(round(initial_quantity))

        # Apply the minimum quantity rule
        if rounded_quantity < minimum_quantity:
            adjusted_quantities[store_name] = 0
        else:
            adjusted_quantities[store_name] = rounded_quantity
            initial_distributed_sum += rounded_quantity
            stores_that_met_minimum.append(store_name)


    # Calculate remaining integer quantity to distribute to match the original total
    remaining_integer_difference = int(round(total_quantity)) - initial_distributed_sum

    # Distribute the remaining integer difference in a round-robin fashion
    # among stores that met the minimum, prioritizing Grande and Mediano.
    prioritized_store_names = df_stores[df_stores['Formato'].isin(['Grande', 'Mediano'])]['Nombre'].tolist()
    non_prioritized_store_names = df_stores[df_stores['Formato'] == 'Pequeño']['Nombre'].tolist()

    distribution_order_balancing = [name for name in prioritized_store_names if name in stores_that_met_minimum] + \
                                   [name for name in non_prioritized_store_names if name in stores_that_met_minimum]

    dist_index = 0
    while remaining_integer_difference != 0 and distribution_order_balancing:
        store_name = distribution_order_balancing[dist_index % len(distribution_order_balancing)]

        if remaining_integer_difference > 0:
            adjusted_quantities[store_name] += 1
            remaining_integer_difference -= 1
        else: # remaining_integer_difference < 0
            # Only subtract if the current quantity for the store is greater than the minimum (6)
            # to avoid going below the minimum after balancing
            if adjusted_quantities[store_name] > minimum_quantity:
                adjusted_quantities[store_name] -= 1
                remaining_integer_difference += 1
            # If quantity is already at minimum, skip this store for subtraction in this round


        dist_index += 1

    # Ensure all adjusted quantities are non-negative integers
    for store_name in adjusted_quantities.keys():
        if adjusted_quantities[store_name] < 0:
            adjusted_quantities[store_name] = 0
        # Quantities should already be integers from rounding and adding/subtracting 1


    return adjusted_quantities


# --- Streamlit App Structure ---

st.title("Quantity Distribution App")

st.write("Upload your store information and quantities data files to get the distribution.")

# File uploaders
store_file = st.file_uploader("Upload Store Information File (Excel or CSV)", type=['xlsx', 'csv'])
quantities_file = st.file_uploader("Upload Quantities Data File (Excel or CSV)", type=['xlsx', 'csv'])

# Optional: Minimum quantity input
minimum_quantity_input = st.number_input("Minimum Quantity per Store", min_value=0, value=6, step=1)

# Optional: Quantities file parameters
st.sidebar.header("Quantities File Options")
quantity_column_name = st.sidebar.text_input("Quantity Column Name", value='cantidad')
quantities_skip_rows = st.sidebar.number_input("Rows to skip in Quantities File", min_value=0, value=0, step=1)


if store_file is not None and quantities_file is not None:
    df_stores_data = load_store_data(store_file)
    df_quantities_data = load_quantities_data(quantities_file, quantity_column=quantity_column_name, skiprows=quantities_skip_rows)

    if df_stores_data is not None and df_quantities_data is not None:
        st.subheader("Distribution Results")

        # Prepare DataFrame to store the final tabulated distribution
        tabulated_data = []
        store_columns_with_format = [f"{row['Nombre']} ({row['Formato']})" for index, row in df_stores_data.iterrows()]
        final_df_columns = ['Original Quantity'] + store_columns_with_format

        # Iterate through each quantity and apply the distribution logic
        for index, row in df_quantities_data.iterrows():
            original_quantity = row[quantity_column_name]
            adjusted_distribution = distribute_quantity(original_quantity, df_stores_data, minimum_quantity=minimum_quantity_input)

            row_data = [original_quantity]
            for store_name in df_stores_data['Nombre']:
                row_data.append(adjusted_distribution.get(store_name, 0))
            tabulated_data.append(row_data)

        df_final_tabulated = pd.DataFrame(tabulated_data, columns=final_df_columns)

        st.dataframe(df_final_tabulated)

        # Optional: Download button for the results
        csv_output = df_final_tabulated.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Distribution Table as CSV",
            data=csv_output,
            file_name='final_distribution_table.csv',
            mime='text/csv',
        )

    else:
        st.warning("Please upload both valid store and quantities data files.")
