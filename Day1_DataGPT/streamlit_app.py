"""Run with: python -m streamlit run myenv/streamlit_app.py"""

import os
from pathlib import Path
import re

import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from mydbconnector import get_connection
from sakila_context import SAKILA_CONTEXT


load_dotenv(Path(__file__).with_name(".env"))

INSTRUCTIONS = f"""You are an expert MySQL data analyst.
Use this database schema and context:
{SAKILA_CONTEXT}

Return exactly one SELECT statement answering the user's question.
Use only the tables and columns in the provided schema.
Do not include markdown, comments, explanations, or multiple statements.
Do not modify data, write files, or use locking clauses.
Limit results to 500 rows unless the question requests fewer.
If the question cannot be answered from this schema, return exactly UNSUPPORTED.
"""


def generate_query(question: str) -> str:
    client = OpenAI(timeout=30.0, max_retries=1)
    response = client.responses.create(
        model="gpt-5.6-sol",
        instructions=INSTRUCTIONS,
        input=question,
    )
    query = response.output_text.strip()
    if query == "UNSUPPORTED":
        raise ValueError("Please ask a question about the Sakila rental database.")
    # Accept a single SELECT only. Reject ambiguous output before execution.
    query = query.removesuffix(";").strip()
    if (
        not re.match(r"^SELECT\b", query, re.IGNORECASE)
        or ";" in query
        or re.search(r"--|/\*|#|\bINTO\b|\bFOR\s+UPDATE\b|\bLOCK\b", query, re.IGNORECASE)
    ):
        raise ValueError("Could not generate a supported read-only query. Please rephrase your question.")
    return query


def fetch_answer(query: str) -> tuple[pd.DataFrame, bool]:
    """Use a read-only transaction and fetch at most 500 displayed rows."""
    connection = get_connection()
    cursor = None
    try:
        connection.start_transaction(readonly=True)
        cursor = connection.cursor()
        cursor.execute("SET SESSION MAX_EXECUTION_TIME = 10000")
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchmany(501)
        return pd.DataFrame(rows[:500], columns=columns), len(rows) > 500
    finally:
        # Closing the connection also discards any unread rows and transaction.
        connection.close()


def main():
    st.set_page_config(page_title="Sakila DataGPT", page_icon="📊", layout="wide")
    st.title("📊 Sakila DataGPT")
    st.write("Ask a question about films, actors, customers, or rentals.")
    st.caption("Try: Which 10 films have been rented the most?")

    if not os.getenv("OPENAI_API_KEY") or not os.getenv("MYSQL_DATABASE"):
        st.error("Set OPENAI_API_KEY and MYSQL_DATABASE in myenv/.env before asking a question.")
        st.stop()

    with st.form("question_form"):
        question = st.text_input("Your question", placeholder="Which actors appear in the most films?")
        submitted = st.form_submit_button("Get answer", type="primary")

    if submitted:
        st.session_state.pop("answer", None)
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Finding your answer…"):
                    query = generate_query(question.strip())
                    table, truncated = fetch_answer(query)
                st.session_state.answer = (question.strip(), query, table, truncated)
            except ValueError as error:
                st.warning(str(error))
            except OpenAIError:
                st.error("The AI service request failed. Check your API key, quota, and connection, then try again.")
            except mysql.connector.Error:
                st.error("The database query failed. Check your MySQL settings and that Sakila is available, or rephrase your question.")

    if "answer" in st.session_state:
        question, query, table, truncated = st.session_state.answer
        st.subheader("Answer")
        st.write(question)
        if table.empty:
            st.info("No matching rows found.")
        else:
            st.dataframe(table, hide_index=True, width="stretch")
            st.caption(f"{len(table)} row(s) displayed. Results are limited to 500 rows.")
            if truncated:
                st.info("More rows are available. Narrow your question to see a smaller result.")
            st.download_button(
                "Download CSV", table.to_csv(index=False).encode("utf-8"),
                file_name="sakila_answer.csv", mime="text/csv",
            )
        with st.expander("View SQL query"):
            st.code(query, language="sql")


if __name__ == "__main__":
    main()
