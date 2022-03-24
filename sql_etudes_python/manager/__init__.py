import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+pg8000://postgres:postgres@localhost:5432/employees')
Session = sessionmaker(bind=engine)


def connect():
    return psycopg2.connect(host='127.0.0.1', database='employees', user='postgres', password='postgres')


def disconnect(conn):
    if conn is not None:
        conn.close()
