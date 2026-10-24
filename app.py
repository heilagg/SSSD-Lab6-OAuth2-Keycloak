#!/usr/bin/env python3
"""
Lab 6 - OAuth2.0 / OIDC demo app (Flask + Keycloak).

The app logs the user in through Keycloak using the OAuth2 Authorization Code
flow, requests the "openid discipline" scope, and prints the "discipline"
attribute taken from the access token.
"""

import base64
import json
import secrets

import requests
from flask import Flask, redirect, request, session
from markupsafe import escape

# ---------------------- CONFIG: edit CLIENT_SECRET ----------------------
KEYCLOAK_BASE = "http://localhost:8080"
REALM = "lab6"
CLIENT_ID = "flask-app"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"   # <-- paste the secret from Keycloak
REDIRECT_URI = "http://localhost:5001/callback"
# ------------------------------------------------------------------------

AUTH_URL = f"{KEYCLOAK_BASE}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_BASE}/realms/{REALM}/protocol/openid-connect/token"

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # used to sign the session cookie


def decode_jwt_payload(token: str) -> dict:
    """A JWT is header.payload.signature (base64url). Read the payload claims."""
    payload_b64 = token.split(".")[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)  # fix base64 padding
    return json.loads(base64.urlsafe_b64decode(payload_b64))


@app.route("/")
def home():
    return (
        "<h2>Lab 6 - OAuth2 / OIDC demo</h2>"
        '<p><a href="/login">Login with Keycloak</a></p>'
    )


@app.route("/login")
def login():
    # state is a random value we check on return, to tie the flow together
    state = secrets.token_urlsafe(16)
    session["state"] = state
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid discipline",   # we explicitly request the discipline scope
        "state": state,
    }
    return redirect(AUTH_URL + "?" + requests.compat.urlencode(params))


@app.route("/callback")
def callback():
    # 1. check the state matches the one we sent
    if request.args.get("state") != session.get("state"):
        return "Invalid state", 400

    # 2. exchange the one-time code for tokens
    code = request.args.get("code")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(TOKEN_URL, data=data)
    resp.raise_for_status()
    tokens = resp.json()

    # 3. read the "discipline" claim from the ACCESS token
    access_token = tokens["access_token"]
    claims = decode_jwt_payload(access_token)
    discipline = claims.get("discipline", "(no discipline claim in token)")
    username = claims.get("preferred_username", "")

    return f"""
    <h2>Logged in through Keycloak</h2>
    <p>User: {escape(username)}</p>
    <p>Your discipline (from the access token):
       <b>{escape(discipline)}</b></p>
    <hr>
    <details>
      <summary>Full access token claims</summary>
      <pre>{escape(json.dumps(claims, indent=2))}</pre>
    </details>
    <p><a href="/">Home</a></p>
    """


if __name__ == "__main__":
    app.run(port=5001, debug=True)
