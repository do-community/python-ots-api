from flask import Flask, request
import base64, os, hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import timedelta
from flask_cors import CORS
import redis
import uuid

app = Flask(__name__)
CORS(app)

r = redis.Redis(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 6379),
    password=os.getenv("DB_PASSWORD", None),
    ssl=os.getenv("SSL", "True") == "True",
)


@app.route("/secrets", methods=["POST"])
def create_secret():
    content = request.get_json()
    if content is None or all(key in content for key in ("passphrase", "message")) is not True:
        return {"success": "False", "message": "Missing passphrase and/or message"}, 400
    passphrase = content["passphrase"]
    message = content["message"]
    if "expiration_time" in content:
        expiration_time = content["expiration_time"]
        if isinstance(expiration_time, int) is True:
            expiration_time = content["expiration_time"]
        else:
            if content["expiration_time"].isdigit():
                expiration_time = int(content["expiration_time"])
    else:
        expiration_time = 604800

    id = uuid.uuid4().hex

    m = hashlib.sha256()
    m.update(passphrase.encode("utf-8"))
    sha = m.hexdigest()

    # setup a Fernet key based on our passphrase
    password_provided = passphrase  # This is input in the form of a string
    password = password_provided.encode()  # Convert to type bytes
    salt = str.encode(os.getenv("SALT"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    f = Fernet(key)

    # encrypt the message
    ciphertext = f.encrypt(message.encode("utf-8"))

    r.setex(
        id,
        timedelta(seconds=expiration_time),
        "{0}\n{1}".format(sha, ciphertext.decode("utf-8")),
    )
    return {"success": "True", "id": id}


@app.route("/secrets/<id>", methods=["POST"])
def get_secret(id):
    content = request.get_json()
    if "passphrase" not in content:
        return {"success": "False", "message": "Missing passphrase"}, 400
    passphrase = content["passphrase"]

    data = r.get(id)
    if data is None:
        return {
            "success": "False",
            "message": "This secret either never existed or it was already read",
        }, 404

    data = data.decode("utf-8")
    stored_sha, stored_ciphertext = data.split("\n")

    m = hashlib.sha256()
    m.update(passphrase.encode("utf-8"))
    sha = m.hexdigest()

    if stored_sha != sha:
        return {
            "success": "False",
            "message": "This secret either never existed or it was already read",
        }

    r.delete(id)
    # If this doesn't return a value we say secret has either
    # never existed or it was already read
    password = passphrase.encode()  # Convert to type bytes
    salt = str.encode(os.getenv("SALT"))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    f = Fernet(key)
    decrypted_message = f.decrypt(stored_ciphertext.encode("utf-8"))

    return {"success": "True", "message": decrypted_message.decode("utf-8")}
