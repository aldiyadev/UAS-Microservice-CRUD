
import os
import Crypto
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import psycopg2

Crypto
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_data(data, key):
    if not isinstance(data, str) or len(data) == 0:
        raise ValueError("Data must be a non-empty string")

    cipher = AES.new(key, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return ct_bytes.hex()

def decrypt_data(data, key):
    if not isinstance(data, str) or len(data) % 2 != 0:
        raise ValueError("Data must be a hexadecimal string with even number of digits")

    cipher = AES.new(key, AES.MODE_ECB)
    pt = unpad(cipher.decrypt(bytes.fromhex(data)), AES.block_size).decode('utf-8')
    return pt


key = get_random_bytes(16)

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
connection = psycopg2.connect(url)


with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    for user in users:
        encrypted_password = encrypt_data(user[2], key)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (encrypted_password, user[0]))

    connection.commit()

with connection.cursor() as cursor:
    cursor.execute(CREATE_USERS_TABLE)
    connection.commit()


@app.route('/api/login', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    encrypted_password = encrypt_data(password, key)

    with connection.cursor() as cursor:
        cursor.execute(INSERT_USERS_RETURN_ID, (username, encrypted_password))
        user_id = cursor.fetchone()[0]
        connection.commit()

    return jsonify({'id': user_id}), 201


@app.route('/api/login', methods=['GET'])
def read_users():
    with connection.cursor() as cursor:
        cursor.execute(SELECT_ALL_USERS)
        users = cursor.fetchall()

        decrypted_users = []
        for user in users:
            decrypted_password = decrypt_data(user[2], key)
            decrypted_users.append({'id': user[0], 'username': user[1], 'password': decrypted_password})

        return jsonify(decrypted_users)


@app.route('/api/login/<int:user_id>', methods=['GET'])
def read_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_USER_BY_ID, (user_id,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        decrypted_password = decrypt_data(user[2], key)
        return jsonify({'id': user[0], 'username': user[1], 'password': decrypted_password})


@app.route('/api/login/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data['username']
    password = data['password']

    encrypted_password = encrypt_data(password, key)

    with connection.cursor() as cursor:
        cursor.execute(UPDATE_USER_BY_ID, (username, encrypted_password, user_id))
        connection.commit()

        return jsonify({'message': 'User updated'})


@app.route('/api/login/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute(DELETE_USER_BY_ID, (user_id,))
        connection.commit()

        return jsonify({'message': 'User deleted'})

if __name__ == '__main__':
    app.run(debug=True)