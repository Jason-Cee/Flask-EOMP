from flask import Flask, request, jsonify
import hmac
import sqlite3

from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


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
                     "price INTEGER NOT NULL,"
                     "description TEXT NOT NULL)")
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


@app.route('/protected/')
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


@app.route('/add-products/', methods=["POST"])
def add_products():
    response = {}

    if request.method == "POST":
        title = request.form['title']
        category = request.form['category']
        price = request.form['price']
        description = request.form['description']

        with sqlite3.connect('sale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items ("
                           "title,"
                           "category,"
                           "price,"
                           "description) VALUES(?, ?, ?, ?)", (title, category, price, description))
            conn.commit()
            response["status_code"] = 201
            response['message'] = "Product added successfully"
        return response


@app.route('/get-products/', methods=["GET"])
def get_products():
    response = {}
    with sqlite3.connect("sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return jsonify(response)


@app.route('/get-products-one/<int:id>/')
def view_one(id):
    response = {}

    with sqlite3.connect("sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items where id=?", str(id))
        product = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = product
    return jsonify(response)


@app.route('/edit-product/<int:id>/', methods=["PUT"])
def updating_products(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('sale.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")

                with sqlite3.connect('sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET title =? WHERE id=?",
                                   (put_data["title"], id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")

                with sqlite3.connect('sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET category =? WHERE id=?", (put_data["category"],
                                                                                id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect('sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET price =? WHERE id=?",
                                   (put_data["price"], id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

            elif incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect('sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE items SET description =? WHERE id=?",
                                   (put_data["description"], id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200

    return response


@app.route("/delete-product/<int:id>")
def delete_products(id):
    response = {}
    with sqlite3.connect("sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id=" + str(id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


if __name__ == "__main__":
    app.debug = True
    app.run(port=5002)

# https://dashboard.heroku.com/apps/limitless-citadel-50663/deploy/github
