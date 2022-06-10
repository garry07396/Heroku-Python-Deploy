import flask
import os
from flask import send_from_directory
import sys
import requests
from urllib.parse import urlparse, parse_qs
from fyers_api import accessToken
from fyers_api import fyersModel
app = flask.Flask(__name__)

username = "XG08959"  # fyers_id 
password = "Arihant4u@"  # fyers_password
pin = 1949  # your integer pin
client_id = "X3D0U1H61S-100"  # "L9NY****W-100" (Client_id here refers to APP_ID of the created app)
secret_key = "SD476OVV6A"  # app_secret key which you got after creating the app
redirect_uri = "https://smartstrangles.herokuapp.com/api/tf"  # redircet_uri you entered while creating APP.

def setup():
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "accept-language": "en-US,en;q=0.9",
    }

    s = requests.Session()
    s.headers.update(headers)

    data1 = f'{{"fy_id":"{username}","password":"{password}","app_id":"2","imei":"","recaptcha_token":""}}'
    r1 = s.post("https://api.fyers.in/vagator/v1/login", data=data1)
    assert r1.status_code == 200, f"Error in r1:\n {r1.json()}"

    request_key = r1.json()["request_key"]
    data2 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{pin}","recaptcha_token":""}}'
    r2 = s.post("https://api.fyers.in/vagator/v1/verify_pin", data=data2)
    assert r2.status_code == 200, f"Error in r2:\n {r2.json()}"

    headers = {"authorization": f"Bearer {r2.json()['data']['access_token']}", "content-type": "application/json; charset=UTF-8"}
    data3 = f'{{"fyers_id":"{username}","app_id":"{client_id[:-4]}","redirect_uri":"{redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
    r3 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data3)
    assert r3.status_code == 308, f"Error in r3:\n {r3.json()}"

    parsed = urlparse(r3.json()["Url"])
    auth_code = parse_qs(parsed.query)["auth_code"][0]

    session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type="code", grant_type="authorization_code")
    session.set_token(auth_code)
    response = session.generate_token()
    token = response["access_token"]
    print("Got the fyers access token!")
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    print(fyers.get_profile())
    return token

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')

@app.route('/token')
def token():
    token = setup()
    return token


@app.route('/')
@app.route('/home')
def home():
    return "Fyers Login App"

if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
