from openai import OpenAI
from dotenv import load_dotenv
import os
from mydbconnector import execute_query, get_schema
from table_names import TABLE_NAMES
import json

load_dotenv()

client = OpenAI()


tools = [
    {
        "type": "function",
        "name": "get_schema",
        "description": (
            "Get the database schema including columns and data types "
            "for one or more Sakila tables. Call this before generating SQL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_names": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Names of the tables whose schemas are required."
                }
            },
            "required": ["table_names"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "execute_query",
        "description": (
            "Execute a read-only MySQL SELECT query against the Sakila database. "
            "Call this only after obtaining the required table schemas."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The MySQL SELECT query to execute."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
]

tool_map = {"get_schema": get_schema, "execute_query": execute_query}

history = [{'role': 'developer', 'content': 'You are an expert text-to-SQL agent for a MySQL Sakila database.'}]
history.append({'role': 'developer', 'content': 'Here are the table names in the Sakila database:\n\n' + TABLE_NAMES})
history.append({'role': 'developer', 'content': """
                                            For every database question:

                                            1. Determine which tables are likely required.
                                            2. FIRST call get_schema for those tables.
                                            3. Never guess column names or relationships.
                                            4. After receiving the schemas, construct the shortest correct MySQL query.
                                            5. Call execute_query with that query.
                                            6. Use the query result to answer the user's question.

                                            Never call execute_query before obtaining the relevant schemas.
                                            Only generate read-only SELECT queries.
                """
})



while True:

    user_input = input("Enter your question (or type 'exit' to quit): ")

    if user_input.lower() == 'exit':
        break

  
    history.append({'role': 'user', 'content': user_input})    

    while True:

        resp = client.responses.create(
            model="gpt-5.6-sol", input=history, tools=tools, parallel_tool_calls=False)

        history += resp.output

        function_calls = [
                item
                for item in resp.output
                if item.type == "function_call"
            ]

        if not function_calls:
            print(resp.output_text)
            print(f"HISTORY: {history}")
            break

        for call in function_calls:
            function_name = call.name
            arguments = json.loads(call.arguments)

            if function_name in tool_map:
                try:
                    result = tool_map[function_name](**arguments)
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"error": f"Function '{function_name}' not found."}

            if not isinstance(result, str):
                result = json.dumps(result, default=str)

            history.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result
            })  
            

        
