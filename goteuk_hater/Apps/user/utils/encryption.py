from cryptography.fernet import Fernet

# 암호화 키 생성
def generate_key():
    return Fernet.generate_key()

# 데이터 암호화
def encrypt_data(data, key):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# 데이터 복호화
def decrypt_data(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data