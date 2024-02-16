# Detail
- Nama : Aldi Yahya Awaluddin
- NIM : 220401010143

## Membuat virtual environments
- python -m venv venv
- venv/Scripts/activate

## Install dependencies
pip install -r requirements.txt

## Menjalankan Program
flask run

----------------------------

## api test
Menghubungkan dengan PostgreSQL >> edit file .env

<ul>
  <li>Melihat user yang sudah terdaftar : http://127.0.0.1:5000/api/login | <b>GET</b></li>
  <li>Membuat user : http://127.0.0.1:5000/api/login | <b>POST</b></li>
  <li>Update user : http://127.0.0.1:5000/api/login/{id} | <b>PUT</b></li>
  <li>Lihat satu user : http://127.0.0.1:5000/api/login/{id} | <b>GET</b></li>
  <li>delete user : http://127.0.0.1:5000/api/login/{id} | <b>DELETE</b></li>
</ul>