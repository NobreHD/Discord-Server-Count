from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import requests, os, urllib.parse

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')


app = Flask(__name__)

def get_token(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI+'/auth',
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    return r.json()

def set_header(access_token, token_type):
    return {
        "Authorization": f"{token_type} {access_token}"
    }

def get_server_count(header):
    response = requests.get("https://discord.com/api/users/@me/guilds", headers=header)
    return len(response.json())    

def is_user_nitro(header):
    response = requests.get("https://discord.com/api/users/@me", headers=header)
    return response.json()['premium_type'] == 2

@app.route('/')
def index():
    return render_template("index.html", client_id = CLIENT_ID, redirect_url = urllib.parse.quote_plus(REDIRECT_URI + "/auth"))

@app.route('/auth')
def auth():
    code = request.args.get('code')
    token = get_token(code)
    header = set_header(token['access_token'], token['token_type'])
    server_count = get_server_count(header)
    nitro = is_user_nitro(header)
    return redirect(f"/?server_count={server_count}&nitro={nitro}")

app.run(host='0.0.0.0', port=80)