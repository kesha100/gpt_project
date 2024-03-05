from database import Base
from sqlalchemy import Column, Integer, Text,Boolean, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    email = Column(String(50), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    user_response = relationship('User_Response', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"

class User_Response(Base):
    __tablename__ = 'user_response'

    id = Column(Integer, primary_key=True)
    submission_time = Column(String)
    time_taken = Column(String)
    source = Column(String)
    source_detail = Column(String)
    ip_address = Column(String)
    student_name = Column(String)
    grade_level = Column(String)
    gender = Column(String)
    openness = Column(String)
    conscientiousness = Column(String)
    agreeableness = Column(String)
    neuroticism = Column(String)
    mbti_result = Column(String)
    has_college_major_choice = Column(Boolean)
    chosen_major = Column(String)
    favorite_high_school_subjects = Column(String)
    weight_high_school_subjects = Column(Integer)
    favorite_extracurricular_activities = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='user_response')
    







