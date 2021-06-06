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
        if log_type == "1":
            print(drivers[0]["name"] + " - " + drivers[0]["rfid"] + " - time-in")
        elif log_type == "2":
            print(drivers[0]["name"] + " - " + drivers[0]["rfid"] + " - time-out")

        return True

    else:
        print("Unregistered Driver - " + str(rfid))

        return False


def log_driver(driver, log_type):
    now = datetime.datetime.now()
    logSql = "INSERT INTO logs (driver_id, log_type_id, time, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)"
    value = (driver["id"], log_type, now, now, now)

    logCursor = db.cursor()
    logCursor.execute(logSql, value)
    db.commit()
    
def get_last_scanned():
    print('get_last_scanned')
    lastScannedCursor = db.cursor(dictionary=True)

    lastScannedSql = "SELECT * FROM logs ORDER BY ID DESC LIMIT 1"

    lastScannedCursor.execute(lastScannedSql)

    last_log = lastScannedCursor.fetchone()
    
    if last_log:        
        driverCursor = db.cursor(dictionary=True)
        
        driverSql = "SELECT * FROM drivers where id = " + str(last_log['driver_id'])
        
        driverCursor.execute(driverSql)
        
        driver = driverCursor.fetchone()
        
        logTypeCursor = db.cursor(dictionary=True)
        
        logTypeSql = "SELECT * FROM log_types where id = " + str(last_log['log_type_id'])
        
        logTypeCursor.execute(logTypeSql)
        
        logType = logTypeCursor.fetchone()
        
        driverName = "Name: " + driver['name']
        
        driverRfid = "RFID: " + driver['rfid']
        
        driverPhoto = driver['photo']
        
        driverLogType = "Log Type: " + logType['log_type']
        
        driverLogTime = "Time: " + str(last_log['created_at'])
        
        return {'name' : driverName, 'rfid': driverRfid, 'photo': driverPhoto, 'log_type': driverLogType, 'time': driverLogTime}
    
    else:
        {'name' : 'No records yet', 'rfid': '', 'photo': '', 'log_type': '', 'time': ''}
        