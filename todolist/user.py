from math import e
from re import template
from flask import Blueprint, render_template, request, flash, session
from flask.helpers import url_for
from sqlalchemy.sql.expression import false
from werkzeug.utils import redirect
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from todolist import views
from .models import User, Note,User_infor
from flask import current_app

from . import db

user = Blueprint("user", __name__)
# user.permanent_session_lifetime = timedelta(minutes=1)
@user.route('/information', methods=["GET", "POST"])
@login_required
def information():
    if request.method == "POST":
        # Lấy dữ liệu từ form
        full_name = request.form.get("full_name")
        user_class = request.form.get("class")
        age = request.form.get("age")
        phone = request.form.get("phone")
        address = request.form.get("address")
        gender = request.form.get("gender")

        # Kiểm tra xem người dùng đã có thông tin chưa
        user_info = User_infor.query.filter_by(user_id=current_user.id).first()
        
        if user_info:
            # Cập nhật thông tin người dùng nếu đã có thông tin
            user_info.full_name = full_name
            user_info.c_class = user_class
            user_info.age = age
            user_info.phone = phone
            user_info.address = address
            user_info.gender = gender
            db.session.commit()
            flash("Information updated successfully!", category="success")
        else:
            # Nếu chưa có thông tin, tạo mới thông tin người dùng
            new_info = User_infor(
                full_name=full_name, 
                email=current_user.email, 
                age=age,
                c_class=user_class, 
                phone=phone,
                address=address, 
                gender=gender, 
                user_id=current_user.id
            )
            db.session.add(new_info)
            db.session.commit()
            flash("Information added successfully!", category="success")

        # Sau khi xử lý xong, quay lại trang thông tin người dùng
        return redirect(url_for("user.information"))
    
    # Hiển thị form nhập thông tin, lấy thông tin người dùng nếu đã có
    user_info = User_infor.query.filter_by(user_id=current_user.id).first()
    return render_template('information.html', user_info=user_info,user=current_user)

@user.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                session.permanent = True
                session["user_id"] = user.id
                current_app.logger.info(f"Session Permanent: {session.permanent}")
                current_app.logger.info(f"Session Lifetime: {current_app.permanent_session_lifetime}")
                login_user(user, remember=True)
                flash("Logged in success!", category="success")
                return redirect(url_for("views.home"))
            else:
                flash("Wrong password, please check again!", category="error")
        else:
            flash("User doesn't exist!", category="error")
    return render_template("login.html", user=current_user)


@user.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()
        # validate user
        if user:
            flash("User existed!", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(password) < 7:
            flash("Email must be greater than 7 characters.", category="error")
        elif password != confirm_password:
            flash("Password doesn not match!", category="error")
        else:
            password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(email, password, user_name)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("User created!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            except:
                "Error when create user!"
    return render_template("signup.html", user=current_user)


@user.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("user.login"))
