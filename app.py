import os 
import psycopg2
from dotenv import load_dotenv 
from flask import Flask, request

# enkripsi
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return ct_bytes.hex()

def decrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    pt = unpad(cipher.decrypt(bytes.fromhex(data)), AES.block_size).decode('utf-8')
    return pt

# key
key = get_random_bytes(16)

# database
CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);"
)

INSERT_USERS_RETURN_ID = "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;"

SELECT_USER_BY_ID = """
SELECT id, username, password FROM users WHERE id = %s;
"""

DELETE_USER_BY_ID = """
DELETE FROM users WHERE id = %s;
"""

SELECT_ALL_USERS = "SELECT * FROM users"

UPDATE_USER_BY_ID = """
UPDATE users
SET username = %s, password = %s
WHERE id = %s;
"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url);

# create
@app.post("/api/users")
def create_users():
    data = request.get_json()
    username = data["username"]
    password = encrypt_data(data["password"], key)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(INSERT_USERS_RETURN_ID, (username,password))
            user_id = cursor.fetchone()[0]
    return {"id" : user_id, "message" : f"users {username} berhasil dibuat"}, 201
    

# menampilkan satu user
@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_BY_ID, (user_id,))
            user = cursor.fetchone()
            if user is None:
                return {"message" : f"user dengan id {user_id} tidak ditemukan"}, 404
    return {"id" : user_id, "username" : user[1], "password" : user[2]}, 200

# meghapus user
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_BY_ID, (user_id,))
            user = cursor.fetchone()
            if user is None:
                return {"message" : f"user dengan id {user_id} tidak ditemukan"}, 404

            cursor.execute(DELETE_USER_BY_ID, (user_id,))
            connection.commit()
    return {"message" : f"user dengan id {user_id} berhasil dihapus"}, 200

# mengambil seluruh user
@app.get("/api/users/")
def get_users():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_USERS)
            users = cursor.fetchall()
            if users is None:
                return {"message" : "tidak ada user yang tersedia"}, 404

    return {"message" : "daftar user yang tersedia", "users" :  users}, 200


# update
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_BY_ID, (user_id,))
            user = cursor.fetchone()
            if user is None:
                return {"message" : f"user dengan id {user_id} tidak ditemukan"}, 404

            username = data['username']
            password = data['password']

            cursor.execute(UPDATE_USER_BY_ID, (username, password, user_id))
            connection.commit()
    return {"message" : f"user dengan id {user_id} berhasil diupdate"}, 200