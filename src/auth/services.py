from fastapi import HTTPException,status
from src.db.schema import User
from sqlalchemy.ext.asyncio import  AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from .schemas import UserCreateInput
from .utils import gen_pass_hash

class UserService:
    async def get_user_identity(self,email:str,session:AsyncSession):
        stmt=select(User.id,User.email,User.password_hash).where(User.email==email) #* check pass security properly
        res=await session.execute(stmt)
        user=res.first()
        return user
    
    async def get_user_id_email(self,email:str,session:AsyncSession):
        stmt=select(User.id,User.email).where(User.email==email)
        res=await session.execute(stmt)
        return res.first()
    
    async def get_user_details(self,user_id:int,session:AsyncSession):   
        user=await session.get(User,user_id) 
        print(user) 
        return user
        # stmt=select(User).where(User.id==user_id)  
        # res=await session.execute(stmt)
        # return res.scalar_one_or_none()

    async def get_user_public(self,user_id:int,session:AsyncSession):   
        stmt=select(User.id,User.name,User.email,User.about,User.avatar).where(User.id==user_id)
        res=await session.execute(stmt)
        return res.first()
    
    async def get_user_id(self,user_id:int,session:AsyncSession):   
        stmt=select(User.id).where(User.id==user_id)  
        res=await session.execute(stmt)
        res=res.first()  # return (id,) or None
        print("user_id",res)
        return res
        
        
    
    async def create_user(self,user_data:UserCreateInput,session:AsyncSession):
        pass_hash=gen_pass_hash(user_data.password)
        new_user=User(email=user_data.email,name=user_data.username,password_hash=pass_hash)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user 
       
            
