from typing import List

from fastapi import FastAPI, Response, HTTPException
import json
import psycopg2
from psycopg2.extras import DictCursor
from pydantic import BaseModel, Field

app = FastAPI()
conn = psycopg2.connect(dbname="DB_NAME", user="USER_NAME",
                        password="DB_PASSWORD", host="HOST", port="DB_PORT")


@app.on_event("shutdown")
def shutdown():
    conn.close()
    print("Закрыто соединение с БД")


class Currency(BaseModel):
    id: int
    code: str = Field(max_length=3)
    fullname: str
    sign: str


@app.get("/currencies")
def get_currencies():
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT* FROM currencies')
        records = cursor.fetchall()

        cursor.close()

        currencies_json = [dict(record) for record in records]
        return {"status": 200, "data": currencies_json}
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500, media_type="application/json")


@app.get("/currencies/{code}", response_model=Currency)
def get_concrete_currency(code: str):
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT* FROM currencies WHERE code = %s', (code,))
        record = cursor.fetchone()
        cursor.close()

        return Currency(**record)

    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500, media_type="application/json")


@app.post("/currencies")
def add_currency(id: int, code: str, fullname: str, sign: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO currencies (id, code, fullname, sign) VALUES (%s, %s, %s, %s) RETURNING id, code, fullname, sign",
            (id, code, fullname, sign))
        conn.commit()
        record = cursor.fetchone()

        if record:
            return {"status": 200,
                    "data": {"id": record[0], "code": record[1], "fullname": record[2], "sign": record[3]}}
        else:
            raise HTTPException(status_code=400, detail="Не удалось получить информацию о вновь добавленной валюте")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ExchangeRates(BaseModel):
    id: int
    basecurrencyid: Currency
    targetcurrencyid: Currency
    rate: float


@app.get("/exchangeRates", response_model=List[ExchangeRates])
def get_exchange_rates():
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('''
                SELECT cr.id,
                       cr.rate,
                       c1.id AS base_currency_id,
                       c1.fullname AS base_currency_name,
                       c1.code AS base_currency_code,
                       c1.sign AS base_currency_sign,
                       c2.id AS target_currency_id,
                       c2.fullname AS target_currency_name,
                       c2.code AS target_currency_code,
                       c2.sign AS target_currency_sign
                FROM exchangerates cr
                INNER JOIN currencies c1 ON cr.basecurrencyid = c1.id
                INNER JOIN currencies c2 ON cr.targetcurrencyid = c2.id
            ''')
        records = cursor.fetchall()
        cursor.close()

        conversion_rates = []
        for record in records:
            conversion_rate = ExchangeRates(
                id=record["id"],
                basecurrencyid=Currency(
                    id=record["base_currency_id"],
                    code=record["base_currency_code"],
                    fullname=record["base_currency_name"],
                    sign=record["base_currency_sign"]
                ),
                targetcurrencyid=Currency(
                    id=record["target_currency_id"],
                    code=record["target_currency_code"],
                    fullname=record["target_currency_name"],
                    sign=record["target_currency_sign"]
                ),
                rate=record["rate"]
            )
            conversion_rates.append(conversion_rate.dict())

        return conversion_rates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exchangeRate/{base_code,target_code}")
def get_exchange_rate(base_code: str, target_code: str):
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('''
                        SELECT cr.id,
                           c1.id AS base_currency_id,
                           c1.fullname AS base_currency_name,
                           c1.code AS base_currency_code,
                           c1.sign AS base_currency_sign,
                           c2.id AS target_currency_id,
                           c2.fullname AS target_currency_name,
                           c2.code AS target_currency_code,
                           c2.sign AS target_currency_sign,
                           cr.rate
                    FROM exchangerates cr
                    INNER JOIN currencies c1 ON cr.basecurrencyid = c1.id
                    INNER JOIN currencies c2 ON cr.targetcurrencyid = c2.id
                    WHERE c1.code = %s and c2.code = %s
                        ''', (base_code, target_code))
        record = cursor.fetchone()
        cursor.close()

        if record:
            exchange_rate_data = {
                "id": record["id"],
                "baseCurrency": {
                    "id": record["base_currency_id"],
                    "name": record["base_currency_name"],
                    "code": record["base_currency_code"],
                    "sign": record["base_currency_sign"]
                },
                "targetCurrency": {
                    "id": record["target_currency_id"],
                    "name": record["target_currency_name"],
                    "code": record["target_currency_code"],
                    "sign": record["target_currency_sign"]
                },
                "rate": record["rate"]
            }
            return exchange_rate_data
        else:
            return {"message": "Exchange rate not found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
