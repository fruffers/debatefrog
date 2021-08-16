from app import app
import mysql.connector

# database
database = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "debatefrog"
)
dbcursor = database.cursor(buffered=True)