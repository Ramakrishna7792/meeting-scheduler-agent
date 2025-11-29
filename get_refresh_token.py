from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# Your downloaded OAuth client_secret.json file
CLIENT_SECRET_FILE = "client_secret.json"

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES
    )

    creds = flow.run_local_server(port=0)

    print("\n============================================")
    print("YOUR REFRESH TOKEN:")
    print(creds.refresh_token)
    print("============================================\n")

    # Save for backup
    with open("saved_token.json", "w") as f:
        f.write(json.dumps({
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }, indent=4))

    print("saved_token.json created!")

if __name__ == "__main__":
    main()
