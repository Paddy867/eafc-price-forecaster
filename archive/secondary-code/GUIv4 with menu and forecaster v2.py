import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import numpy as np
from sklearn.linear_model import LinearRegression

#base path is the path on my computer to the directory in which there are folders that hold the database, data files, and this code

#define the base path and the path to the database
base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA\Code'

# Function to read from database
def Read_db_to_df(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn) #select all of the records in the database that are included in the selection query defined above
        conn.close()
        return df # return this database with records from the database
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error reading database: {e}")
        return None
    
    
def Show_forecaster_page():
        #access the cleaned data out of the database and ensure that its type is datetime
        db_path = os.path.join(base_path, 'Output Files', 'Market_prices_cleaned_all.db')
        cleaned_df = Read_db_to_df(db_path, "Cleaned_market_prices")
        cleaned_df['Date_time'] = pd.to_datetime(cleaned_df['Date_time'])
        
        #set the title of the page and the sidebar header
        st.set_page_config(page_title="Price Data Visualizer", layout="wide") #sets up the page
        st.title("Price Forecaster")
        st.write("")
        st.sidebar.header("Select which item to forecast:")
        
        #like the graphing page get the list of available items and then using the selectbox allow the user to choose one item from the available items
        available_items = cleaned_df["Item_name"].unique().tolist()
        item_selected = st.sidebar.selectbox("Select Item to Forecast", options = available_items, index = 0)
        filtered_df = cleaned_df[cleaned_df["Item_name"] == item_selected]
        
        #create a slider to determine how long the forecast should be with default value 7 days and min and max values 1 and 30
        days_to_forecast = st.sidebar.slider("Number of Days to Forecast:", min_value = 3, max_value = 30, value = 7)
        
        #use the forecast prices function to get teh forecast dataframe
        forecast_df = forecast_prices(filtered_df, days_to_forecast)
        
        #put one more column into each dataframe labeling which dataframe the record comes from and concatinate both dataframes together to create one to graph
        filtered_df['Data Type'] = 'Historical'
        forecast_df['Data Type'] = 'Forecast'
        plot_df = pd.concat([filtered_df[['Date_time', 'Price', 'Data Type']], forecast_df[['Date_time', 'Price', 'Data Type']]], ignore_index=True)
        
        forecast_graph = px.line(
        plot_df,
        x='Date_time',
        y='Price',
        #colour is determined by what datafraame the data originally came from
        color='Data Type',
        labels={'Date_time': 'Date', 'Price': 'Price', 'Data Type': 'Data Type'},
        title=f'Historical and Forecasted Prices for {item_selected}',
        color_discrete_map={'Historical': 'blue', 'Forecast': 'red'})
        
        forecast_graph.update_layout(xaxis_title="Date", yaxis_title="Price", legend_title="Items Graphed", hovermode="x unified")
        st.plotly_chart(forecast_graph)
    
def forecast_prices(cleaned_df, days_to_forecast):
    #create a list of the dates in the dataframe
    dates = cleaned_df['Date_time'].tolist()
    
    #work out the earliest and latest dates by sorting the dates in the df
    sorted_dates = cleaned_df['Date_time'].sort_values()
    sorted_dates_list = sorted_dates.tolist()
    earliest_date = sorted_dates_list[0]
    latest_date = sorted_dates_list[-1]
    
    days_time_difference = []
    for date in dates:
        #work out the total seconds between the first date and the current date
        difference_seconds = (date - earliest_date).total_seconds()
        #convert seconds into days for the days difference
        difference_days = difference_seconds / (24 * 60 * 60)  
        days_time_difference.append(difference_days)    
    
    #reshape the time differences to be in an array and between -1 and 1
    x = np.array(days_time_difference)
    X = x.reshape(-1, 1)
    #reshape the cleaned_df prices into an array
    Y = np.array(cleaned_df["Price"])
    
    #call the model class
    model = LinearRegression()
    #fit the model to the data
    model.fit(X, Y)
    
    #get values for the days to forecast after the current latest date
    future_dates_including_latest = pd.date_range(start=latest_date, periods=days_to_forecast, freq='D')
    future_dates = future_dates_including_latest[1:]
    
    #same logic as earlier applied to the future days
    future_time_difference = []
    for date in future_dates:
        #work out the total seconds between the first date and the current future date
        difference_seconds = (date - earliest_date).total_seconds()
        #convert seconds into days for the days difference
        difference_days = difference_seconds / (24 * 60 * 60)
        future_time_difference.append(difference_days)
    
    #reshape the future days into an array and between values 1 and -1
    x_future = np.array(future_time_difference)
    X_future = x_future.reshape(-1, 1)
    
    #use the model to predict price values for these days
    future_prices = model.predict(X_future)
    
    forecast_df = pd.DataFrame({'Date_time': future_dates, 'Price': future_prices})
    return forecast_df
        
        
    
