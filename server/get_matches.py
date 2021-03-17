import random
import datetime
import math
from haversine import haversine
import sqlite3
import json


def calc_like_value(age, gender, pronouns, preferences):
    value = 0
    if "age" in preferences.keys():
        if preferences["age"][0] <= age <= preferences["age"][1]:
            value += 1
    if "gender" in preferences.keys():
        if gender in preferences["gender"]:
            value += 1
    if "pronouns" in preferences.keys():
        if pronouns in preferences["pronouns"]:
            value += 1
    return value


def calc_dislike_value(age, gender, pronouns, dislikes):
    dislike_value = 0
    if "age" in dislikes.keys():
        if dislikes["age"][0] > age > dislikes["age"][1]:
            dislike_value += 1
    if "gender" in dislikes.keys():
        if gender in dislikes["gender"]:
            dislike_value += 1
    if "pronouns" in dislikes.keys():
        if pronouns in dislikes["pronouns"]:
            dislike_value += 1
    return dislike_value


def find_common_interests(A_interests, B_interests):
    return len(list(set(A_interests).intersection(B_interests)))


def calculate_distance(lat, lng, lat0, lng0):
    return haversine((lat, lng), (lat0, lng0))


def calculate_compatibility(A, B, preferences={}):
    distance = calculate_distance(A["lat"], A["lng"], B["lat"], B["lng"])
    dist_factor = 1 - math.pow(distance, 2)
    B["likes"] = calc_like_value(B["age"], B["gender"], B["pronouns"], preferences)
    B["dislikes"] = calc_dislike_value(
        B["age"], B["gender"], B["pronouns"], preferences
    )
    B["common_interests"] = find_common_interests(A["interests"], B["interests"])

    # L(a,b) = { I | a likes | about b }
    # D(a,b) = { I | a dislikes | about b }
    # I(a)   = { I | a is interested in }
    #
    # Assume every set in the below equation below represents the length of the sets
    #
    # (1 + L(a,b) - D(a,b)) * (I(a) ∩ I(b)) * distance_factor
    return ((1 + B["likes"] - B["dislikes"]) * B["common_interests"]) * dist_factor


def get_n_users(n, username):
    conn = sqlite3.connect("data")
    c = conn.cursor()

    c.execute("SELECT ROWID FROM users WHERE user_name=?", (username,))
    index = c.fetchone()[0]

    c.execute(
        "SELECT user_name, age, gender, pronouns, lat, lng FROM users WHERE ROWID >= ? AND user_name!=? LIMIT ?",
        (n, username, index),
    )
    users = c.fetchall()

    return users


def get_n_sorted_users(n, username):
    conn = sqlite3.connect("data")
    c = conn.cursor()

    c.execute(
        "SELECT user_name, age, gender, pronouns, lat, lng FROM users WHERE user_name=?",
        (username,),
    )
    user_A = c.fetchone()

    c.execute(
        "SELECT interest1, interest2, interest3, interest4, interest5 FROM interests WHERE user_name=?",
        (user_A[0],),
    )
    interests = c.fetchone()
    user_A = {
        "user_name": user_A[0],
        "age": user_A[1],
        "gender": user_A[2],
        "pronouns": user_A[3],
        "interests": interests,
        "lat": user_A[4],
        "lng": user_A[5],
    }

    users = get_n_users(n, username)

    for i in range(len(users)):
        c.execute(
            "SELECT interest1, interest2, interest3, interest4, interest5 FROM interests WHERE user_name=?",
            (users[i][0],),
        )
        interests = c.fetchone()
        users[i] = {
            "user_name": users[i][0],
            "age": users[i][1],
            "gender": users[i][2],
            "pronouns": users[i][3],
            "interests": interests,
            "lat": users[i][4],
            "lng": users[i][5],
        }
        users[i]["compatibility"] = calculate_compatibility(user_A, users[i])

    return json.dumps(users)
