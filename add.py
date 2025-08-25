
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
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

