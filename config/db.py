from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://root:@localhost:3306/b7_locator",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
