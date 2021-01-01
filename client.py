from pathlib import Path
import os
import requests

home = str(Path.home())
if not os.path.isdir(f"{home}/.clidating"):
    os.mkdir(f"{home}/.clidating/")
    # r = requests.post("http://127.0.0.1:5000/register", json={"user_name": "pussyslayer69", "first_name": "John", "last_name": "Doe", "gender": "Non-binary",
    #                                                           "pronouns": "they/them", "interests": ["Python", "Jython", "Cython", "Gython", None]})
    # print(r.status_code)
