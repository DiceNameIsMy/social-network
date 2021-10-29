import sqlalchemy as sa

# create an engine
engine = sa.create_engine('postgresql+psycopg2://user:pass@db:5432/database')

from sqlalchemy.ext.declarative import declarative_base
# define declarative base
Base = declarative_base()

# reflect current database engine to metadata
metadata = sa.MetaData(engine)
metadata.reflect()

# build your User class on existing `users` table
class CustomUser(Base):
    __table__ = sa.Table("accounts_customuser", metadata)
    
# call the session maker factory
Session = sa.orm.sessionmaker(engine)
session = Session()

# filter a record 
user = session.query(CustomUser).filter(CustomUser.id==1).first()
print(user.username)
