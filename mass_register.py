import requests
import random

SERVER_ADDRESS = "http://127.0.0.1:5000"


def register():
    for i in range(1000):

            username = str(i)
            print(username)
            # Check if the username if available by making a POST request to the API
            username_unavailable = (
                requests.post(
                    f"{SERVER_ADDRESS}/check_username", json={"user_name": username}
                ).status_code
                != 200
            )



            # Get the user's first name
            first_name = str(i)

            # Get the user's last name
            last_name = str(i)
            gender = random.choice((0, 1, 2))
            genderstring = ["female", "male", "non-binary"][gender]

            pronouns = random.choice((0, 1, 2, 3, 4))
            pronounsstring = ["she/her", "she/they", "he/him", "he/they", "they/them"][
                pronouns
            ]
            interests = [i]*5

            lat = float(i%180)
            lng = float(i%180)

            age = int(i)

            password = str(i)

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
                    "age": age,
                },
            )
            del password
    return True



register()
