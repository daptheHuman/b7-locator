from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://root:@localhost:3306/ipc_management", )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

