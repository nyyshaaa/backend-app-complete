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

### Users api endpoints decision

```markdown
1. Create - via signup endpoint in auth router
2. Read - private view to owner and public for others
3. Read , Update , Delete endpoints same type
```

> /users/{user_id} with access token in header ,user_id in path parameter also compatible with public view , user_id needs a check with user_id of token's user_id to provide the private or public view
> /profile with access token not compatible with public view for read but straightforward,fits well with update and delete and no checks

> /users/{user_id} for public view separately , but how will user user_id be passed in frontend ?
> How will the token be retrieved ? users don't need to pass token anywhere , but for developmnet phase we need to pass token in headers? How it is really handled?
