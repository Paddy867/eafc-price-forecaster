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

def calculate_stats(group):
    prices = group["Price"].tolist()#convert the prices to a list
    group_stats = {"Mean": np.mean(prices), "Standard deviation": np.std(prices), "Prices": prices}#create a dictionary that contains the stats for the group as well as the prices
    return group_stats

def clean_group(group_stats, prices):
    for index in range(len(prices)):
        #check if the data point is an anomaly
        if (prices[index] < (group_stats['Mean'] - 2 * group_stats['Standard deviation']) or prices[index] > (group_stats['Mean'] + 2 * group_stats['Standard deviation'])):
            #if it is replace the data with the average of data either side, or two points on one side (if the data point is the last or first point) of the data point
            if index == 0:
                prices[index] = (prices[index+1] + prices[index+2])/2
            elif index == len(prices)-1:
                prices[index] = (prices[index-1] + prices[index-2])/2
            else:
                 prices[index] = (prices[index + 1] + prices[index -1])/2
            
    return prices

def clean_all_data(df):
    cleaned_data = []
    for name, group in df.groupby("Item_name"):#sort the dataframe by groups based on item name
        group_stats = calculate_stats(group)#calculate the group stats
        cleaned_prices = clean_group(group_stats, group_stats["Prices"])#clean the group
        group["Price"] = cleaned_prices#write the cleaned prices to the price column of the group
        cleaned_data.append(group)#append the cleaned data list with the group
        

    cleaned_dataframe = pd.DataFrame(cleaned_data[0])#convert the cleaned data into a dataframe
    return cleaned_dataframe

if __name__ == "__main__":
    #set the base path into the directory that holds both the data folder and the coding folder
    base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA'
    
    #set different paths up ready to pass into the functions
    directory_path = os.path.join(base_path, 'All price files')
    db_path = os.path.join(base_path, 'NEA', 'Code', 'Output Files', 'Market_prices_cleaned_all.db')
    table_name = "Market_prices"

    #read data from the directory into the dataframe
    df = read_directory_to_df(directory_path)
    
    #checks if there is data in the dataframe or if there was no data to be read
    if df is not None:
        print("Directory data loaded:", df.head())
        plt.figure(figsize=(10, 6))
        for name, group in df.groupby('Item_name'):
            print(group)
            if name == "Anchor":
                plt.plot(group['Date_time'], group['Price'], label=name)
        plt.title("Original Historical Market Prices")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
        cleaned_df = clean_all_data(df.copy())
        print(cleaned_df)
        if cleaned_df is not None:
            plt.figure(figsize=(10, 6))
            for name, group in cleaned_df.groupby('Item_name'):
                plt.plot(group['Date_time'], group['Price'], label=name)
            plt.title("Cleaned Historical Market Prices")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        #write the data from the dataframe just created into the database
        if write_df_to_db(cleaned_df, db_path, table_name):
            print(f"DataFrame written to {db_path}, table {table_name}")

        #reads the data just put into the database back into another dataframe and then prints it so that I can check the data has not been changed
        db_to_df_read = read_db_to_df(db_path, table_name)
        if db_to_df_read is not None:
            print("Database data loaded:", db_to_df_read.head())

            