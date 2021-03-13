from pathlib import Path
import os
import requests
import getpass
import bcrypt
import subprocess
import json

SERVER_ADDRESS = "http://127.0.0.1:5000"


def register():

    # Get the username the user wishes to use
    username = input("Please enter a username no longer than 255 characters: ")

    # Check if the username if available by making a POST request to the API
    username_unavailable = (
        requests.post(
            f"{SERVER_ADDRESS}/check_username", json={"user_name": username}
        ).status_code
        != 200
    )

    # If the username is longer than 255 characters or
    # is not available, continue to ask
    while len(username) > 255 or username_unavailable:
        if len(username) > 255:
            username = input("Please enter a username no longer than 255 characters: ")
        else:
            username = input(
                "The username you entered is currently in use. Please enter another: "
            )
        username_unavailable = (
            requests.post(
                f"{SERVER_ADDRESS}/check_username", json={"user_name": username}
            ).status_code
            != 200
        )

    # Get the user's first name
    first_name = input("Please enter a first name no longer than 255 characters: ")
    # Continue to ask if it is longer than 255 characters
    while len(first_name) > 255:
        first_name = input("Please enter a first name no longer than 255 characters: ")

    # Get the user's last name
    last_name = input("Please enter a last name no longer than 255 characters: ")
    # Continue to ask if it is longer than 255 characters
    while len(last_name) > 255:
        last_name = input("Please enter a last name no longer than 255 characters: ")

    # Get the user's gender.
    print(
        """Please select the gender most applicable to you:
        0: Female
        1: Male
        2: Non-binary"""
    )
    gender = input("")

    # If the selection is not an integer or is not between 0 and 2 continue to ask
    while not gender.isnumeric() or 0 > int(gender) > 2:
        if not gender.isnumeric():
            print("Please enter an integer value for your selection.")
            print(
                """Please select the gender most applicable to you:
                0: Female
                1: Male
                2: Non-binary"""
            )
            gender = input("")
        else:
            print("Please select an integer between 0 and 2")
            print(
                """Please select the gender most applicable to you:
                0: Female
                1: Male
                2: Non-binary"""
            )
            gender = input("")
    gender = int(gender)
    genderstring = ["female", "male", "non-binary"][gender]

    # Get the user's pronouns
    print(
        """Please select your pronouns:
          0: she/her
          1: she/they
          2: he/him
          3: he/they
          4: they/them
          5: neopronouns (please specify)"""
    )
    print(f"If this question confuses you, select: {gender*2}")
    pronouns = input("")

    # If the selection is not an integer or is not between 0 and 5, continue to ask
    while not pronouns.isnumeric() or 0 > int(pronouns) > 5:
        if not pronouns.isnumeric():
            print("Please enter an integer value for your selection.")
            print(
                """Please select your pronouns:
                  0: she/her
                  1: she/they
                  2: he/him
                  3: he/they
                  4: they/them
                  5: neopronouns (please specify)"""
            )
            print(f"If this question confuses you, select: {gender*2}")
            pronouns = input("")
        else:
            print("Please enter a value between 0 and 5")
            print(
                """Please select your pronouns:
                  0: she/her
                  1: she/they
                  2: he/him
                  3: he/they
                  4: they/them
                  5: neopronouns (please specify)"""
            )
            print(f"If this question confuses you, select: {gender*2}")
            pronouns = input("")

    pronouns = int(pronouns)

    # If the user indicated that they use neopronouns, request that they specify
    # which neopronouns
    if pronouns == 5:
        pronounsstring = input("Please specify your pronouns: ")
    else:
        pronounsstring = ["she/her", "she/they", "he/him", "he/they", "they/them"][
            pronouns
        ]

    # Get 5 of the user's interests. If they cannot name enough interests the
    # remaining columns will be filled with None
    interests = [None, None, None, None, None]
    for i in range(5):
        interest = input(
            f"Please enter interest {i}. If you cannot think of one, press return:\n"
        )
        if interest != "":
            interests[i] = interest
        while len(str(interests[i])) > 255:
            print("Please limit your interest title to no more than 255 characters")
            interest = input(
                f"Please enter interest {i}. If you cannot think of one, press return:\n"
            )
            if interest != "":
                interests[i] = interest

    lat = float(input("Please enter your rough latitude:  "))
    lng = float(input("Please enter your rough longitude:  "))

    age = int(input("Please enter your age:  "))

    password = getpass.getpass("Please enter a password: ")
    password_verif = getpass.getpass("Please verify your password: ")
    while password_verif != password:
        print("Your passwords were inconsistent. Please try again.")
        password = getpass.getpass("Please enter a password: ")
        password_verif = getpass.getpass("Please verify your password: ")


    del password_verif

    r = requests.post(
        f"{SERVER_ADDRESS}/register",
        json={
            "user_name": username,
            "first_name": first_name,
            "last_name": last_name,
            "gender": genderstring,
            "pronouns": pronounsstring,
            "interests": interests,
            "auth": password,
            "lat": lat,
            "lng": lng,
            "age": age
        },
    )
    del password
    return username


