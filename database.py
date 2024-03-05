from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://hello:1@localhost/gpt_4', echo=True)
Base = declarative_base()
Session = sessionmaker()