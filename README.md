# Lab 6 - OAuth2.0 / OIDC with Keycloak

Software Security and Secure Development (SSSD). Author: Amirzhan Malika.

A small Flask web app that authenticates users through Keycloak using the OAuth2
Authorization Code flow, requests the `openid discipline` scope, and prints the
`discipline` attribute taken from the access token.

## How it works

Keycloak is the identity provider (authorization server). The Flask app is the
client. The flow:

1. The browser opens the app and clicks Login.
2. The app redirects to Keycloak, requesting `scope=openid discipline`.
3. The user registers (with a `discipline` field) or logs in.
4. Keycloak redirects back with a one-time `code`.
5. The app exchanges the code for tokens and reads the `discipline` claim from the access token.

## Keycloak setup

Run Keycloak:

```
docker run -d --name kc -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:26.4 start-dev
```

Then in the admin console (http://localhost:8080, admin/admin):

1. Create a realm `lab6`.
2. Realm settings -> Login -> enable User registration.
3. Realm settings -> User profile -> create attribute `discipline`.
4. Client scopes -> create `discipline` (type Optional). Add a User Attribute mapper: user attribute `discipline`, token claim `discipline`, add to access token ON.
5. Clients -> create `flask-app` (OpenID Connect, client authentication ON). Redirect URI `http://localhost:5001/*`. Add the `discipline` client scope as Optional. Copy the client secret.

## Run the app

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# paste your client secret into app.py (CLIENT_SECRET)
python3 app.py
```

Open http://localhost:5001, click Login, register with a discipline value, and
the page will show your discipline read from the access token.

## Note

`app.py` keeps `CLIENT_SECRET` as a placeholder on purpose. Do not commit your
real client secret to the repository.
