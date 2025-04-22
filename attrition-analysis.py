# April 22nd, 2025
# This program will use tools to go through csv data and generate results and graphs


# io and contextlib used to capture print output stdout from generated code safety
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from langchain_openai import OpenAI
from dotenv import load_dotenv
import io
import contextlib


# here load in my .env file 
# instantiates a deterministic LLM temp is at 0. makes outputs consistent
load_dotenv()
llm = OpenAI(temperature=0)




# user passes in the question string and the output head is a string for the model to know 
# what data it is working with 
# prompt sent to gpt 4 via langchain and gets back python code
# .strip() of any white space
def generate_analysis_code(user_question: str, df_head: str) -> str:
    """
    Prompt the LLM to generate Python code using the dataframe `df`.
    """
    prompt = f"""
                You are a helpful data analysis assistant.
                A user has uploaded a CSV file with the following structure (first 5 rows shown):

                {df_head}

                They asked: "{user_question}"

                Write Python code using Pandas and Matplotlib to answer the question.
                Use a variable named `df` for the DataFrame. Assume it is already loaded.
                Do NOT read the CSV again.
                If you show a table, assign it to a variable named `result`.
                If you create a plot, use `matplotlib.pyplot` (already imported as `plt`).
                Only return Python code, no explanations. If you create a table, assign it to a variable named `result`, 
                and print it using `print(result.head())`. If you're answering a question with a single value (like a max, sum, or count), 
                use `print(...)` to display the result. If you create a plot, use `matplotlib.pyplot` (already imported as `plt`).
                Only return Python code, no explanations.
                """
    return llm.predict(prompt).strip()



def main():
    st.set_page_config(page_title="Analysis Chatbot", page_icon="📊")
    st.title("Analysis Chatbot")
    st.subheader("Ask questions about your CSV data and get smart insights")
    st.markdown("""
                This chatbot uses AI to analyze your uploaded CSV file and respond with text answers, plots, or tables.
                """)

    # user is able to upload teh file of type csv
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("File uploaded. Here's a preview:")
        st.dataframe(df.head())

        # takes in the user's questions input 
        # not null pass in the user's query text + df.head()string of the data
        user_question = st.text_input("Ask a question about your data:")
        if user_question:
            
            code = generate_analysis_code(user_question, df.head().to_string())

            # show the user the output code here
            st.subheader("AI-Generated Code")
            st.code(code, language="python")

            
            try:
                # here we are defining the global variables available inside teh generate code
                # df is the DataFrame
                # plt is Matplotlib for charting
                exec_globals = {"df": df, "plt": plt}
                with contextlib.redirect_stdout(io.StringIO()) as f:
                    # executes the generated python code using exec_globals
                    exec(code, exec_globals)

                stdout_output = f.getvalue()
                if stdout_output:
                    st.subheader("Text Output")
                    st.text(stdout_output)
                    st.text(stdout_output.strip())

                
                if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                    st.subheader("Table Result")
                    st.dataframe(exec_globals["result"].head())

                # checks if any charts/figures were created
                if plt.get_fignums():
                    st.subheader("Chart Output")
                    st.pyplot(plt.gcf())
                    plt.clf()

            except Exception as e:
                st.error(f"Error executing generated code:\n{e}")

if __name__ == "__main__":
    main()
