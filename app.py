from flask import Flask, render_template, request, redirect, send_file
from dotenv import load_dotenv
import requests, os, urllib.parse

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

count = 0

app = Flask(__name__)

def get_count():
    global count
    if count == 0:
        with open("count.txt", "r") as f:
            count = int(f.read())
            return count

def add():
    global count
    count-=-1
    with open("count.txt", "w") as f:
        f.write(str(count))

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

@app.route('/')
def index():
    return render_template("index.html", client_id = CLIENT_ID, redirect_url = urllib.parse.quote_plus(REDIRECT_URI + "/auth"), count = get_count())

@app.route('/auth')
def auth():
    code = request.args.get('code')
    token = get_token(code)
    header = set_header(token['access_token'], token['token_type'])
    server_count = get_server_count(header)
    user_info = requests.get("https://discord.com/api/users/@me", headers=header).json()
    nitro = user_info['premium_type'] == 2
    name = urllib.parse.quote(user_info['username'] + "#" + user_info['discriminator'])
    add()
    return redirect(f"/?server_count={server_count}&nitro={nitro}&user={name}")

@app.route('/static/<path:path>')
def favicon(path):
    return send_file(f"static/{path}")