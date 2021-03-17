from flask import Blueprint
from flask import request, Response
import sqlite3
import bcrypt
import utils

loginblueprint = Blueprint("login", __name__)


@loginblueprint.route("/login", methods=["POST"])
def login():
    # Connect to the database
    conn = sqlite3.connect("data")
    c = conn.cursor()

    req_data = request.get_json()
    username = req_data["user_name"]
    client_nonce = req_data["client_nonce"].encode("utf-8")
    client_nonce_hash = req_data["nonce_hash"].encode("utf-8")

    if not utils.check_if_user_exists("data", username):
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )

    c.execute("SELECT hash,nonce FROM users WHERE user_name=?", (username,))

    password_hash, server_nonce = c.fetchone()

    c.execute("UPDATE users SET nonce = NULL WHERE user_name=?", (username,))
    conn.commit()

    server_nonce_hash = bcrypt.hashpw(
        password_hash, bcrypt.hashpw(client_nonce, server_nonce)
    )

    if client_nonce_hash == server_nonce_hash:
        session_id = None
        return {"message": "Autorisation accepted", "session_id": session_id}, 200
    else:
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )


@loginblueprint.route("/salt-nonce", methods=["GET"])
def request_salt_and_nonce():
    req_data = request.get_json()
    user_name = req_data["user_name"]

    # Connect to the database
    conn = sqlite3.connect("data")
    c = conn.cursor()

    c.execute("""SELECT salt FROM users WHERE user_name=?""", (user_name,))

    salt = c.fetchone()
    nonce = bcrypt.gensalt()
    c.execute("UPDATE users SET nonce = ? WHERE user_name=?", (nonce, user_name))
    conn.commit()

    if salt is not None:
        salt = salt[0]
        string = '{"message":"' + str(salt)[2:-1] + " " + str(nonce)[2:-1] + '"}'

        return Response(string, status=200, mimetype="application/json")

    else:
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )
