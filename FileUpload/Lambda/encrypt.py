import json
import pymongo
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
from datetime import datetime
import urllib.parse

username = "FRP_admin"
password = "App@2020@FRP@24"
host = "45.79.122.7"
database = "FRP"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)
connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:27017/{database}?authSource={database}"

client = pymongo.MongoClient(connection_string)
db = client["FRP"]
auth_collection = db["auth_table"]
main_collection = db["main_table"]


def aes_encrypt(data):
    key = b"gFjP5bR6ZQm2O5bC8qY3xD4vVqW8eR6j"
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    encrypted_message = iv + encrypted_data
    return base64.b64encode(encrypted_message).decode("utf-8")


def lambda_handler(event, context):
    body = json.loads(event["body"]) if "body" in event else event
    tenant_id = body.get("tenant_id")
    URLKey = event["headers"].get("authorization")

    auth_entry = auth_collection.find_one({"tenant_id": tenant_id, "URLKey": URLKey})

    if not auth_entry:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Tenant ID and URLKey do not match in auth_table"}
            ),
        }

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    token = aes_encrypt(timestamp)

    auth_collection.update_one(
        {"tenant_id": tenant_id, "URLKey": URLKey},
        {"$set": {"token": token}},
        upsert=True,
    )

    if main_collection.count_documents({"tenant_id": tenant_id}) == 0:
        main_collection.insert_one({"tenant_id": tenant_id, "URLKey": URLKey})

    return {
        "statusCode": 200,
        "body": json.dumps({"tenant_id": tenant_id, "token": token}),
    }


if __name__ == "__main__":
    test_event = {
        "headers": {"authorization": "BBF091C2-9FBC-46CE-951C-AC797CA0AF78"},
        "body": json.dumps(
            {
                "tenant_id": "DA9909F1-AB16-4F53-8AAA-800B19A8BEE6",
            }
        ),
    }
    test_context = {}
    print(lambda_handler(test_event, test_context))


