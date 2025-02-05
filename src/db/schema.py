from sqlalchemy.orm import declarative_base,relationship,DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column,BigInteger,String,Text,TIMESTAMP,Integer,ForeignKey,Numeric,Date,Enum,DECIMAL,Boolean,UniqueConstraint
from datetime import datetime,timedelta
import enum

DecBase=declarative_base()

class connstatus(enum.Enum):
    PENDING='pending'
    ACCEPTED='accepted'
    REJECTED='rejected'

class orderstatus(enum.Enum):
    PENDING='pending'
    COMPLETED='completed'
    INPROGRESS='inprogress'

#ORM will map database table to python classes and cols to class properties

class User(DecBase):
    """users table to store all unique users with their profile data"""
    __tablename__='users'  
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    name=Column(String(length=120),nullable=False)
    email=Column(String(length=255),nullable=False,unique=True)
    password_hash=Column(String(length=300),nullable=False,unique=True)
    about=Column(Text,nullable=True)
    avatar=Column(Text,nullable=False) #stores image url
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)
    deleted_at=Column(TIMESTAMP,nullable=True)
    updated_at=Column(TIMESTAMP,default=datetime.now,onupdate=datetime.now)
     
    link_versions=relationship("Versions",secondary='userversions',back_populates="link_users")
    link_goals=relationship("Goals",back_populates="link_users")

class Versions(DecBase):
    """ version table to store all possible unique versions"""
    __tablename__='versions'
    id=Column(Integer,primary_key=True,autoincrement=True)
    vname=Column(String(length=400),nullable=False,unique=True)
    # strength_xp=Column(Integer,default=0)   
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)
    updated_at=Column(TIMESTAMP,default=datetime.now,onupdate=datetime.now)

    link_users=relationship("User",secondary='userversions',back_populates="link_versions")
    link_goals=relationship("Goals",back_populates="link_versions")

class UserVersions(DecBase):
    """to relate users and version via many to many relationship"""
    __tablename__='userversions'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    user_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    version_id=Column(Integer,ForeignKey("versions.id",ondelete="CASCADE")) 

    __table_args__ = (
        UniqueConstraint("user_id","version_id",name="unique_user_version"),
    )

class Goals(DecBase):
    """Goals for each version of users"""
    __tablename__='goals'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    user_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    version_id=Column(Integer,ForeignKey("versions.id",ondelete="CASCADE")) 
    title=Column(String(length=500),nullable=False)
    description=Column(Text,nullable=True)
    deadline=Column(Date,nullable=False,default=datetime.now().date() + timedelta(days=365))
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)
    updated_at=Column(TIMESTAMP,default=datetime.now,onupdate=datetime.now)
    #**progress add it
    
    link_users=relationship("User",back_populates="link_goals") #user to goals (1 to many mapping) 
    link_versions=relationship("Versions",back_populates="link_goals")  #version to goals (1 to many mapping) 

class Frosties(DecBase):
    """table for some cool things built by users"""
    __tablename__='frosties'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    user_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    title=Column(String(600),nullable=False)
    description=Column(Text,nullable=True)
    item_image=Column(Text,nullable=False)
    qty=Column(Integer,nullable=False,default=1)
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)
    updated_at=Column(TIMESTAMP,default=datetime.now,onupdate=datetime.now)
    price=Column(Numeric(20,2),nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id","title",name="unique_user_title"),
    )
    #**likes count

class likes(DecBase):
    __tablename__='likes'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    user_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    frost_id=Column(BigInteger,ForeignKey("frosties.id",ondelete="CASCADE")) 
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id","frost_id",name="unique_user_like"),
    )

class orders(DecBase):
    __tablename__='orders'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    buyer_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)
    status=Column(Enum(orderstatus),default=orderstatus.PENDING,nullable=False)
    #**payment key 

class orderitems(DecBase):
    __tablename__='orderitems'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    order_id=Column(BigInteger,ForeignKey("orders.id",ondelete="CASCADE"))
    frost_id=Column(BigInteger,ForeignKey("frosties.id",ondelete="SET NULL"))
    seller_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE")) 
    quantity=Column(Integer,nullable=False,default=1)
    created_at=Column(TIMESTAMP,nullable=False,default=datetime.now)

    __table_args__ = (
        UniqueConstraint("order_id","frost_id",name="unique_order_item"),
    )

class connections(DecBase):
    __tablename__='connections'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    sender_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE"))
    receiver_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE"))
    status=Column(Enum(connstatus),default=connstatus.PENDING,nullable=False)

    __table_args__ = (
        UniqueConstraint("sender_id","receiver_id",name="unique_friend_request"),
    )

class followers(DecBase):
    __tablename__='followers'
    id=Column(BigInteger,primary_key=True,autoincrement=True)
    follower_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE"))
    followed_id=Column(BigInteger,ForeignKey("users.id",ondelete="CASCADE"))

    __table_args__ = (
        UniqueConstraint("follower_id","followed_id",name="unique_follows"),
    )
