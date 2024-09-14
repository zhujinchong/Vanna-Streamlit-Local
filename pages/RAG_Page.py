import time
import streamlit as st
import pandas as pd
from src.Local_Vanna import *


@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = MyVanna(config={'model': OPENAI_MODEL})
    vn.connect_to_mysql(host=MYSQL_HOST, dbname=MYSQL_DB_NAME, user=MYSQL_USER_NAME, password=MYSQL_PASSWORD, port=MYSQL_PORT)
    return vn

def get_training_data():
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
with st.form('addition'):
    train_question = st.text_input("Question")
    train_sql = st.text_input("SQL")
    submit = st.form_submit_button('submit')
    if submit:
        succ = add_training_data(train_question, train_sql)
        if succ:
            st.write(f"successfully.")
        else:
            st.write(f"faild.")


st.title("Trained Data")
df = get_training_data()
dataframe = st.dataframe(df)


st.title("Delete")
with st.form('delete'):
    index_to_delete = st.selectbox(label="Select row to delete", options=df.index, index=None)
    if index_to_delete != None:
        st.dataframe(df.iloc[index_to_delete])
    if st.form_submit_button('submit'):
        if index_to_delete != None and delete_training_data(df.iloc[index_to_delete]['id']):
            st.write(f"successfully.")
        else:
            st.write("failed!")