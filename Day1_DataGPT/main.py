from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
from mydbconnector import execute_query, get_schema
from sakila_context import SAKILA_CONTEXT

load_dotenv()

client = OpenAI()
schema = get_schema("actor")

while True:


    user_input = input("Enter your question: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    ques = f"""
    You are an expert MySQL data analyst. 

    You have access to the following database schema and context: {SAKILA_CONTEXT}

    Based on the schema provided, write a MySQL query to answer the following question: {user_input}


    Rules:
    - Use the table and column names exactly as they appear in the schema.
    - Do not include any additional text, comments, or explanations in your response.
    - Return only select type queries, no insert, update, or delete statements.
    - If the question cannot be answered with the given schema, return a query that selects no rows, such as "SELECT * FROM actor WHERE 1=0;".

    """
    resp = client.responses.create(model="gpt-5.6-sol", input=ques)

    query = resp.output_text

    #print(f"Generated Query: {query}")

    response = execute_query(query)
    if isinstance(response, list):
        if response:
            table = pd.DataFrame(response).fillna("NULL")
            print(table.to_string(index=False))
            print(f"\n{len(response)} row(s) returned.\n")
        else:
            print("No rows returned.\n")
    else:
        print(f"{response} row(s) affected.\n")
