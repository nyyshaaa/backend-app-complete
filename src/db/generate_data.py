# import random , uuid, time
# from datetime import datetime , timedelta
# from faker import Faker
# from src.db.schema import User, Versions, UserVersions, Goals, Frosties, likes, orders, orderitems, connections, followers
# from src.db.data_gen_utils import versions_list,product_titles_list
# from src.config import configSettgs
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import IntegrityError
# from src.db.schema import orderstatus,connstatus

# fake=Faker()

# engine=create_engine(configSettgs.DB_SYNC_URL)
# Session=sessionmaker(bind=engine)
# session=Session()

# BATCH_SIZE=10_000

# versions_data = [{
#     "vname": version,
#     "created_at": datetime.now(),
#     "updated_at": datetime.now()
# } for version in versions_list]

# # start_time=time.time()

# # session.bulk_insert_mappings(Versions,versions_data)
# # session.commit()

# # end_time=time.time()

# # print(f'time taken to insert versions: {versions_data} -- {end_time-start_time} time ')

# versions_db=session.query(Versions).all()
# version_ids=[v.id for v in versions_db]

# total_users = 50_000 
# # users_to_insert = []
# # counter=0
# # for i in range(total_users):
# #     user_entry = {
# #         "name": fake.name(),
# #         "email": fake.unique.email(),
# #         "password_hash": fake.sha256(),  # Simulated hash for demo purposes
# #         "about": fake.text(max_nb_chars=200),
# #         "avatar": "https://res.cloudinary.com/dxgc847bt/image/upload/v1741524748/profile_default_fpie1f.jpg",  # Default image URL
# #         "created_at": datetime.now(),
# #         "updated_at": datetime.now()
# #     }
    
# #     users_to_insert.append(user_entry)
# #     counter+=1
# #     if counter >= BATCH_SIZE:
# #         start_time=time.time()
# #         session.bulk_insert_mappings(User, users_to_insert)
# #         session.commit()
# #         end_time_time=time.time()
# #         print(f"Inserted {i+1} users... in {end_time-start_time} time")
# #         users_to_insert = []
# #         counter=0
# # if users_to_insert:
# #     start_time=time.time()
# #     session.bulk_insert_mappings(User, users_to_insert)
# #     session.commit()
# #     end_time=time.time()
# #     print(f"Inserted remaining users in {end_time-start_time} ")


# user_ids = [u.id for u in session.query(User.id).yield_per(1000)]


# #-------------------------------------
# # Insert userversions(many to many )

# existing_userversions = {(uv.user_id, uv.version_id) for uv in session.query(UserVersions.user_id, UserVersions.version_id).yield_per(1000)}
# print(f"Fetched {len(existing_userversions)} existing userversions.")

# # user_versions_data = []
# # counter=0
# # for user_id in user_ids:
# #     # Each user gets 1 or 2 versions
# #     num_versions = random.randint(1,2)
# #     assigned_versions = random.sample(version_ids, num_versions)
# #     for ver_id in assigned_versions:
# #         if(user_id,ver_id) not in existing_userversions:
# #             user_versions_data.append({"user_id": user_id, "version_id": ver_id})
    
# #     counter+=1
# #     # Batch commit if needed
# #     if counter >= BATCH_SIZE:
# #         try:
# #             start_time = time.time()
# #             session.bulk_insert_mappings(UserVersions, user_versions_data)
# #             session.commit()
# #             end_time = time.time()
# #             print(f"Inserted {len(user_versions_data)} userversions in {end_time - start_time} seconds.")
# #         except IntegrityError as e:
# #             session.rollback()
# #             print(f"IntegrityError encountered while inserting userversions: {e}")
# #         finally:
# #             user_versions_data = []
# #             counter = 0
# # if user_versions_data:
# #     try:
# #         session.bulk_insert_mappings(UserVersions, user_versions_data)
# #         session.commit()
# #     except IntegrityError as e:
# #         session.rollback()
# #         print(f"IntegrityError encountered while inserting remaining userversions: {e}")

