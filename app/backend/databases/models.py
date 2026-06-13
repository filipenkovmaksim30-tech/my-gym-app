from app.backend.databases.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")

#упражнения на день
class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date,index=True, nullable=False)
    title = Column(String, nullable=False)

    user = relationship("User", back_populates="workout_plans")
    exercises = relationship("PlannedExercise", back_populates="workout_plan", cascade="all, delete-orphan")


#запланированные подходы на упражнение
class PlannedExercise(Base):
    __tablename__ = "planned_exercises"
    id = Column(Integer, primary_key=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"))
    exercise_name = Column(String, nullable=False)
    target_sets = Column(Integer, nullable=False)
    target_reps = Column(Integer, nullable=False)

    workout_plan = relationship("WorkoutPlan", back_populates="exercises")
    actual_sets = relationship("ActualSet", back_populates="planned_exercise", cascade="all, delete-orphan")
    
class ActualSet(Base):
    __tablename__ = "actual_sets" 
    id = Column(Integer, primary_key=True)
    planned_exercise_id = Column(Integer, ForeignKey("planned_exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    reps_done = Column(String, nullable=False)

    planned_exercise = relationship("PlannedExercise", back_populates="actual_sets")
