# from fastapi import FastAPI
# from auth_routers import auth_router
# from fastapi_jwt_auth import AuthJWT
# from schemas import Settings


# app= FastAPI(title='gpt-4')

# app.include_router(auth_router)
# # app.include_router(api_router)

# @AuthJWT.load_config()
# def get_config():
#     return Settings()