import pandas as pd
import os
import sqlite3
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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
        combined_data['Date_time'] = pd.to_datetime(combined_data['Date_time'])
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
        
        df['Date_time'] = pd.to_datetime(df['Date_time'])
        
        return df
    
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error reading database: {e}")
        return None

def calculate_stats(prices, index, window_size):
    """
    Calculate mean and standard deviation for a window of `window_size` points on either side of the given index,
    excluding the point at the current index.
    """
    # Define the start and end of the window, excluding the current point
    if index - window_size < 0:
        start = 0
    else:
        start = index - window_size

    if index + window_size + 1 > len(prices):
        end = len(prices)
    else:
        end = index + window_size + 1
    
    # Extract the local window, but exclude the current point (index)
    local_prices = prices[start:index] + prices[index + 1:end]  # Exclude the current point
    
    # If the window is empty (e.g., at edges), use all available points except current
    if not local_prices:
        # Fallback: use all points except the current one
        local_prices = prices[:index] + prices[index + 1:]
    
    # Calculate mean and standard deviation on the local window (excluding current point)
    if local_prices:  # Ensure we have data
        local_mean = np.mean(local_prices)
    else:
        # If no other points are available, use the global mean/std (or handle differently)
        local_mean = np.mean(prices)
    
    return local_mean

def clean_group(group_stats, prices):
    cleaned_prices = prices.copy()  # Create a copy to avoid modifying the original
    
    for index in range(len(prices)):
        # Calculate local stats for the window around this index, excluding the current point
        local_mean = calculate_stats(prices, index, 5)
        
        # Check if the current price is an outlier (beyond 2 standard deviations from local mean)
        prices[index] = local_mean
    
    return prices

def clean_all_data(df):
    cleaned_data = []
    for name, group in df.groupby("Item_name"):
        group_prices = group["Price"].tolist()
        cleaned_prices = clean_group(None, group_prices)  # Pass None since we don't need group_stats anymore
        group["Price"] = cleaned_prices
        cleaned_data.append(group)
    
    cleaned_dataframe = pd.concat(cleaned_data, ignore_index=True)
    return cleaned_dataframe

def forecast_prices(smoothed_df, weeks_to_forecast):
    #smoothed_df['Date_time'] = pd.to_datetime(smoothed_df['Date_time'])
    # Convert Datetime to numeric (days since start) for regression
    time_numeric = (smoothed_df['Date_time'] - smoothed_df['Date_time'].min()).dt.total_seconds() / (24 * 3600)
    X = time_numeric.values.reshape(-1, 1)  # Reshape for sklearn
    y = smoothed_df['Price'].values
    
    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_date = smoothed_df['Date_time'].max()
    future_dates = pd.date_range(start=last_date, periods=weeks_to_forecast * 7, freq='D')[1:]  # Daily steps, skip last_date
    future_time_numeric = (future_dates - smoothed_df['Date_time'].min()).total_seconds() / (24 * 3600)
    X_future = np.array(future_time_numeric).reshape(-1, 1)  # Convert to NumPy array and reshape
    
    # Predict future prices
    future_prices = model.predict(X_future)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'Date_time': future_dates,
        'Price': future_prices
    })
    return forecast_df

if __name__ == "__main__":
    #set the base path into the directory that holds both the data folder and the coding folder
    base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA'
    
    #set different paths up ready to pass into the functions
    directory_path = os.path.join(base_path, 'All price files')
    db_path = os.path.join(base_path, 'Code', 'Output Files', 'Market_prices_cleaned_all.db')
    table_name = "Market_prices"

    #select the read from directory to update the database, select read database for a quick run
    #df = read_directory_to_df(directory_path)
    df = read_db_to_df(db_path, table_name)
        
    #limit the data in the dataframe so that it only shows so much data and for only one item
    start_date = '2024-01-01'
    end_date = '2024-04-30'
    selected_item = 'Basic'
    filtered_original_df = df[(df['Date_time'] >= start_date) & (df['Date_time'] <= end_date)]
    filtered_original_df = filtered_original_df[df['Item_name'] == selected_item]
    
    #checks if the dataframe is empty
    if filtered_original_df is not None:
        print("Directory data loaded:", filtered_original_df.head())
        plt.figure(figsize=(10, 6))
        #plot the original data in blue
        plt.plot(filtered_original_df['Date_time'], filtered_original_df['Price'], label='Original', color='blue')
        
        #clean the dataframe and then use this cleaned dataframe to forecast
        cleaned_df = clean_all_data(filtered_original_df.copy())
        forecast_df = forecast_prices(cleaned_df, 2)
        
        #checks if the cleaned and forecast is empty
        if cleaned_df is not None:
            #plot the cleaned data
            plt.plot(cleaned_df['Date_time'], cleaned_df['Price'], label='Cleaned', color='orange')
        if forecast_df is not None:
            #plot the forecast data
            plt.plot(forecast_df['Date_time'], forecast_df['Price'], label='Forecast', color='red')
        
        #create the actual plot and display it
        plt.title("Historical Market Prices")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        #write the data from the dataframe just created into the database
        if write_df_to_db(df, db_path, "Market_prices"):
            print(f"DataFrame written to {db_path}, table Market_prices")
        if write_df_to_db(cleaned_df, db_path, "Cleaned_market_prices"):
            print(f"DataFrame written to {db_path}, table Cleaned_market_prices")

        #reads the data just put into the database back into another dataframe and then prints it so that I can check the data has not been changed
        db_to_df_read = read_db_to_df(db_path, "Cleaned_market_prices")
        if db_to_df_read is not None:
            print("Database data loaded:", db_to_df_read.head())
            