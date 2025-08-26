import os
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Signature import pkcs1_15
from typing import Optional

def generate_aes_key_from_password(password, salt):
    return PBKDF2(password, salt, dkLen=32, count=1000000)  # Tạo khóa AES từ mật khẩu người dùng

def encrypt_with_password(password, plaintext):
    salt = get_random_bytes(16)  # Tạo salt ngẫu nhiên
    key = generate_aes_key_from_password(password, salt) # Tạo khóa AES từ mật khẩu
    iv = get_random_bytes(16)  # Tạo IV ngẫu nhiên
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = plaintext + (16 - len(plaintext) % 16) * chr(16 - len(plaintext) % 16)
    ciphertext = cipher.encrypt(padded_text.encode())
    return base64.b64encode(salt + iv + ciphertext).decode() # Mã hóa Base64 cho salt, iv, và ciphertext để dễ lưu trữ

# Hàm giải mã AES (chế độ CBC) sử dụng mật khẩu người dùng
from Crypto.Cipher import AES
import base64


def decrypt_with_password(password, encrypted_data):
    data = base64.b64decode(encrypted_data)
    salt = data[:16]  # Extract the salt
    iv = data[16:32]  # Extract the IV
    ciphertext = data[32:]  # Extract the ciphertext

    # Generate the AES key from the password and salt
    key = generate_aes_key_from_password(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the ciphertext
    decrypted_data = cipher.decrypt(ciphertext)

    # Since we might be dealing with non-text data, avoid decoding directly
    # Check if the decrypted data can be a valid UTF-8 string or return as raw bytes
    try:
        decrypted_text = decrypted_data.decode('utf-8')
        padding_length = ord(decrypted_text[-1])
        return decrypted_text[:-padding_length]  # Remove padding
    except UnicodeDecodeError:
        # Return the raw decrypted binary data (in case it's not text)
        return decrypted_data
