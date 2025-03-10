import secrets,asyncio,os,random
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from src.db.schema import Versions,User,UserVersions, Goals, Frosties, orders, orderitems, connections, followers
from src.__init__ import app
from sqlalchemy import select,delete,func,update
from passlib.context import CryptContext
import secrets,getpass
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from src.db.connection import async_session

pass_context=CryptContext(schemes=['bcrypt'])

passwords=os.getenv("sample_passwords")



def gen_password_hash(password:str):
    hashp=pass_context.hash(password)
    return hashp

hash_passwords=[gen_password_hash(p) for p in passwords]

emails=["nyshaaa@dreamer.com","nyssaaa@dreamer.com","nishaaa@dreamer.com"]
names=["nysha","nyssa","nisha"]

versions_list=["Martial Artist+Scitech Engineer+Free Runner","Fauji","Cosplay+Scifi Artist","Fighter Pilot","Athlete","Stunts Artist","Engineer","Wood Worker"]

avatar_img_links=["https://t3.ftcdn.net/jpg/05/73/26/24/240_F_573262496_esTYXe6GmES7ya6Ek2L2aJFwmu43Js2p.jpg",
                 "https://t3.ftcdn.net/jpg/10/34/57/30/360_F_1034573005_yW9MCan8PQKOLulY9q2jwtH5Ve6qOQLy.jpg",
                 "https://t3.ftcdn.net/jpg/07/50/06/62/240_F_750066208_HZH7QKsCHjbEuwf2rJnjeS6u1EKc7Ksp.jpg"]

frost_img_links=["https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcSxcPxMEiJ-l2e8eEX104jG2q-c8_0K_GCl_6ucE8ACPChIGRI06gsmaptXpPzKPgyAP0tnNSK8JtqeoucWGOuYd4TTbgG1VLZk-6KD43AStfopA5UimrFgAQ",
                 "https://i.pinimg.com/736x/1a/df/c1/1adfc1f8e1bac82c2144229bdce828df.jpg",
                 "https://i.pinimg.com/236x/31/ff/d7/31ffd7d79115c7e97c96ff2c92e7503a.jpg",
                 "https://i.pinimg.com/236x/f1/b8/92/f1b892a4b7c12a1509b012fd80ef4e1d.jpg",
                 "https://i.pinimg.com/236x/a6/a0/e5/a6a0e5739dc308dc5442c98f7e2d56cf.jpg"]

async def populate_schema():
    # async_session=app.state.session
    if async_session is None:
        raise RuntimeError("app.state.async_session is not initialized!")
    async with async_session() as session:
        try:
            users=[User(name=names[i],email=emails[i],password_hash=hash_passwords[i],avatar=avatar_img_links[i]) for i in range(len(emails))]
            session.add_all(users)
            await session.commit()
        except IntegrityError:
            print("Users already exist, skipping user insert.")
            await session.rollback() #**is it necessary to use rollback , won't it automatically rollback
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("USER[0] -->",users[0])
        usr0=users[0]
        print("USER [0] id -->",usr0.id)

        users = [{ "id": user.id, "name": user.name } for user in users]

        try:
           versions=[Versions(vname=v) for v in versions_list]
           session.add_all(versions)
           await session.commit() 
        except IntegrityError:
            print("Versions already exist, skipping version insert.")
            await session.rollback()
        result = await session.execute(select(Versions))
        versions = result.scalars().all()
        versions = [{ "id": version.id, "vname": version.vname } for version in versions]
        
        try:
            user_versions=[UserVersions(user_id=users[0]["id"],version_id=versions[i]["id"]) for i in range(5)
            ]+[UserVersions(user_id=users[1]["id"],version_id=versions[3+i]["id"]) for i in range(4)]
            session.add_all(user_versions)
            await session.commit()
        except IntegrityError:
            print("User-Version relationships already exist, skipping insert.")
            await session.rollback()
        result = await session.execute(select(UserVersions))
        user_versions = result.scalars().all()

        try:
            result = await session.execute(select(Goals))
            goals = result.scalars().all()
            if not goals :
                goals=[Goals(user_id=users[0]["id"],version_id=versions[i]["id"],title=f'Achieve mastery in {versions[i]["vname"]}') for i in range(5)
                ]+[Goals(user_id=users[1]["id"],version_id=versions[3+i]["id"],title=f'Achieve mastery in {versions[i+3]["vname"]}') for i in range(3)]
                session.add_all(goals)
                await session.commit()
        except IntegrityError:
            print("Goals already exist, skipping goal insert.")
            await session.rollback()
        if goals:
            goals=goals
        else:
            result = await session.execute(select(Goals))
            goals = result.scalars().all()
        print("goals",goals)
        

        try:
            frosties=[Frosties(user_id=users[i]["id"],title=f"Cool Invention {i}",item_image=frost_img_links[i],
                               price=5000+500*i) for i in range(3)
                               ]+[Frosties(user_id=users[i]["id"],title=f"Cool Invention {i+3}",item_image=frost_img_links[i+3],
                                          price=6000+500*i) for i in range(2)]
            session.add_all(frosties)
            await session.commit()
        except IntegrityError:
            print("frosties already exist, skipping frost things insert.")
            await session.rollback()

        result = await session.execute(select(Frosties))
        frosties = result.scalars().all()
        frosties=[{ "id": frost.id, "user_id": frost.user_id,"title":frost.title } for frost in frosties]

        try:
            res=await session.execute(select(orders))
            order_exists=res.scalars().all()
            if not order_exists:
               orders_data = [orders(buyer_id=users[0]["id"]) for i in range(3)]
               session.add_all(orders_data)
               await session.commit()
        except IntegrityError:
            print("orders already exist, skipping orders insert.")
            await session.rollback()
        if order_exists:
            orders_data=order_exists
        else:
            result = await session.execute(select(orders))
            orders_data = result.scalars().all()
        orders_data=[{ "id": order.id,"buyer_id":order.buyer_id } for order in orders_data]
       

        try:
            orderitems_data = [orderitems(order_id=orders_data[0]["id"],frost_id=frosties[1]["id"])
                            ]+[orderitems(order_id=orders_data[1]["id"],frost_id=frosties[2]["id"])
                            ]+[orderitems(order_id=orders_data[2]["id"],frost_id=frosties[4]["id"])]

            session.add_all(orderitems_data)
            await session.commit()
        except IntegrityError:
            print("orderitems already exist, skipping orderitems insert.")
            await session.rollback()

        try:
            connections_data = [connections(sender_id=users[0]["id"],receiver_id=users[i+1]["id"]) for i in range(2)]
            session.add_all(connections_data)
            await session.commit()
        except IntegrityError:
            print("connections already exist, skipping connections insert.")
            await session.rollback()

        result = await session.execute(select(connections))
        connections_data = result.scalars().all()
        connections_data=[{ "sender_id": conn.sender_id, "receiver_id":conn.receiver_id } for conn in connections_data]

        try:
            followers_data = [followers(follower_id=conn["sender_id"],followed_id=conn["receiver_id"])for conn in connections_data
                              ]+[followers(follower_id=conn["receiver_id"],followed_id=conn["sender_id"])for conn in connections_data]
            session.add_all(followers_data)
            await session.commit()
        except IntegrityError:
            print("followers already exist, skipping followers insert.")
            await session.rollback()


async def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async with app.router.lifespan_context(app):
            await populate_schema()
    finally:
        loop.close()
        

if __name__ == "__main__":
    asyncio.run(main())
    print("Sample users seeded successfully!")
    



    