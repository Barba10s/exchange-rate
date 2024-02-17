import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_db():
    try:
        connection = psycopg2.connect(user="DB_USER",
                                      password="DB_PASSWORD",
                                      host="DB_HOST",
                                      port="DB_PORT")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE currency_database")
    except (Exception, Error) as error:
        print("Ошибка при работе PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def connect_to_db():
    connection = psycopg2.connect(user="DB_USER",
                                  password="DB_PASSWORD",
                                  host="DB_HOST",
                                  port="DB_PORT",
                                  database="DB_NAME")
    return connection


def create_currencies_table():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS currencies 
                        (id int PRIMARY KEY NOT NULL,
                        code VARCHAR(3) NOT NULL,
                        fullname VARCHAR(30) NOT NULL,
                        sign VARCHAR(3) NOT NULL)''')

        cursor.execute('''
            CREATE UNIQUE INDEX unique_code_idx ON currencies (code)
        ''')
        connection.commit()
        print("Таблица создана")
    except (Exception, Error) as error:
        print("Ошибка при работе PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def create_exchange_rates_table():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS exchangerates 
                        (id int PRIMARY KEY NOT NULL,
                        baseCurrencyId INTEGER REFERENCES currencies(id),
                        targetCurrencyId INTEGER REFERENCES currencies(id),
                        rate DOUBLE PRECISION NOT NULL)''')

        connection.commit()
        print("Таблица создана")
    except (Exception, Error) as error:
        print("Ошибка при работе PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def insert_currencies_data():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute('''
                        INSERT INTO currencies (id, code, fullname, sign) VALUES
                        (1, 'RUB', 'Russian Ruble', '₽'),
                        (2, 'USD', 'US Dollar', '＄'),
                        (3, 'CNY', 'Yuan Renminbi', '¥'),
                        (4, 'GBP', 'Pound Sterling', '£'),
                        (5, 'TRY', 'Turkish Lira', '₤')''')

        connection.commit()
        print("Таблица создана")
    except (Exception, Error) as error:
        print("Ошибка при работе PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def insert_exchange_rates_data():
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute(
                       '''
                           INSERT INTO exchangerates (id, baseCurrencyId, targetCurrencyId, rate) VALUES
                           (1, 1, 2, 0.011), (2, 1, 3, 0.079),
                           (3, 1, 4 , 0.008), (4, 1, 5, 0.336),                  
                           (5, 2, 1, 90.89), (6, 2, 3, 7.25),
                           (7, 2, 4, 0.793), (8, 2, 5, 30.56),
                           (9, 3, 1, 12.54), (10, 3, 2, 0.137),
                           (11, 3, 4, 0.109), (12, 3, 5, 4.22),
                           (13, 4, 1, 114.57), (14, 4, 2, 1.26),
                           (15, 4, 3, 9.14), (16, 4, 5, 38.52),
                           (17, 5, 1, 2.97), (18, 5, 2, 0.032),
                           (19, 5, 3, 0.237), (20, 5, 4, 0.025)''')

        connection.commit()
        print("Таблица создана")
    except (Exception, Error) as error:
        print("Ошибка при работе PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

create_db()
create_currencies_table()
create_exchange_rates_table()
insert_currencies_data()
insert_exchange_rates_data()