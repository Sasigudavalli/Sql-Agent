import streamlit as st
import psycopg2
import pandas as pd
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

"""Set up Google Gemini API Key (replace with your key)"""
GENAI_API_KEY = "AIzaSyDXrgWrQ7nLWcY-3FluaniKYTxEowJs_8U"
genai.configure(api_key=GENAI_API_KEY)


DB_CONFIG = {
    "dbname": "northwind",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "55432", 
}



st.write("connected")


llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GENAI_API_KEY)


sql_prompt = PromptTemplate(
    input_variables=["query"],
    template="Convert this user request into an optimized SQL query for PostgreSQL: {query}"
)


sql_chain = LLMChain(llm=llm, prompt=sql_prompt)


def generate_sql(user_input):
    response = sql_chain.run(query=user_input).strip()
    st.write('before',response)
    
    if response.lower().startswith("```"):
        print(response)
        response = response[6:].strip() 
        response = response[:-3]
    st.write("res",response)
    return response



def execute_sql(query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return str(e)

""" FOR User INterface"""
st.title("AI SQL Query Generator (Gemini + Langchain)")


user_input = st.text_input("Enter your request (e.g., 'Show me 10 customers'):")

if st.button("Generate & Execute Query"):
    sql_query = generate_sql(user_input)
    st.code(sql_query, language="sql")  

   
    result = execute_sql(sql_query)
    
    if isinstance(result, pd.DataFrame):
        st.write("### Query Results:")
        #st.dataframe(result) 
        json_result = result.to_json(orient="records", indent=2)
        st.json(json_result)
    else:
        st.error(f"Error: {result}") 
