from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///assets/entity.db', connect_args={'check_same_thread': False})
#Session = sessionmaker(bind=engine)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))

Base = declarative_base()
