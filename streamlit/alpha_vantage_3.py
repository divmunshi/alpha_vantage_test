import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
import requests
import numpy as np
import psycopg2

st.title("Stock Market Explorer")

# Function to return JSON data from API
def return_json(url):
    response = requests.get(url)
    return response.json()

# Function to connect to PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            host='data-sandbox.c1tykfvfhpit.eu-west-2.rds.amazonaws.com',
            database='pagila',
            user='de_dimu',
            password='inmagged'
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Error connecting to PostgreSQL: {e}")
        return None

# Function to execute PostgreSQL queries
def execute_query(conn, query, values=None):
    try:
        cur = conn.cursor()
        if values:
            cur.execute(query, values)
        else:
            cur.execute(query)
        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        st.error(f"Error executing query: {e}")

# API call to Alpha Vantage
tope = return_json('https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=demo')
most_actively_traded_data = tope['most_actively_traded']

# Create DataFrame from API data
most_active_pd = pd.DataFrame(columns=['Ticker', 'Price', 'Change Amount', 'Change Percentage', 'Volume'])
for data in most_actively_traded_data:
    name = data['ticker']
    price = float(data['price'])
    change_amount = float(data['change_amount'])
    volume = int(data['volume'])
    change_percentage = float(data['change_percentage'].rstrip('%')) / 100
    most_active_pd.loc[len(most_active_pd)] = [name, price, change_amount, change_percentage, volume]


# Display DataFrame in Streamlit
st.write('This app displays information about the most actively traded tickers.')
st.write(most_active_pd)

# Connect to PostgreSQL
conn = connect_to_postgres()

# If connection successful, create table and insert data
if conn:
    # Create table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS student.dm_MostActive (
        ticker VARCHAR(30),
        price FLOAT,
        change_amount FLOAT,
        change_percentage FLOAT,
        volume INT
    );
    """
    execute_query(conn, create_table_query)

    # Insert data into the table
    for index, row in most_active_pd.iterrows():
        insert_query = """
        INSERT INTO student.dm_MostActive (ticker, price, change_amount, change_percentage, volume)
        VALUES (%s, %s, %s, %s, %s);
        """
        execute_query(conn, insert_query, (row['Ticker'], row['Price'], row['Change Amount'], row['Change Percentage'], row['Volume']))

    
    conn.close()  # Close the connection

# Visualizations
# Add your visualizations here
# Visualizations
st.subheader('Volume Comparison for Each Company')
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(most_active_pd['Ticker'], most_active_pd['Volume'], color='skyblue')
ax.set_title('Volume Comparison for Each Company')
ax.set_xlabel('Ticker')
ax.set_ylabel('Volume')
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y')
st.pyplot(fig)

st.subheader('Price vs. Change Amount for Each Ticker')
fig, ax = plt.subplots(figsize=(12, 8))
for i, ticker in enumerate(most_active_pd['Ticker'].unique()):
    subset = most_active_pd[most_active_pd['Ticker'] == ticker]
    ax.scatter(subset['Price'], subset['Change Amount'], color=np.random.rand(3,), label=ticker)

ax.set_title('Price vs. Change Amount for Each Ticker')
ax.set_xlabel('Price')
ax.set_ylabel('Change Amount')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True)
st.pyplot(fig)

st.subheader('Volume vs. Change Amount for Each Ticker')
fig, ax = plt.subplots(figsize=(10, 6))
for i, ticker in enumerate(most_active_pd['Ticker'].unique()):
    subset = most_active_pd[most_active_pd['Ticker'] == ticker]
    ax.scatter(subset['Volume'], subset['Change Amount'], color=np.random.rand(3,), label=ticker)

ax.set_title('Volume vs. Change Amount for Each Ticker')
ax.set_xlabel('Volume')
ax.set_ylabel('Change Amount')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True)
st.pyplot(fig)

st.subheader('Price Distribution for Each Ticker')
fig, ax = plt.subplots(figsize=(10, 6))
for i, ticker in enumerate(most_active_pd['Ticker'].unique()):
    subset = most_active_pd[most_active_pd['Ticker'] == ticker]
    ax.hist(subset['Price'], bins=20, color=np.random.rand(3,), edgecolor='black', alpha=0.5, label=ticker)

ax.set_title('Price Distribution for Each Ticker')
ax.set_xlabel('Price')
ax.set_ylabel('Frequency')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True)
st.pyplot(fig)

st.subheader('Change Percentage Distribution for Each Ticker')
fig, ax = plt.subplots(figsize=(10, 6))
for i, ticker in enumerate(most_active_pd['Ticker'].unique()):
    subset = most_active_pd[most_active_pd['Ticker'] == ticker]
    ax.hist(subset['Change Percentage'], bins=20, color=np.random.rand(3,), edgecolor='black', alpha=0.5, label=ticker)

ax.set_title('Change Percentage Distribution for Each Ticker')
ax.set_xlabel('Change Percentage')
ax.set_ylabel('Frequency')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True)
st.pyplot(fig)

st.subheader('Volume Distribution for Each Ticker')
fig, ax = plt.subplots(figsize=(10, 6))
for i, ticker in enumerate(most_active_pd['Ticker'].unique()):
    subset = most_active_pd[most_active_pd['Ticker'] == ticker]
    ax.hist(subset['Volume'], bins=20, color=np.random.rand(3,), edgecolor='black', alpha=0.5, label=ticker)

ax.set_title('Volume Distribution for Each Ticker')
ax.set_xlabel('Volume')
ax.set_ylabel('Frequency')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True)
st.pyplot(fig)
    

# PostgreSQL Connection and Queries
conn = connect_to_postgres()
if conn:
    execute_query(conn, "SELECT * FROM student.dm_MostActive as most_active;")
    conn.close()
