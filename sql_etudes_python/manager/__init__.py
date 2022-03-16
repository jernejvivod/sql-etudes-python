from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+pg8000://postgres:postgres@localhost:5432/employees')
Session = sessionmaker(bind=engine)
