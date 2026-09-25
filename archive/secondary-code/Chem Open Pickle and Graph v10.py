# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:46:18 2023

@author: derek
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression

#
cutdate = pd.to_datetime("2025-02-01")
enddate = pd.to_datetime("2025-10-14")

# Path to the pickle file
#pickle_file_path = r'C:\Users\derek\OneDrive\Tech\DataExchange\Code\TestData\all_data24.pkl'
pickle_file_path = r'C:\Users\derek\OneDrive\Tech\DataExchange\Code\TestData\TempPickle.pkl'
#pickle_file_path = r'C:\Users\Trading Account\OneDrive\Tech\DataExchange\Code\TestData\all_data24.pkl'

#thingToProcess = 'Shadow'
#thingToProcess = 'Hunter'
#thingToProcess = 'Engine'
thingToProcess = 'Basic'
#thingToProcess = 'Anchor'

weeks_to_forecast = 2  # Number of weeks to forecast

# Condensed thingToProcess settings using a dictionary
chem_settings = {
    'Shadow': {'color': 'darkslategray'},
    'Hunter': {'color': 'darkred'},
    'Engine': {'color': 'darkolivegreen'},
    'Anchor': {'color': 'darkblue'},
    'Basic': {'color': 'darkolivegreen'}
}

# Function to smooth data using a rolling average




def forecast_prices(smoothed_df, weeks_to_forecast):
    # Convert Datetime to numeric (days since start) for regression
    time_numeric = (smoothed_df['Datetime'] - smoothed_df['Datetime'].min()).dt.total_seconds() / (24 * 3600)
    X = time_numeric.values.reshape(-1, 1)  # Reshape for sklearn
    y = smoothed_df['price'].values
    
    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_date = smoothed_df['Datetime'].max()
    future_dates = pd.date_range(start=last_date, periods=weeks_to_forecast * 7, freq='D')[1:]  # Daily steps, skip last_date
    future_time_numeric = (future_dates - smoothed_df['Datetime'].min()).total_seconds() / (24 * 3600)
    X_future = np.array(future_time_numeric).reshape(-1, 1)  # Convert to NumPy array and reshape
    
    # Predict future prices
    future_prices = model.predict(X_future)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'Datetime': future_dates,
        'price': future_prices
    })
    return forecast_df

def forecast_prices2(smoothed_df, weeks_to_forecast):
    # Add day of week as a feature
    smoothed_df['DayOfWeek'] = smoothed_df['Datetime'].dt.day_name()
    smoothed_df['DaysSinceStart'] = (smoothed_df['Datetime'] - smoothed_df['Datetime'].min()).dt.total_seconds() / (24 * 3600)
    
    # Create dummy variables for day of week (categorical)
    day_dummies = pd.get_dummies(smoothed_df['DayOfWeek'], prefix='Day')
    
    # Combine features: days since start (linear trend) + day of week dummies (weekly pattern)
    X = np.column_stack((smoothed_df['DaysSinceStart'].values, day_dummies.values))
    y = smoothed_df['price'].values
    
    # Fit multiple linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates
    last_date = smoothed_df['Datetime'].max()
    future_dates = pd.date_range(start=last_date, periods=weeks_to_forecast * 7, freq='D')[1:]  # Daily steps, skip last_date
    future_days_since_start = (future_dates - smoothed_df['Datetime'].min()).total_seconds() / (24 * 3600)
    
    # Create day of week dummies for future dates
    future_df = pd.DataFrame({'Datetime': future_dates})
    future_df['DayOfWeek'] = future_df['Datetime'].dt.day_name()
    future_day_dummies = pd.get_dummies(future_df['DayOfWeek'], prefix='Day')
    
    # Ensure future_day_dummies has the same columns as day_dummies
    for col in day_dummies.columns:
        if col not in future_day_dummies.columns:
            future_day_dummies[col] = 0
    future_day_dummies = future_day_dummies[day_dummies.columns]  # Align column order
    
    # Combine features for prediction
    X_future = np.column_stack((future_days_since_start, future_day_dummies.values))
    
    # Predict future prices
    future_prices = model.predict(X_future)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'Datetime': future_dates,
        'price': future_prices
    })
    return forecast_df