def login(username=None):
    if not username:
        username = input("Enter username: ")
    password = getpass.getpass("Enter password to login: ").encode("utf-8")

    r = requests.get(f"{SERVER_ADDRESS}/salt-nonce", json={"user_name": username})

    salt, server_nonce = r.json()["message"].split()
    salt, server_nonce = salt.encode("utf-8"), server_nonce.encode("utf-8")

    client_nonce = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password, salt)

    nonce_hash = bcrypt.hashpw(password_hash, bcrypt.hashpw(client_nonce, server_nonce))

    r = requests.post(
        f"{SERVER_ADDRESS}/login",
        json={
            "user_name": username,
            "client_nonce": client_nonce.decode("utf-8"),
            "nonce_hash": nonce_hash.decode("utf-8"),
        },
    )
    if r.status_code == 200:
        print("Login successful.")
    else:
        print("Login failed.")

    return username


def display_user(user_data):
    display_string = f"""
{user_data['user_name']}{' '*32}Interests:
{user_data['gender']}{' '*(36+len(user_data['user_name'])-len(user_data['gender']))}{str(user_data['interests'][0])*bool(user_data['interests'][0])}
{user_data['pronouns']}{' '*(36+len(user_data['user_name'])-len(user_data['pronouns']))}{str(user_data['interests'][1])*bool(user_data['interests'][1])}
{' '*(36+len(user_data['user_name']))}{str(user_data['interests'][2])*bool(user_data['interests'][2])}
{' '*(36+len(user_data['user_name']))}{str(user_data['interests'][3])*bool(user_data['interests'][3])}
{' '*(36+len(user_data['user_name']))}{str(user_data['interests'][4])*bool(user_data['interests'][4])}
"""
    print(display_string)


def search_users(username):
    repeat = True
    while repeat:
        subprocess.run("clear")
        r = requests.get(f"{SERVER_ADDRESS}/get-match", json={"user_name": username})
        if not r.ok:
            return False
        users = r.json()
        for user_data in users:
            display_user(user_data)
            like = True if input("\rLike this user? y/n  ") == "y" else False
            if like:
                r = requests.post(
                    f"{SERVER_ADDRESS}/confirm-match",
                    json={"user_name": username, "match_name": user_data["user_name"]},
                )
            else:
                r = requests.post(
                    f"{SERVER_ADDRESS}/reject-match",
                    json={"user_name": username, "match_name": user_data["user_name"]},
                )
            repeat = (
                True if input("\rContinue looking for matches? y/n  ") == "y" else False
            )


home = str(Path.home())
if not os.path.isdir(f"{home}/.cli-matchmaking") or not os.path.isfile(
    f"{home}/.cli-matchmaking/name"
):
    try:
        os.mkdir(f"{home}/.cli-matchmaking/")
    except:
        # Please be quiet about this
        pass
    account = True if input("Already have an account? y/n  ") == "y" else False
    if account:
        username = login()
    else:
        username = register()
        login(username)

    with open(f"{home}/.cli-matchmaking/name", "w") as f:
        f.write(username)


else:
    with open(f"{home}/.cli-matchmaking/name", "r") as f:
        username = f.readline()
        login(username)

print(username)
search = search_users(username)
if not search:
    print("Could not get any matches. Exiting.")
