from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

engine = create_engine('sqlite:///assets/entity.db', connect_args={'check_same_thread': False}, echo= True)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base.query = Session.query_property()  # Used by graphql to execute queries

Base.metadata.bind = engine  # Bind engine to metadata of the base class