# # goals_data = []
# # counter=0
# # for user_id in user_ids:
# #     num_goals = random.randint(1, 2)
# #     for _ in range(num_goals):
# #         goal_entry = {
# #             "user_id": user_id,
# #             "version_id": random.choice(version_ids),
# #             "title": fake.sentence(nb_words=6),
# #             "description": fake.text(max_nb_chars=300),
# #             "deadline": datetime.now().date() + timedelta(days=random.randint(30, 365)),
# #             "created_at": datetime.now(),
# #             "updated_at": datetime.now(),
# #         }
# #         goals_data.append(goal_entry)
# #     counter+=1
# #     if counter >= BATCH_SIZE:
# #         try:
# #             start_time = time.time()
# #             session.bulk_insert_mappings(Goals, goals_data)
# #             session.commit()
# #             end_time = time.time()
# #             print(f"Inserted {len(goals_data)} goals in {end_time - start_time} seconds.")
# #         except IntegrityError as e:
# #             session.rollback()
# #             print(f"IntegrityError encountered while inserting goals: {e}")
# #         finally:
# #             goals_data = []
# #             counter = 0
# # if goals_data:
# #     try:
# #         session.bulk_insert_mappings(Goals, goals_data)
# #         session.commit()
# #     except IntegrityError as e:
# #         session.rollback()
# #         print(f"IntegrityError encountered while inserting remaining goals: {e}")

# total_products = 50000 

# # products_data = []
# # counter=0
# # for i in range(total_products):
# #     # Generate a base title from the list then append a unique UUID portion
# #     base_title = f"{random.choice(product_titles_list)}"
# #     unique_title = f"{base_title}{uuid.uuid4().hex[:8]}"
# #     product_entry = {
# #         "user_id": random.choice(user_ids),  # Assign a random creator from inserted users
# #         "title": unique_title,
# #         "description": fake.text(max_nb_chars=300),
# #         "item_image": "https://res.cloudinary.com/dxgc847bt/image/upload/v1741524759/product_default_x37sfe.jpg",  # Default product image URL
# #         "qty": random.randint(1, 10),
# #         "price": float(fake.pydecimal(left_digits=2, right_digits=2, positive=True)),
# #         "created_at": datetime.now(),
# #         "updated_at": datetime.now(),
# #     }
# #     products_data.append(product_entry)
# #     counter+=1
# #     if counter >= BATCH_SIZE:
# #         try:
# #             start_time = time.time()
# #             session.bulk_insert_mappings(Frosties, products_data)
# #             session.commit()
# #             end_time = time.time()
# #             print(f"Inserted currrent batch  products in {end_time - start_time} seconds.")
# #         except IntegrityError as e:
# #             session.rollback()
# #             print(f"IntegrityError encountered while inserting products: {e}")
# #         finally:
# #             products_data = []
# #             counter = 0
# # if products_data:
# #     try:
# #         session.bulk_insert_mappings(Frosties, products_data)
# #         session.commit()
# #     except IntegrityError as e:
# #         session.rollback()
# #         print(f"IntegrityError encountered while inserting remaining products: {e}")

# frosty_ids = [f.id for f in session.query(Frosties.id).yield_per(1000)]

# # total_likes = 100000  
# # likes_data = []
# # counter=0
# # for i in range(total_likes):
# #     like_entry = {
# #         "user_id": random.choice(user_ids),
# #         "frost_id": random.choice(frosty_ids),
# #         "created_at": datetime.now(),
# #     }
# #     likes_data.append(like_entry)
# #     counter+=1
# #     if counter >= BATCH_SIZE:
# #         try:
# #             start_time=time.time()
# #             session.bulk_insert_mappings(likes, likes_data)
# #             session.commit()
# #             end_time=time.time()
# #             print(f"Inserted current bacth likes... in {end_time-start_time} time")
# #         except IntegrityError as e:
# #             session.rollback()
# #             print(f"IntegrityError encountered {e}")
# #         finally:
# #             likes_data = []
# #             counter=0
# # if likes_data:
# #     try:
# #         session.bulk_insert_mappings(likes, likes_data)
# #         session.commit()
# #     except IntegrityError as e:
# #             session.rollback()
# #             print(f"IntegrityError encountered {e}")



