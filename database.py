from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    reports = relationship("Report", back_populates="user")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String, nullable=False)
    category = Column(String, nullable=True)
    authority = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    posted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="reports")

def init_database():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

def create_user(name: str, email: str):
    db = get_db_session()
    try:
        user = User(name=name, email=email, credits=0)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def get_user(user_id: int):
    db = get_db_session()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

def create_report(user_id: int, image_url: str, category: str = None, authority: str = None, caption: str = None):
    db = get_db_session()
    try:
        report = Report(user_id=user_id, image_url=image_url, category=category, authority=authority, caption=caption, posted=False)
        db.add(report)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits += Config.CREDITS_FOR_UPLOAD
        db.commit()
        db.refresh(report)
        return report
    finally:
        db.close()

def get_user_reports(user_id: int):
    db = get_db_session()
    try:
        return db.query(Report).filter(Report.user_id == user_id).all()
    finally:
        db.close()

def update_user_credits(user_id: int, points: int):
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits += points
            db.commit()
    finally:
        db.close()

def mark_report_posted(report_id: int):
    db = get_db_session()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report and not report.posted:
            report.posted = True
            user = db.query(User).filter(User.id == report.user_id).first()
            if user:
                user.credits += Config.CREDITS_FOR_SOCIAL_POST
            db.commit()
    finally:
        db.close()

def update_report_ai_data(report_id: int, category: str, authority: str, caption: str):
    db = get_db_session()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.category = category
            report.authority = authority
            report.caption = caption
            db.commit()
    finally:
        db.close()
