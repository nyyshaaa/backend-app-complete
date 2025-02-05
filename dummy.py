# from fastapi import FastAPI
# from typing import Optional

# app=FastAPI() # instance of FastAPI class ,main entry point to use FastAPI

# @app.get("/")
# async def read_root():
#     return {"message":"Hey  !"}

# #FastAPI will take any string present in path handler function and not in path operator as query parameter of that path
# #if anything in query parameter optional then not required to pass as query parameter
# #for path parameter must to specify even if used as optional other wise not found error
# @app.get("/greet")
# async def greet_user(uname:str="niya",group:Optional[str]="Insurgent")-> dict:
#     return {"message" : f"Welcome to version module user {uname} belongs to {group} group"}


