from flask import Flask, request
import hmac
import sqlite3

from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
import datetime

app = Flask(__name__)


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


def init_user_table():
    conn = sqlite3.connect('sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_item_table():
    with sqlite3.connect('sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "title TEXT NOT NULL,"
                     "category TEXT NOT NULL,"
                     "price INTEGER NOT NULL)")
    print("item table created successfully.")


init_user_table()
init_item_table()
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("sale.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 200
        return response


@app.route('/products/', methods=["POST"])
@jwt_required()
def create_blog():
    response = {}

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        date_created = datetime.datetime.now()

        with sqlite3.connect('sale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO item("
                           "title,"
                           "content,"
                           "date_created) VALUES(?, ?, ?)", (title, content, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product added successfully"
        return response


@app.route('/get-products/', methods=["GET"])
def get_blogs():
    response = {}
    with sqlite3.connect("sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM item")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_post(product_id):
    response = {}
    with sqlite3.connect("sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM item WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


# @app.route('/edit-product/<int:product_id>/', methods=["PUT"])
# @jwt_required()
# def edit_post(product_id):
#     response = {}
#
#     if request.method == "PUT":
#         with sqlite3.connect('sale.db') as conn:
#             incoming_data = dict(request.json)
#             put_data = {}
#
#             if incoming_data.get("title") is not None:
#                 put_data["title"] = incoming_data.get("title")
#                 with sqlite3.connect('sale.db') as conn:
#                     cursor = conn.cursor()
#                     cursor.execute("UPDATE item SET title =? WHERE id=?", (put_data["title"], product_id))
#                     conn.commit()
#                     response['message'] = "Update was successfully"
#                     response['status_code'] = 200
#             if incoming_data.get("content") is not None:
#                 put_data['content'] = incoming_data.get('content')
#
#                 with sqlite3.connect('sale.db') as conn:
#                     cursor = conn.cursor()
#                     cursor.execute("UPDATE item SET content =? WHERE id=?", (put_data["content"], product_id))
#                     conn.commit()
#
#                     response["content"] = "Content updated successfully"
#                     response["status_code"] = 200
#     return response


if __name__ == "__main__":
    app.debug = True
    app.run()


# https://dashboard.heroku.com/apps/limitless-citadel-50663/deploy/github