# total_orders = 50000  
# orders_data = []
# counter=0
# for i in range(total_orders):
#     order_entry = {
#         "buyer_id": random.choice(user_ids),
#         "created_at": datetime.now(),
#         "status": random.choice(list(orderstatus)).name,  
#     }
#     orders_data.append(order_entry)
#     counter+=1
#     if len(orders_data) >= BATCH_SIZE:
#         try:
#             start_time=time.time()
#             session.bulk_insert_mappings(orders, orders_data)
#             session.commit()
#             end_time=time.time()
#             print(f"Inserted current batch orders... in {end_time-start_time} time")
#         except IntegrityError as e:
#             session.rollback()
#             print(f"IntegrityError encountered {e}")
#         finally:
#             orders_data = []
#             counter=0
# if orders_data:
#     try:
#         session.bulk_insert_mappings(orders, orders_data)
#         session.commit()
#     except IntegrityError as e:
#         session.rollback()
#         print(f"IntegrityError encountered {e}")


# order_ids = [o.id for o in session.query(orders.id).yield_per(1000)]

# # ----------------------------------------------------
# # Insert OrderItems (each order item references an order and a frosty)

# total_order_items = 80000 
# order_items_data = []
# counter=0
# for i in range(total_order_items):
#     order_item_entry = {
#         "order_id": random.choice(order_ids),
#         "frost_id": random.choice(frosty_ids),
#         "quantity": random.randint(1, 5),
#         "created_at": datetime.now(),
#     }
#     order_items_data.append(order_item_entry)
#     counter+=1
#     if counter >= BATCH_SIZE:
#         try:
#             start_time=time.time()
#             session.bulk_insert_mappings(orderitems, order_items_data)
#             session.commit()
#             end_time=time.time()
#             print(f"Inserted current batch  orderitems... in {end_time-start_time} time")
#         except IntegrityError as e:
#             session.rollback()
#             print(f"IntegrityError encountered {e}")
#         finally:
#             order_items_data = []
#             counter=0
# if order_items_data:
#     try:
#         session.bulk_insert_mappings(orderitems, order_items_data)
#         session.commit()
#     except IntegrityError as e:
#         session.rollback()
#         print(f"IntegrityError encountered {e}")

# # ----------------------------------------------------
# # Insert Connections (friend connections between users)

# total_connections = 50000  
# connections_data = []
# counter=0
# for i in range(total_connections):
#     sender = random.choice(user_ids)
#     receiver = random.choice(user_ids)
#     if sender != receiver:
#         connection_entry = {
#             "sender_id": sender,
#             "receiver_id": receiver,
#             "status": random.choice(list(connstatus)).name,
#         }
#         connections_data.append(connection_entry)
#         counter+=1
#         if len(connections_data) >= BATCH_SIZE:
#             try:
#                 start_time=time.time()
#                 session.bulk_insert_mappings(connections, connections_data)
#                 session.commit()
#                 end_time=time.time()
#                 print(f"Inserted current batch connections... in {end_time-start_time} time")
#             except IntegrityError as e:
#                 session.rollback()
#                 print(f"IntegrityError encountered {e}")
#             finally:
#                 connections_data = []
#                 counter=0
# if connections_data:
#     try:
#         session.bulk_insert_mappings(connections, connections_data)
#         session.commit()
#     except IntegrityError as e:
#             session.rollback()
#             print(f"IntegrityError encountered {e}")



