import time
import streamlit as st
import pandas as pd
from src.Local_Vanna import *


@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = MyVanna(config={'model': OPENAI_MODEL})
    vn.connect_to_mysql(host=MYSQL_HOST, dbname=MYSQL_DB_NAME, user=MYSQL_USER_NAME, password=MYSQL_PASSWORD, port=MYSQL_PORT)
    return vn

# @st.cache_data(show_spinner="Get training data ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.get_training_data()

def add_training_data(question, sql):
    question = question.strip()
    sql = sql.strip()
    if question and sql:
        vn = setup_vanna()
        return vn.add_question_sql(question=question, sql=sql)
    return None

def delete_training_data(id):
    if id:
        vn = setup_vanna()
        return vn.remove_training_data(id)
    return False


st.set_page_config(page_title="Vanna", layout="wide")


st.title("Training")
train_question = st.text_input("Question")
train_table = st.text_input("Table")
train_sql = st.text_input("SQL")
if st.button("Submit"):
    succ = add_training_data(train_question, train_sql)
    if succ:
        st.write(f"successfully.")
    else:
        st.write(f"training faild.")


st.title("Trained Data")
df = generate_questions_cached()
dataframe = st.dataframe(df)


st.title("Delete")
index_to_delete = st.selectbox(label="Select row to delete", options=df.index, index=None)
if index_to_delete != None:
    st.dataframe(df.iloc[index_to_delete])    
if st.button("Delete"):
    if index_to_delete != None and delete_training_data(df.iloc[index_to_delete]['id']):
        df.drop(index=index_to_delete, inplace=True) 
        st.write(f"Row {index_to_delete} deleted successfully.")
    else:
        st.write("failed!")