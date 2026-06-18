from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    day = Column(String)
    parent_name = Column(String)
    parent_email = Column(String)
    parent_phone = Column(String)
    age_level = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    price = Column(Float)
    payment_status = Column(String)
    welcome_kit = Column(Boolean)
    status = Column(String)
    internal_notes = Column(Text)
    season_id = Column(Integer, ForeignKey("seasons.id"))


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    season_id = Column(Integer, ForeignKey("seasons.id"))


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    day = Column(String)
    time = Column(Time)
    lesson_type = Column("type", String)
    notes = Column(Text)
    coach_id = Column(Integer, ForeignKey("coaches.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))


class Makeup(Base):
    __tablename__ = "makeups"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    original_date = Column(Date)
    makeup_date = Column(Date)
    reason = Column(String)
    notes = Column(Text)
    season_id = Column(Integer, ForeignKey("seasons.id"))


class StudentLesson(Base):
    __tablename__ = "student_lessons"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), primary_key=True)
