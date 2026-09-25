import streamlit as st

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

Show_about_page()

#streamlit run "C:\Users\paddy\OneDrive - Lancing College\NEA\code\v3\About page function.py"


def myround(x, base=100):
    return base * round(x/base)
print(myround(1950))