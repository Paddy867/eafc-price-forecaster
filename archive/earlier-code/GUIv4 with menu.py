import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

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
    
def Show_about_page():
    st.set_page_config(page_title="Price Data Visualizer", layout="wide") #sets up the page
    st.title("About This Software") #writes the title
    #this writes a small paragraph about the software including bullet points. The asterixes make the text between them bold.
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
    df = Read_db_to_df(db_path, "Cleaned_market_prices")
    
    #checks if the database is not empty
    if df is not None:
        #renames the columns of the dataframe ready for graphing
        market_prices_df = pd.DataFrame({
            "Name": df['Item_name'],
            "Date": pd.to_datetime(df['Date_time']),
            "Price": df['Price']
        })
        
        #sets up the page name, title, layout and sidebar
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

def Show_forecaster_page():
    pass

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


# To run: streamlit run "C:\Users\paddy\OneDrive - Lancing College\NEA\Code\v3\GUIv4 with menu.py"