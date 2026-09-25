import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

#base path is the path on my computer to the directory in which there are folders that hold the database, data files, and this code

#define the base path and the path to the database
base_path = r'C:\Users\paddy\OneDrive - Lancing College\NEA\Code'

# Function to read from database
def read_db_to_df(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name}"
        DataFrame = pd.read_sql_query(query, conn) #select all of the records in the database that are included in the selection query defined above
        conn.close()
        return DataFrame # return this database with records from the database
    except Exception as e: #if this function throws an error it is caught and tells the user there was an error in this function and what the error was
        print(f"Error reading database: {e}")
        return None

def main():
    #read the data from the database into a dataframe
    db_path = os.path.join(base_path, 'Output Files', 'Market_prices.db')
    Market_prices_array = read_db_to_df(db_path, "Market_prices")
    
    #checks if the database is not empty
    if Market_prices_array is not None:
        #renames the columns of the dataframe ready for graphing
        market_prices_df = pd.DataFrame({
            "Name": Market_prices_array['Item_name'],
            "Date": pd.to_datetime(Market_prices_array['Date_time']),
            "Price": Market_prices_array['Price']
        })
        
        #sets up the page name, title, layout and sidebar
        st.set_page_config(page_title="Market Price Visualizer", layout="wide")
        st.title("Historical Market Prices")
        
        #once again checks if the new filtered dataframe is empty and then graphs the data using plotly.express
        if not market_prices_df.empty:
            fig = px.line(market_prices_df, x="Date", y="Price", color="Name", title="Historical Market Prices")
            fig.update_layout(xaxis_title="Date", yaxis_title="Price", legend_title="Items Graphed", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available in the database.")

main()
# To run: streamlit run "C:\Users\paddy\OneDrive - Lancing College\NEA\Code\v3\GUIv3.py"