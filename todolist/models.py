from datetime import timezone
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import mysql.connector # type: ignore

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class User_infor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    age = db.Column(db.Integer)
    c_class = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    address = db.Column(db.String(200))  # Thêm cột address
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="user_infor", uselist=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_name = db.Column(db.String(150))
    user_infor = db.relationship("User_infor", back_populates="user", uselist=False)
    files = db.relationship("File", back_populates="user")

    def __init__(self, email, password, user_name):
        self.email = email
        self.password = password
        self.user_name = user_name

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # idfile = db.Column(db.String(150), unique=True)  # Unique ID for the file
    filename = db.Column(db.String(150))
    filetype = db.Column(db.String(100))
    link = db.Column(db.String(200))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    file_id = db.Column(db.String(200))
    link_convert = db.Column(db.String(200))
    file_id_convert = db.Column(db.String(200))
    user = db.relationship("User", back_populates="files")

def find_file(name):
# Kết nối đến MySQL
    try:
        data1 = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tranvantu@294",
            database="data"
        )
        
        file_name = name
        cursor = data1.cursor()  
        sql = "SELECT file_name,file_type FROM files WHERE file_name Like %s"
        values = ('%'+file_name+'%',)
        cursor.execute(sql,values)
        myresult = cursor.fetchall()

        for x in myresult:
         print(x)
        return myresult
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
