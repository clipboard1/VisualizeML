import psycopg2
import json
import pandas as pd

CONFIG_FILE = "db_config.json"


def loadConfig():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        return {}


def saveConfig(config):
    if "password" in config:
        del config["password"]
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)


def connectToDatabase(params):
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        return conn, cursor
    except psycopg2.OperationalError as e:
        raise ValueError(f"Ошибка подключения к базе данных: {e}")
    except Exception as e:
        raise ValueError(f"Произошла ошибка при подключении к базе данных: {e}")


def getTableNames(cursor):
    try:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    except psycopg2.Error as e:
        raise ValueError(f"Ошибка получения списка таблиц: {e}")


def loadTableToDataFrame(cursor, tableName):
    try:
        query = f'SELECT * FROM "{tableName}"'
        cursor.execute(query)
        data = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=colnames)
        return df
    except psycopg2.Error as e:
        raise ValueError(f"Ошибка загрузки данных из таблицы: {e}")
