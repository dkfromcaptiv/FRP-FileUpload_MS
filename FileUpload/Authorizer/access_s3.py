import json
import pymongo
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from datetime import datetime

MONGO_URI = "mongodb://FRP_admin:App%402020%40FRP%4024@45.79.122.7:27017/FRP?authSource=FRP"
mongo_client = pymongo.MongoClient(MONGO_URI)
auth_collection = mongo_client["FRP"]["auth_table"]

AES_KEY = b"gFjP5bR6ZQm2O5bC8qY3xD4vVqW8eR6j"

def decrypt_and_validate_token(token):
    try:
        encrypted_data = base64.b64decode(token)
        iv, ciphertext = encrypted_data[:AES.block_size], encrypted_data[AES.block_size:]
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
        token_time = datetime.strptime(decrypted_data, "%Y_%m_%d_%H_%M_%S")
        time_difference = (datetime.now() - token_time).total_seconds()
        
        if time_difference > 30:
            raise ValueError("Token expired")
        return True
    
    except (ValueError, Exception):
        raise ValueError("Invalid or expired token")

def lambda_handler(event, context):
    try:
        headers = event.get("headers", {})
        url_key, token = headers.get("authorization"), headers.get("token")
        
        if not url_key or not token:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing authorization or token"})}
        
        document = auth_collection.find_one({"URLKey": url_key, "token": token})
        if not document:
            return {"statusCode": 404, "body": json.dumps({"error": "Authorization or token not found"})}
        
        decrypt_and_validate_token(token)
        
        return {
            "principalId": "user",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {"Action": "execute-api:Invoke", "Effect": "Allow", "Resource": event.get("routeArn")}
                ],
            },
        }
    
    except ValueError as e:
        return {"statusCode": 403, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

if __name__ == "__main__":
    event = {
        "headers": {
            "authorization": "BBF091C2-9FBC-46CE-951C-AC797CA0AF78",
            "token": "zRfNhT/302XYZYlFl+dWogmiFTRh85jymH0QA2MaynIndHxDRasjrLnAs/YD/OgP"
        },
        "routeArn": "arn:aws:execute-api:ap-south-1:022499044345:m4e6s68p3l/$default/POST/"
    }
    print(lambda_handler(event, None))