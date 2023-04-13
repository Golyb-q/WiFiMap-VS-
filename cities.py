__author__ = "R"
__project__ = "Wifimap Downloader"

from datetime import date
import hashlib
from importlib.resources import read_text
import pip._vendor.requests
import time
import random
import json
from os import path

# Config
user_agent = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; Google Nexus 6 - 5.1.0 - API 22 - "
    "1440x2560 Build/LMY47D) WiFiMap/2.2.0",
    "Content-type": "application/json",
    "Accept": "text/plain",
}

current_date = date.today()


def format_string(value):
    return "{{{}}}".format(
        ",".join('"{}":"{}"'.format(key, val) for (key, val) in sorted(value.items()))
    )


def key():
    random.seed(time.time())
    return random.randrange(0, 1000)


def linuxTimestamp(string):
    salt = "MoKXE8Z84hkHOIXNWw6XIJli2Sl-pqE-rryygRBj"
    sha = hashlib.sha1()
    sha.update(("{}".format(string + salt)).encode(encoding="UTF-8", errors="strict"))
    return sha.hexdigest().lower()[2:25]


def sign_in():
    if not path.exists("sign_in.txt"):
        sign_in = json.dumps(
            {"email": str(input("Email: ")), "password": str(input("Password: "))}
        )
        with open("sign_in.txt", "w") as line:
            line.write(sign_in)
        return json.loads(sign_in)
    else:
        with open("sign_in.txt", "r") as line:
            return json.loads(line.read())


def load_token():
    if not path.exists("session.txt"):
        data = "{}".format(format_string(sign_in()))
        token = pip._vendor.requests.post(
            "http://wifimap.io/users/sign_in?timestamp={}".format(linuxTimestamp(data)),
            data=data,
            headers=user_agent,
        )
        with open("session.txt", "w") as line:
            line.write(token.text)
        return json.loads(token.text)

    else:
        with open("session.txt", "r") as line:
            return json.loads(line.read())


def valid_name(oldName):
    newName = ""
    correctSymbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for symbol in oldName:
        if symbol in correctSymbols:
            newName = newName + symbol
    return newName


if __name__ == "__main__":
    token = load_token()["session_token"]

    with open("city.csv", "r") as f:
        for i in f:
            i = i.replace("\n", "")
            split = i.split(",")
            print(
                "{} - {}".format(split[2].translate('"\n\r'), split[1].translate('"\n'))
            )

            x = pip._vendor.requests.get(
                "http://wifimap.io/user/purchased_cities/"
                "{}?srv_id={}&sub_srv_id={}&timestamp={}&session_token={}".format(
                    split[0], key(), key(), linuxTimestamp(str(split[0] + token)), token
                ),
                headers=user_agent,
            )

            if x.status_code == 200:
                with open(
                    "WIFIdata\\{}. {}-{}.json".format(
                        current_date,
                        valid_name(split[2].translate('"\n\r')),
                        valid_name(split[1].translate('"\n')).strip(),
                    ),
                    "w",
                    encoding="utf-8",
                ) as z:
                    json.dump(str(x.text), z, ensure_ascii=False, indent=4)
            else:
                print(x.status_code)
                # data = json.dumps({
                #    "order": {
                #    "city_id": 9,
                #    "platform": "android"
                #    }
                # })
                # requests.post("http://wifimap.io/users/orders?timestamp={}&session_token={}".format(linuxTimestamp(data), token), data=data, headers=user_agent)
