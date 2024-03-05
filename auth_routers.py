from fastapi import APIRouter,status
from database import Session, engine
from schemas import SignUpModel, LoginModel
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encorders import jsonable_encoder



auth_router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)

session=Session(bind=True)

@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user:SignUpModel):
    db_email=session.query(User).filter(User.email==user.email).first()

    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="User with this email already exist")

    db_username =session.query(User).filter(User.username==user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
        detail="User with this username already exist")

    new_user = User(
        username=user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_staff = user.is_staff, 
    )
    session.add(new_user)
    session.commit()
    return new_user

@auth_router.post('/login', status_code=200)
async def login(user:LoginModel, Authorize:AuthJWT=Depends()):
    db_user=session.query(User).filter(User.username==user.username).first()

    if db_user and check_password_hash(db_user.password,user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response ={
            "access": access_token,
            "refresh": refresh_token,
        }

        return jsonable_encoder(response)

    raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
    detail="invalid username or password"
    )