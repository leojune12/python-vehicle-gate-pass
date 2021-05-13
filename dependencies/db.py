import mysql.connector
import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

try:
    db = mysql.connector.connect(
        host=config["DB_HOST"],
        user=config["DB_USERNAME"],
        password=config["DB_PASSWORD"],
        database=config["DB_DATABASE"]
    )
    db_status = True
except:
    print("Database error. Please run again.")
    db_status = False

def check_driver(rfid, log_type):
    selectCursor = db.cursor(dictionary=True)

    selectSql = "SELECT * FROM drivers where rfid = '" + rfid + "'"

    selectCursor.execute(selectSql)

    drivers = selectCursor.fetchall()

    if len(drivers):
        log_driver(drivers[0], log_type)
        print("Logged successfully")
    else:
        print("Unknown driver")


def log_driver(driver, log_type):
    now = datetime.datetime.now()
    logSql = "INSERT INTO logs (driver_id, log_type_id, time, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)"
    value = (driver["id"], log_type, now, now, now)

    logCursor = db.cursor()
    logCursor.execute(logSql, value)
    db.commit()
