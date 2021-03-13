from flask import Blueprint
from flask import request, Response
import sqlite3
import utils
import bcrypt

registration = Blueprint('registration', __name__)
location = "data"

def register_user(name, first_name, last_name, gender, pronouns, interests, auth, lat, lng, age):
    # If user name is already in use, return False with the reason
    if utils.check_if_user_exists("data", name):
        return False, "User name already in use."

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(auth.encode("utf-8"), salt)
    del auth

    # Connect to the database
    conn = sqlite3.connect(location)
    c = conn.cursor()

    # Insert the new user into the 'user' table
    c.execute(
        """INSERT INTO users
                  (user_name,
                  first_name,
                  last_name,
                  gender,
                  pronouns,
                  age,
                  lat,
                  lng,
                  salt,
                  hash,
                  nonce)
              VALUES (?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?);""",
        (name, first_name, last_name, gender, pronouns, age, lat, lng, salt, hash, None),
    )
    conn.commit()

    # Insert the new user's interests into the 'interests' table
    c.execute(
        """INSERT INTO interests
                  (user_name,
                  interest1,
                  interest2,
                  interest3,
                  interest4,
                  interest5)
              VALUES (?,?,?,?,?,?);""",
        (name, interests[0], interests[1], interests[2], interests[3], interests[4]),
    )
    conn.commit()

    return True, "Success"

@registration.route("/register", methods=["POST"])
def register():
    # The location of the database
    location = "data"

    # Connect to the database
    conn = sqlite3.connect(location)
    c = conn.cursor()

    req_data = request.get_json()

    user_name = req_data["user_name"]
    first_name = req_data["first_name"]
    last_name = req_data["last_name"]
    gender = req_data["gender"]
    pronouns = req_data["pronouns"]
    interests = req_data["interests"]
    auth = req_data["auth"]
    lat = req_data["lat"]
    lng = req_data["lng"]
    age = req_data["age"]

    success, message = register_user(
        user_name, first_name, last_name, gender, pronouns, interests, auth, lat, lng, age
    )

    if success:
        return Response(
            "{'message':" + message + "}", status=201, mimetype="application/json"
        )

    return Response(
        "{'message':" + message + "}", status=409, mimetype="application/json"
    )


@registration.route("/check_username", methods=["POST"])
def check_username():
    req_data = request.get_json()

    user_name = req_data["user_name"]

    exists = utils.check_if_user_exists("data", user_name)

    if exists:
        return Response(
            "{'message': 'User name already in use.'}",
            status=409,
            mimetype="application/json",
        )
    return Response(
        "{'message': 'User name available'}", status=200, mimetype="application/json"
    )