def Show_about_page():
    st.set_page_config(page_title="Price Data Visualizer", layout="wide") #sets up the page
    st.title("About This Software") #writes the title
    #this writes a small paragraph about the software including bullet points. The asterixes make the text between them bold
    #I have put this over multiple lines to make it easier to read but when executed there are no line breaks, I also because of this have to use three quotations
    st.write("""
    I decided to create a Price Data Visualiser for the EAFC transfer market for my Computer Science A-Level NEA project. 
    This software is free to use and below is an example of what the hitorical market prices grapher is able to do. 
    - **Developer**: Patrick Joyce
    - **Purpose**: This software allows users to easily graph chemistry data using the historical market prices we have collected.
    - **How it Works**: I have collected data from FUTWIZ website since 2023. This data has been put into an SQL database that is read into a 
                        DataFrame when the application starts. I have used the Streamlit app framework to create this GUI, and this GUI interacts
                        this DataFrame to graph the data.
    """)
    left_column, middle_column, right_column = st.columns([1, 20, 1]) #splits the page into three columns, with the middle column being much wider
    with middle_column: #places an image in the middle column so that it is centered on the page
        st.image("C:/Users/paddy/OneDrive - Lancing College/NEA/code/Image for the about page/market prices visualiser 2.png", caption="Market Prices Visualizer Example", width=1000)

def Show_graphing_page():
    #read the data from the database into a dataframe
    db_path = os.path.join(base_path, 'Output Files', 'Market_prices_cleaned_all.db')
    cleaned_df = Read_db_to_df(db_path, "Cleaned_market_prices")
    
    #checks if the database is not empty
    if cleaned_df is not None:
        #renames the columns of the dataframe ready for graphing
        market_prices_df = pd.DataFrame({"Name": cleaned_df['Item_name'],"Date": pd.to_datetime(cleaned_df['Date_time']),"Price": cleaned_df['Price']})
        
        #sets up the page name, title, layout and sidebar
        st.set_page_config(page_title="Price Data Visualizer", layout="wide") #sets up the page
        st.title("Historical Market Prices")
        st.sidebar.header("Graphs Settings")

        #sets up the multiselect in the sidebar by creating a list of items to select, then creating the multiselect option 
        #and then filtering the dataframe to only include these items
        items_to_select = market_prices_df["Name"].unique().tolist()
        currently_selected_items = st.sidebar.multiselect("Select Items to Graph", options=items_to_select, default=[items_to_select[0]])
        filtered_market_prices = market_prices_df[(market_prices_df["Name"].isin(currently_selected_items))]
        
        #once again checks if the dataframe is empty and then graphs the data using plotly.express
        if not filtered_market_prices.empty:
            fig = px.line(filtered_market_prices, x="Date", y="Price", color="Name", title="Historical Market Prices")
            fig.update_layout(xaxis_title="Date", yaxis_title="Price", legend_title="Items Graphed", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available in the database.")

def Main_menu():
    st.title("Market Price Visualiser Menu") #write the title and text on the page
    st.write("Please select a page to visit:")
    with st.form(key="navigation_form"): #creates a form to put inputs in such as buttons and sliders (I only use buttons here)
        first_column, second_column, third_column, fourth_column, fifth_column= st.columns([1, 1, 1, 1, 1])  #makes sure that the buttons are equally spaced out
        #puts buttons for each menu option into the form
        with first_column:
            graphing_button = st.form_submit_button("Market Price Graphing")
        with third_column:
            about_button = st.form_submit_button("About This Software")
        with fifth_column:
            forecaster_button = st.form_submit_button("Forecaster")
        #checks if the button was pressed and if it was changes the session state to whatever button was pressed and refreshes the page
        if graphing_button:
            st.session_state.page = "Market Price Graphing"
            st.rerun()
        if about_button:
            st.session_state.page = "About This Software"
            st.rerun()
        if forecaster_button:
            st.session_state.page = "Forecaster"
            st.rerun()

if __name__ == "__main__":
    if not st.session_state.keys():  
        st.session_state.page = "Main Menu"
    if st.session_state.page == "Main Menu":
        Main_menu()
    elif st.session_state.page == "Market Price Graphing":
        Show_graphing_page()
    elif st.session_state.page == "About This Software":
        Show_about_page()
    elif st.session_state.page == "Forecaster":
        Show_forecaster_page()

    # Reset to Main Menu button on other pages
    if st.session_state.page != "Main Menu":
        if st.button("Back to Main Menu"):
            st.session_state.page = "Main Menu"
            st.rerun()


# To run: streamlit run "C:\Users\paddy\OneDrive - Lancing College\NEA\Code\v4\GUIv4 with menu and forecaster v2.py"