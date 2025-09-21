# app/storage.py\n# SQLite storage logic.\n
# app/storage.py
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.environ.get("RR_DB", "sqlite:///resume_relevance.db")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    candidate_name = Column(String, nullable=True)
    score = Column(Integer)
    verdict = Column(String)
    parsed_json = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_result(obj: dict):
    """Save one result dict into DB"""
    session = SessionLocal()
    r = Result(
        filename=obj.get("filename"),
        candidate_name=obj.get("candidate_name"),
        score=obj.get("final_score"),
        verdict=obj.get("verdict"),
        parsed_json=obj
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    session.close()
    return r.id

def get_all_results():
    """Retrieve all results sorted by score"""
    session = SessionLocal()
    rows = session.query(Result).order_by(Result.score.desc()).all()
    session.close()
    return rows
