import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def create_default_database(database_url: str):
    from sqlalchemy import create_engine

    try:
        database_url = database_url.replace("/allocation", "")
        engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
        conn = engine.connect()

        conn.execute("CREATE DATABASE allocation")
        conn.close()
    except Exception as err:
        print(err)


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8000
    return f"http://{host}:{port}"
