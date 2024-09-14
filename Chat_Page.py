import time
import streamlit as st
from src.Local_Vanna import *


@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = MyVanna(config={'model': OPENAI_MODEL})
    vn.connect_to_mysql(host=MYSQL_HOST, dbname=MYSQL_DB_NAME, user=MYSQL_USER_NAME, password=MYSQL_PASSWORD, port=MYSQL_PORT)
    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions(question='test')


@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    # return vn.generate_followup_questions(question=question, sql=sql, df=df)
    return vn.generate_questions(question=question)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)


st.set_page_config(
    page_title="Vanna",
    layout="wide"
)

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Plotly Code", value=False, key="show_plotly_code")
st.sidebar.checkbox("Show Chart", value=False, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Reset", on_click=lambda: set_question(None), use_container_width=True)


st.title("Chat With Your Database!")
avatar_gpt_url = "asserts/LogosOpenaiIcon.svg"


def set_question(question):
    st.session_state["my_question"] = question


assistant_message_suggested = st.chat_message("assistant", avatar=avatar_gpt_url)
if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Ask me a question about your data",
    )


if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    "assistant", avatar=avatar_gpt_url
                )
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
        else:
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_gpt_url
            )
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_gpt_url,
                )
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)

            if should_generate_chart_cached(question=my_question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_gpt_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_gpt_url,
                        )
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("I couldn't generate a chart")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant",
                    avatar=avatar_gpt_url,
                )
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message(
                    "assistant",
                    avatar=avatar_gpt_url,
                )
                followup_questions = generate_followup_cached(
                    question=my_question, sql=sql, df=df
                )
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text(
                        "Here are some possible follow-up questions"
                    )
                    # Print the first 5 follow-up questions
                    for question in followup_questions[:5]:
                        assistant_message_followup.button(question, on_click=set_question, args=(question,))

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_gpt_url
        )
        assistant_message_error.error("I wasn't able to generate SQL for that question")

