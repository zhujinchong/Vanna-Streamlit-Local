from .vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from .vanna.openai.openai_chat import OpenAI_Chat
import chromadb
import openai
import ollama


OPENAI_API_KEY = "sk-"
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_MODEL = "qwen2-1.5b-instruct"

MYSQL_HOST = 'localhost'
MYSQL_DB_NAME = 'test'
MYSQL_USER_NAME = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_PORT = 13306


"""
use test;
create table Student(Sno char(3) not null primary key,Sname char(8) not null,Ssex char(2) not null,Sbirthday datetime,Class char(5));
Insert Into Student values ('108','曾华','男','1977-09-01','95033');
insert into Student values ('105','匡明','男','1975-10-02','95031');
insert into Student values ('107','王丽','女','1976-01-23','95033');
insert into Student values ('101','李军','男','1976-02-20','95033');
insert into Student values ('109','王芳','女','1975-02-10','95031');
insert into Student values ('103','陆君','男','1974-06-03','95031');
"""


client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL,)


class MyEmbeddingFunction(chromadb.EmbeddingFunction):
    def __call__(self, texts: chromadb.Documents) -> chromadb.Embeddings:
        res = []
        for x in texts:
            resp = ollama.embeddings(
                model='shaw/dmeta-embedding-zh-small:latest',
                prompt=x,
            )
            res.append(resp['embedding'])
        return res


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config={'embedding_function': MyEmbeddingFunction()})
        OpenAI_Chat.__init__(self, client=client, config=config)


if __name__ == '__main__':
    vn = MyVanna(config={'model': OPENAI_MODEL})
    vn.connect_to_mysql(host=MYSQL_HOST, dbname=MYSQL_DB_NAME, user=MYSQL_USER_NAME, password=MYSQL_PASSWORD, port=MYSQL_PORT)


    vn.train(ddl='''create table Student(Sno char(3) not null primary key,Sname char(8) not null,Ssex char(2) not null,Sbirthday datetime,Class char(5));''')
    vn.train(question='出生于1975年的学生有哪些？', sql='SELECT S.Sno, S.Sname FROM Student S WHERE YEAR(S.Sbirthday) = 1975;')

    resp = vn.ask('出生于1975年的学生有哪些？')
    print(resp)