def forecast_prices3(smoothed_df, weeks_to_forecast):
    # Add features for regression
    smoothed_df['DaysSinceStart'] = (smoothed_df['Datetime'] - smoothed_df['Datetime'].min()).dt.total_seconds() / (24 * 3600)
    smoothed_df['DayOfWeek'] = smoothed_df['Datetime'].dt.day_name()
    smoothed_df['Hour'] = smoothed_df['Datetime'].dt.hour
    
    # Create dummy variables for day of week and hour
    day_dummies = pd.get_dummies(smoothed_df['DayOfWeek'], prefix='Day')
    hour_dummies = pd.get_dummies(smoothed_df['Hour'], prefix='Hour', dtype=int)
    
    # Combine features: linear trend + day of week + hour of day
    X = np.column_stack((smoothed_df['DaysSinceStart'].values, day_dummies.values, hour_dummies.values))
    y = smoothed_df['price'].values
    
    # Fit multiple linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate future dates (hourly resolution)
    last_date = smoothed_df['Datetime'].max()
    future_dates = pd.date_range(start=last_date, periods=weeks_to_forecast * 7 * 24, freq='H')[1:]  # Hourly steps, skip last_date
    future_days_since_start = (future_dates - smoothed_df['Datetime'].min()).total_seconds() / (24 * 3600)
    
    # Create day of week and hour features for future dates
    future_df = pd.DataFrame({'Datetime': future_dates})
    future_df['DayOfWeek'] = future_df['Datetime'].dt.day_name()
    future_df['Hour'] = future_df['Datetime'].dt.hour
    
    # Create dummy variables for future dates
    future_day_dummies = pd.get_dummies(future_df['DayOfWeek'], prefix='Day')
    future_hour_dummies = pd.get_dummies(future_df['Hour'], prefix='Hour', dtype=int)
    
    # Ensure dummy variables match historical data
    for col in day_dummies.columns:
        if col not in future_day_dummies.columns:
            future_day_dummies[col] = 0
    future_day_dummies = future_day_dummies[day_dummies.columns]  # Align column order
    
    for col in hour_dummies.columns:
        if col not in future_hour_dummies.columns:
            future_hour_dummies[col] = 0
    future_hour_dummies = future_hour_dummies[hour_dummies.columns]  # Align column order
    
    # Combine features for prediction
    X_future = np.column_stack((future_days_since_start, future_day_dummies.values, future_hour_dummies.values))
    
    # Predict future prices
    future_prices = model.predict(X_future)
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        'Datetime': future_dates,
        'price': future_prices
    })
    return forecast_df

titleLabel = f"{thingToProcess} Prices Since: {cutdate.strftime('%d/%m/%Y')}"
chemColour = chem_settings[thingToProcess]['color']

# Rest of your code remains the same...
# Load the DataFrame from the pickle file
pickle_in = open(pickle_file_path, 'rb')
all_data = pickle.load(pickle_in)
pickle_in.close()

# Filter data for the selected chem (no price filtering)
single_data = all_data[all_data['chem'] == thingToProcess]
Input_df = single_data.sort_values(['Datetime'], ascending=[True])

# Filter by date range
delete_row = Input_df[Input_df['Datetime'] < cutdate].index
Input_df = Input_df.drop(delete_row)

delete_row2 = Input_df[Input_df['Datetime'] > enddate].index
Input_df = Input_df.drop(delete_row2)

Input_df['Weekday'] = Input_df['Datetime'].dt.day_name()
non_sat_dates = Input_df[Input_df['Weekday'] != 'Saturday'].index
AllDates = Input_df['Datetime']
SatDates = AllDates.drop(non_sat_dates)

# Create smoothed and forecast DataFrames
smoothed_df = smooth_data(Input_df, window_size=20)
forecast_df = forecast_prices3(smoothed_df, weeks_to_forecast)

# Plot
plt.figure(figsize=(20, 6))
# Original data
plt.plot(Input_df['Datetime'], Input_df['price'], linestyle='-', color=chemColour, alpha=0.5, label='Raw Data')
# Smoothed data
plt.plot(smoothed_df['Datetime'], smoothed_df['price'], linestyle='-', color='black', label='Smoothed (window=20)')
# Forecast data
plt.plot(forecast_df['Datetime'], forecast_df['price'], linestyle='--', color='red', label=f'Forecast ({weeks_to_forecast} weeks)')

plt.xlabel('Datetime')
plt.ylabel('Price')
plt.title(titleLabel)

# Combine all dates for x-axis ticks
all_dates = pd.concat([Input_df['Datetime'], forecast_df['Datetime']]).sort_values()
plt.xticks(all_dates[::100], all_dates.dt.strftime('%Y-%m-%d')[::100], rotation=45)

plt.legend()
plt.tight_layout()

# Mark Saturdays across both historical and forecast data
combined_df = pd.concat([Input_df, forecast_df]).reset_index(drop=True)
combined_df['Weekday'] = combined_df['Datetime'].dt.day_name()
for index, row in combined_df.iterrows():
    if row['Weekday'] == 'Saturday' and row['Datetime'].hour == 12:
        print(row['Datetime'])
        plt.axvline(x=row['Datetime'], ymin=0.05, ymax=0.95, color='lightgrey', label='axvline')

plt.show()
