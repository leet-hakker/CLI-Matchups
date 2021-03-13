from flask import Blueprint
from flask import request, Response
from flask import jsonify
import get_matches
import sqlite3
import json

matching = Blueprint('matching', __name__)

@matching.route("/get-match", methods=["GET"])
def get_match():
    req_data = request.get_json()
    users = get_matches.get_n_sorted_users(25, req_data["user_name"])

    count = len(json.loads(users))
    print(count)
    if count:
        conn = sqlite3.connect("data")
        c = conn.cursor()
        c.execute("UPDATE users SET count = ? WHERE user_name=?", (count, req_data["user_name"]))
        conn.commit()
        return jsonify(users)
    else:
        return Response('{"message": "Invalid request"}', status=400, mimetype="application/json")


@matching.route("/confirm-match", methods=["POST"])
def confirm_match():
    req_data = request.get_json()
    return Response('{"message:" "Success"}', status=200, mimetype="application/json")


@matching.route("/reject-match", methods=["POST"])
def reject_match():
    req_data = request.get_json()
    return Response('{"message": "Success"}', status=200, mimetype="application/json")
