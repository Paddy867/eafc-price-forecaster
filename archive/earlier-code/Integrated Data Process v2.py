# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 11:23:50 2025

@author: Trading Account
"""

import pandas as pd
import os
import sqlite3

# 1. Read Directory into DataFrame
def read_directory_to_df(directory_path, file_extension=".csv"):
    """
    Reads CSV files from a directory into a DataFrame, adding datetime from filenames.
    
    Parameters:
        directory_path (str): Path to the directory.
        file_extension (str): File extension to filter (default '.csv').
    
    Returns:
        pd.DataFrame: Combined DataFrame with 'Datetime' or 'Date_time' column.
    """
    try:
        all_data = []
        files = os.listdir(directory_path)
        csv_files = [file for file in files if file.endswith(file_extension)]
        
        if not csv_files:
            print(f"No {file_extension} files found in {directory_path}")
            return None
        
        for file_name in csv_files:
            file_path = os.path.join(directory_path, file_name)
            # Check file format from pastes
            if '--' in file_name:  # From Paste 1
                df = pd.read_csv(file_path)
                file_date_str, file_time_str = file_name.split('--')
                file_datetime = pd.to_datetime(f"{file_date_str} {file_time_str.split('.')[0]}")
                df['Datetime'] = file_datetime
            else:  # From Paste 3
                with open(file_path, 'r') as f:
                    lines = f.readlines()[1:]  # Skip header
                    records = []
                    for line in lines:
                        if line.strip():
                            name, date, delay, price, time = line.strip().split(',')
                            records.append([name, f"{date} {time}", int(price)])
                    df = pd.DataFrame(records, columns=['Item_name', 'Date_time', 'Price'])
                    df['Date_time'] = pd.to_datetime(df['Date_time'])
            all_data.append(df)
        
        combined_data = pd.concat(all_data, ignore_index=True)
        return combined_data
    except Exception as e:
        print(f"Error reading directory: {e}")
        return None

# 2. Write DataFrame to Database
def write_df_to_db(df, db_path, table_name, if_exists="replace"):
    """
    Writes a DataFrame to a SQLite database table.
    
    Parameters:
        df (pd.DataFrame): DataFrame to write.
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to write to.
        if_exists (str): Action if table exists ('fail', 'replace', 'append'). Default is 'replace'.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        conn = sqlite3.connect(db_path)
        # Normalize column names to match Paste 3's schema if needed
        if 'Datetime' in df.columns and 'Date_time' not in df.columns:
            df = df.rename(columns={'Datetime': 'Date_time'})
        if 'Item_name' not in df.columns and 'chem' in df.columns:
            df = df.rename(columns={'chem': 'Item_name'})
        if 'price' in df.columns and 'Price' not in df.columns:
            df = df.rename(columns={'price': 'Price'})
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.close()
        return True
    except Exception as e:
        print(f"Error writing to database: {e}")
        return False
    
# 3. Read Database into DataFrame
def read_db_to_df(db_path, table_name, start_date=None, end_date=None):
    """
    Reads a SQLite database table into a pandas DataFrame, optionally filtering by date range.
    
    Parameters:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to read.
        start_date (str, optional): Start of date range (e.g., '2023-01-01 12:00:00').
        end_date (str, optional): End of date range (e.g., '2025-01-01 12:00:00').
    
    Returns:
        pd.DataFrame: DataFrame containing the table data.
    """
    try:
        conn = sqlite3.connect(db_path)
        if start_date and end_date:
            query = f"SELECT * FROM {table_name} WHERE Date_time BETWEEN ? AND ?"
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading database: {e}")
        return None


# Example Usage Integrating All Pastes
if __name__ == "__main__":
    # Single base path to adjust
    base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA\Code'
    
    # Derived paths using base_path
    directory_path = os.path.join(base_path, 'Price Files')
    db_path = os.path.join(base_path, 'Output Files', 'Market_prices.db')
    table_name = "Market_prices"

    # Read from directory
    df = read_directory_to_df(directory_path)
    
    if df is not None:
        print("Directory data loaded:", df.head())

        # Write to database
        if write_df_to_db(df, db_path, table_name):
            print(f"DataFrame written to {db_path}, table {table_name}")

        # Read from database
        # example date time '2022-01-01 12:00:00'
        df_db = read_db_to_df(db_path, table_name)
        if df_db is not None:
            print("Database data loaded:", df_db.head())