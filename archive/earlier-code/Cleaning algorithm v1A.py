import pandas as pd
import os
import sqlite3
import numpy as np
import plotly.express as px

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

def clean_data(df):
    #get the price values from the dataframe
    prices = [df["Price"].values()]
    #work out stats for cleaning
    standard_deviation = np.std(prices)
    mean = np.std(prices)
    #iterate through data checking for anomalies and write over anomalies with average of the values either side of the point
    for index in prices:
        if prices[index] < (mean - 2*standard_deviation) or prices[index] > (mean + 2*standard_deviation):
            prices[index] = (prices[index + 1] + prices[index -1])/2
    #convert back into a dataframe
    filtered_prices_dataframe = pd.DataFrame(prices)
    df["Price"] = filtered_prices_dataframe#write over the prices column in the original dataframe with the cleaned data

    return df    

if __name__ == "__main__":
    #set the base path into the directory that holds both the data folder and the coding folder
    base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA\Code'
    
    #set different paths up ready to pass into the functions
    directory_path = os.path.join(base_path, 'Price Files')
    db_path = os.path.join(base_path, 'Output Files', 'Market_prices.db')
    table_name = "Market_prices"

    #read data from the directory into the dataframe
    df = read_directory_to_df(directory_path)
    
    #checks if there is data in the dataframe or if there was no data to be read
    if df is not None:
        print("Directory data loaded:", df.head())

        fig = px.line(df, x="Date_time", y="Price", color="Item_name", title="Historical Market Prices")
    
        cleaned_df = clean_data(df)
        print(cleaned_df)
        if cleaned_df is not None:
            fig = px.line(cleaned_df, x="Date_time", y="Price", color="Item_name", title="Historical Market Prices")

        
        #write the data from the dataframe just created into the database
        if write_df_to_db(df, db_path, table_name):
            print(f"DataFrame written to {db_path}, table {table_name}")

        #reads the data just put into the database back into another dataframe and then prints it so that I can check the data has not been changed
        db_to_df_read = read_db_to_df(db_path, table_name)
        if db_to_df_read is not None:
            print("Database data loaded:", db_to_df_read.head())