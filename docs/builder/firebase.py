import json
import re
from pathlib import Path

import requests

CERT = "AF1F2F0293ABE91D3EEC64BBD91ECA70643CF311"
PACKAGE = "com.vyroai.aiart"
KEY = "AIzaSyBqheNjCmckFZsc8btvjLzsI_mS5Iw20OQ"

PATH = Path(__file__).resolve().parent / "constants.py"


def get_key(value: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', "_", value.strip().upper()).rstrip("_")


if __name__ == "__main__":
    session = requests.Session()
    session.headers = {
        "accept": "*/*",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 10; Mi A2 Build/QKQ1.190910.002)"
    }

    session.headers.update({
        "x-android-cert": CERT,
        "x-android-package": PACKAGE,
        "x-firebase-client": "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA",
        "x-goog-api-key": KEY
    })

    r = session.request(
        method="POST",
        url="https://firebaseinstallations.googleapis.com/v1/projects/imagine-5d4e5/installations",
        json={
            "fid": "c9JbZUtWROmcmyPKFNhsgE",
            "appId": "1:47152938399:android:928f1ecf0490a9b76611aa",
            "authVersion": "FIS_v2",
            "sdkVersion": "a:17.1.3"
        }
    )
    r.raise_for_status()

    token = r.json()["authToken"]["token"]
    session.headers.pop("x-firebase-client", None)
    session.headers.update({
        "x-firebase-rc-fetch-type": "BASE/1",
        "x-goog-firebase-installations-auth": token,
        "x-google-gfe-can-retry": "yes"
    })

    r = session.request(
        method="POST",
        url="https://firebaseremoteconfig.googleapis.com/v1/projects/47152938399/namespaces/firebase:fetch",
        json={
            "appInstanceId": "c9JbZUtWROmcmyPKFNhsgE",
            "appVersion": "2.7.3",
            "countryCode": "US",
            "analyticsUserProperties": {},
            "appId": "1:47152938399:android:928f1ecf0490a9b76611aa",
            "platformVersion": "29",
            "timeZone": "Asia/Tokyo",
            "sdkVersion": "21.4.0",
            "packageName": "com.vyroai.aiart",
            "appInstanceIdToken": token,
            "languageCode": "en-US",
            "appBuild": "148"
        }
    )
    r.raise_for_status()
    content = r.json()["entries"]

    # Import
    model = ["# Generated by the firebase web compiler.  DO NOT EDIT!", "# source: firebase.py", ""]
    model.append("from enum import Enum")
    model.append("")

    # Key
    """
    model.append("# {}".format(content["transformation"]))
    model.append("APP_KEY = '{}'".format(content["key"]))
    model.append("APP_IV = '{}'".format(content["iv"]))
    model.append("")
    """

    # Banned
    model.append("# Banned")
    model.append("BANNED_WORDS = {}".format([w.lower() for w in json.loads(content["profanity_list"])["banned_words"]]))
    model.append("\n")

    # Mode
    model.append("# KEY = (parameter, images, thumbnail)")
    model.append("class Mode(Enum):")
    for item in json.loads(content["Image_remix_new_modes"]):
        key = get_key(item["displayName"])
        item.pop("displayName", None)
        item.pop("isPremium", None)
        model.append(f"\t{key} = {tuple(item.values())}")
    model.append("\n")

    # Ratio
    model.append("# KEY = ratio")
    model.append("class Ratio(Enum):")
    for item in json.loads(content["image_remix_aspect_ratios"]):
        ratio = item["ratio"].split(":")
        model.append(f'\tRATIO_{ratio[0]}X{ratio[1]} = "{item["ratio"]}"')
    model.append("\n")

    # Style
    model.append("# KEY = (style_id, style_name, style_thumb, init_prompt)")
    model.append("class Style(Enum):")
    for item in json.loads(content["styles_v2"]):
        key = get_key(item["style_name"])
        item.pop("id", None)
        item.pop("isPremium", None)
        if "init_prompt" not in item:
            item["init_prompt"] = ""
        model.append(f"\t{key} = {tuple(item.values())}")
    model.append("\n")

    # Inspiration
    model.append("# KEY = (prompt, inspiration_thumb, style_id, seed)")
    model.append("class Inspiration(Enum):")
    for i, item in enumerate(json.loads(content["inspirations"])):
        item.pop("inspiration_id", None)
        item.pop("aspect_ratio", None)
        model.append(f"\tINSPIRATION_{i + 1:02d} = {tuple(item.values())}")
    model.append("\n")

    PATH.write_text("\n".join(model), encoding="utf-8")
    print(f"I: Created: {PATH}")
