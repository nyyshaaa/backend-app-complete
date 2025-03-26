In Progress...

> Virtual Environment Creation

> a python3 -m venv venv (venv python module , virtual environment name)
> b .\venv\Scripts\Activate
> c pip freeze > requirements.txt (to track the installed dependecies into a file requirements with correct versions,so easy to reinstall at once if and when needed later)

Will use browser as HTTP client or POSTMAN for making http requests requests to server

> 1.pip install fastapi
> 2.pip install "fastapi[standard]"

> To run the server cd to the folder contaning file for app instance initialisation
> --fastapi dev src/

> Create .env file for storing secret variables and add it in gitignore to be not included in publicly visible remote code repository.

> Create a configuration file to read environment variables using pydantic settings

> initialize alembic migrations for schema changes

> create a idempotent seed script for testing.
> $env:PYTHONPATH = (Get-Location)
> python src/db/schema_seed.py

> config.py file ---> 1. to read variables from .env(may contain credentials , passwords)

#### Orders Endpoints

1. POST /orders
2. GET /orders
   Returns a list of orders for the authenticated user (with filters/pagination as needed)
3. GET/orders/{order_id}
   Returns full details of a specific order , including it's order items
   4.PATCH /orders/{order_id}/cancel
   Allows a user to cancel an order if it's still pending
4. PATCH /orders/{ORDER_id}/return
   Allows a user to initiate a return ,amount will be refunded.

#### Test mode stripe Integration

1. pip install stripe
2. stripe lets you simulate creating real objects without the risk of affecting real transactions or moving actual money(test mode)
3. Use stripe's secret key on server side to authenticate api calls to stripe , must be kept confidential as it has full access to account.
4. Publishable key will be used on client side to tokenize credit card data before sending it to server
5. Calling stripe API in test mode doesn't require card data as input

   ![IMG_20250326_125314](https://github.com/user-attachments/assets/364852ac-8360-4ea1-9906-670a10b020d0)
   ![IMG20250326125025](https://github.com/user-attachments/assets/c0050e50-e4b3-4951-bc1c-25baf99c9515)
   ![IMG20250326125041](https://github.com/user-attachments/assets/69b55537-f490-4dae-854e-0ab3478a83a5)
   ![IMG20250326125104](https://github.com/user-attachments/assets/a7c5889f-7add-4e75-9291-e5bf8045f74c)




