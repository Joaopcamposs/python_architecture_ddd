import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8001 if host == "localhost" else 8000
    return f"http://{host}:{port}"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63791 if host == "localhost" else 6379
    return dict(host=host, port=port)


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
