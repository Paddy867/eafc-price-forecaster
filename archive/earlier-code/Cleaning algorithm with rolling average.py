import pandas as pd
import os
import sqlite3
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

#base path is the path on my computer to the directory in which there are folders that hold the database, data files, and this code

def read_directory_to_df(directory_path):
    try:
        all_data = []
        #gives a list of the names of files in a directory
        files = os.listdir(directory_path)
        #stores all of the files in the given directory that is a csv file
        csv_files = []
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(file)
        
        #if there are no csv files in the directory, it tells the user
        if not csv_files:
            print(f"No csv files found in {directory_path}")
            return None
        
        #iterates through each of the files in csv_files array 
        for file_name in csv_files:
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'r') as file:
                lines = file.readlines()[1:]  #skips the header of the file
                records = []
                for line in lines:
                    if line.strip():
                        name, date, delay, price, time = line.strip().split(',') #takes the values in each record and appends them to an array
                        records.append([name, f"{date} {time}", int(price)])
                df = pd.DataFrame(records, columns=['Item_name', 'Date_time', 'Price']) #the array is turneds into a dataframe
                df['Date_time'] = pd.to_datetime(df['Date_time']) #converts the Date_time into a datetime type
            all_data.append(df)
        
        combined_data = pd.concat(all_data, ignore_index=True)
        return combined_data
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error reading directory: {e}")
        return None


def write_df_to_db(df, db_path, table_name, if_exists="replace"):
    try:
        conn = sqlite3.connect(db_path) # connects to the database from the given path
        df.to_sql(table_name, conn, if_exists=if_exists, index=False) #writes the dataframe into the sql table
        conn.close()
        return True
    
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error writing to database: {e}")
        return False
    
def read_db_to_df(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn) # selects out of the database the items chosen in the query defined
        conn.close()
        return df
    
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error reading database: {e}")
        return None

def calculate_stats(prices, index, window_size=25):
    #defines the start and end of the window
    if index - window_size < 0:
        start = 0
    else:
        start = index - window_size

    if index + window_size + 1 > len(prices):
        end = len(prices)
    else:
        end = index + window_size + 1
    
    #get the local window exlcuding the current point
    local_prices = prices[start:index] + prices[index + 1:end]  # Exclude the current point
    
    #calculates mean of the local window
    try:
        local_mean = np.mean(local_prices)

        return local_mean
    except Exception as e:
        print(f"No data in rolling window: {e}")
        return None

def clean_group(prices):
    cleaned_prices = prices.copy()  # Create a copy to avoid modifying the original
    
    for index in range(len(cleaned_prices)):
        # Calculate local stats for the window around this index, excluding the current point
        local_mean = calculate_stats(prices, index, 5)
        
        # Check if the current price is an outlier (beyond 2 standard deviations from local mean)
        prices[index] = local_mean
    
    return prices

def clean_all_data(df):
    cleaned_data = []
    for name, group in df.groupby("Item_name"):
        group_prices = group["Price"].tolist()
        cleaned_prices = clean_group(group_prices)  # Pass None since we don't need group_stats anymore
        group["Price"] = cleaned_prices
        cleaned_data.append(group)
    
    cleaned_dataframe = pd.concat(cleaned_data, ignore_index=True)
    return cleaned_dataframe

if __name__ == "__main__":
    #set the base path into the directory that holds both the data folder and the coding folder
    base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA'
    
    #set different paths up ready to pass into the functions
    directory_path = os.path.join(base_path, 'All price files')
    db_path = os.path.join(base_path, 'Code', 'Output Files', 'Market_prices_cleaned_all.db')
    table_name = "Market_prices"

    #read data from the directory into the dataframe
    df = read_directory_to_df(directory_path)
    #checks if there is data in the dataframe or if there was no data to be read
    start_date = '2024-01-01'
    end_date = '2024-04-30'

    df = df[(df['Date_time'] >= start_date) & (df['Date_time'] <= end_date)]
    if df is not None:
        print("Directory data loaded:", df.head())
        plt.figure(figsize=(10, 6))
        
        # Plot original data
        for name, group in df.groupby('Item_name'):
            if name == "Basic":
                plt.plot(group['Date_time'], group['Price'], label='Original ' + name, color='blue')
        
        # Plot cleaned data
        cleaned_df = clean_all_data(df.copy())
        print(cleaned_df)
        if cleaned_df is not None:
            for name, group in cleaned_df.groupby('Item_name'):
                if name == "Basic":
                    plt.plot(group['Date_time'], group['Price'], label='Cleaned ' + name, color='orange')
        
        plt.title("Historical Market Prices")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        #write the data from the dataframe just created into the database
        if write_df_to_db(cleaned_df, db_path, "Market_prices"):
            print(f"DataFrame written to {db_path}, table Market_prices")
        if write_df_to_db(cleaned_df, db_path, "Cleaned_market_prices"):
            print(f"DataFrame written to {db_path}, table Cleaned_market_prices")

        #reads the data just put into the database back into another dataframe and then prints it so that I can check the data has not been changed
        db_to_df_read = read_db_to_df(db_path, "Cleaned_market_prices")
        if db_to_df_read is not None:
            print("Database data loaded:", db_to_df_read.head())