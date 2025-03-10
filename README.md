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
