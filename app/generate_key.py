import yaml
import bcrypt

names = ["관리자", "로그인테스트"]
usernames = ["jms", "admin"]

hashed_passwords = [
    bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    for p in passwords
]

data = {
    "credentials": {
        "usernames": {
            usernames[0]: {
                "name": names[0],
                "password": hashed_passwords[0]
            },
            usernames[1]: {
                "name": names[1],
                "password": hashed_passwords[1]
            }
        }
    },
    "cookie": {
        "expiry_days": 7,
        "key": "some_signature_key",
        "name": "some_cookie_name"
    }
}

with open("config.yaml", "w", encoding="utf-8") as file:
    yaml.dump(
        data,
        file,
        allow_unicode=True,
        sort_keys=False
    )
