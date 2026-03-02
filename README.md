# Configuration

## Virtual environment
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Alembic (database migrations)
```
$ alembic revision -m "revision description"
$ alembic upgrade head
```

## Running
```
$ source venv/bin/activate
$ fastapi dev main.py
```
