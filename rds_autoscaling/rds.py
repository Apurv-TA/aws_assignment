import configparser
import mysql.connector


config = configparser.ConfigParser()
config.read("config.ini")


mydb = mysql.connector.connect(
    host = config["mysql"]["host"],
    user = config["mysql"]["user"],
    password = config["mysql"]["password"],
    database = config["mysql"]["database"]
)
cursor = mydb.cursor()


def all_db():
    cursor.execute("select * from logs")

    db = []
    for x in cursor:
        db.append(x)

    return db


def update_df(msg):
    cursor.execute(f"insert into logs(access_time, message) values(now(), '{msg}')")
    mydb.commit()
