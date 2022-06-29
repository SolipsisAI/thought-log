from pydrive2.auth import GoogleAuth


def authenticate():
    # You need client_secrets.json
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
