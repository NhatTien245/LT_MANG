
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
import base64
import pdfplumber

from os.path import basename
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import pdfplumber
from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError

from models import db, User, EncryptedEmail, EncryptForward
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, EncryptedEmail, EncryptForward, ConnectAES
from bs4 import BeautifulSoup
from flask_mail import Mail
from flask_socketio import SocketIO, emit
from flask_cors import CORS  # Import CORS
from utils import (
    generate_keys,
    serialize_keys,
    rsa_encrypt,
    rsa_decrypt,
    aes_encrypt,
    aes_decrypt,
    create_signature,
    generate_aes_key,
    generate_aes_key_from_password,
    encrypt_with_password,
    decrypt_with_password
)
import os
import random
import string

# Khởi tạo ứng dụng Flask
app = Flask(__name__)


CORS(app)  # Cho phép tất cả các nguồn kết nối đến server Flask

socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả các origin kết nối đến

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_encryption.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=100)
app.secret_key = os.urandom(24)

# Cấu hình SMTP email (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ikon1605@gmail.com'  # Địa chỉ email của bạn
app.config['MAIL_PASSWORD'] = 'iyyo oxhg cnji epfm'  # Mật khẩu email của bạn

mail = Mail(app)
db.init_app(app)

# Hàm tạo mã token ngẫu nhiên
def generate_token(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length)) # Tạo mã gồm chữ hoa và số

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import smtplib

def send_reset_email(user_email, token):
    msg = MIMEMultipart()

    # Đặt người gửi với mã hóa UTF-8
    sender_name = Header('Tên Người Gửi', 'utf-8').encode()
    msg['From'] = formataddr((sender_name, app.config['MAIL_USERNAME']))
    msg['To'] = user_email

    # Đặt tiêu đề với mã hóa UTF-8
    subject = Header("Mã xác nhận khôi phục mật khẩu", 'utf-8').encode()
    msg['Subject'] = subject

    # Nội dung email (sử dụng UTF-8)
    body = f"Mã xác nhận để khôi phục mật khẩu của bạn là: {token}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Gửi email
    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.ehlo()  # Bắt đầu giao thức giao tiếp với máy chủ
            server.starttls()  # Bảo mật kết nối
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

            # Chuyển đổi `msg` thành chuỗi và đảm bảo mã hóa UTF-8
            server.sendmail(app.config['MAIL_USERNAME'], user_email, msg.as_string().encode('utf-8'))
            print(f"Đã gửi mã xác nhận đến {user_email}")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        
# Danh sách các tên miền email được phép
ALLOWED_DOMAINS = ['@UTH.com', '@UTH.org']

CORS(app)  # Cho phép tất cả các nguồn kết nối đến server Flask

socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả các origin kết nối đến

with app.app_context():
    db.create_all()

# Trang chủ
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('inbox'))
    return render_template('index.html')




# Chức năng quên mật khẩu
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email_primary = request.form['email']       # Primary email input
        email_backup = request.form['email_backup'] # Backup email input

        # Fetch user by primary email and validate the backup email
        user = User.query.filter_by(email=email_primary, backup_email=email_backup).first()

        if user:
            # Generate token and send reset email if backup email is correct
            token = generate_token()
            session['reset_token'] = token
            session['reset_email'] = email_backup
            send_reset_email(email_backup, token)  # Send email to backup email
            return jsonify(success=True, message="Mã xác nhận đã được gửi đến email dự phòng của bạn.")
        else:
            return jsonify(success=False, message="Email chính hoặc email dự phòng không hợp lệ.")

    return render_template('forgot_password.html')

# Chức năng thay đổi mật khẩu
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        token = request.form['token']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra token và email trong session
        if 'reset_token' in session and 'reset_email' in session:
            reset_email = session['reset_email']  # Lấy email từ session để dễ kiểm tra
            print(f"Email trong session: {reset_email}")  # Log email để kiểm tra
            if session['reset_token'] == token:  # Kiểm tra token
                if new_password == confirm_password:  # Kiểm tra mật khẩu mới và xác nhận mật khẩu
                    # Tìm người dùng theo backup_email thay vì email
                    user = User.query.filter_by(backup_email=reset_email).first()
                    if user:
                        # Băm mật khẩu mới và cập nhật vào cơ sở dữ liệu
                        hashed_password = generate_password_hash(new_password)
                        user.password = hashed_password
                        db.session.commit()

                        # Xóa thông tin trong session
                        session.pop('reset_token', None)
                        session.pop('reset_email', None)

                        return jsonify(success=True, message="Mật khẩu đã được thay đổi thành công.")
                    else:
                        print(f"Không tìm thấy người dùng với email dự phòng: {reset_email}")  # Log lỗi chi tiết
                        return jsonify(success=False, message="Không tìm thấy người dùng.")
                else:
                    return jsonify(success=False, message="Mật khẩu không khớp.")
            else:
                return jsonify(success=False, message="Mã xác nhận không hợp lệ.")
        else:
            return jsonify(success=False, message="Phiên làm việc không hợp lệ hoặc đã hết hạn.")

    return render_template('reset_password.html')

