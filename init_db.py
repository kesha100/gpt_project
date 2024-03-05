from database import engine, Base
from models import User, User_Response

Base.metadata.create_all(bind=engine)