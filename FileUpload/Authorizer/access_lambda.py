import json
import pymongo
import urllib.parse

def generate_policy(principal_id, effect, resource):
    auth_response = {
        "principalId": principal_id
        }
    if effect and resource:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke", 
                    "Effect": effect, 
                    "Resource": resource
                }
            ]
        }
        auth_response["policyDocument"] = policy_document
    return auth_response

def lambda_handler(event, context):
    URLKey = event["headers"].get("authorization")
    
    username = "FRP_admin"
    password = "App@2020@FRP@24"
    host = "45.79.122.7"
    database = "FRP"
    encoded_username = urllib.parse.quote_plus(username)
    encoded_password = urllib.parse.quote_plus(password)
    connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:27017/{database}?authSource={database}"

    client = pymongo.MongoClient(connection_string)
    db = client["FRP"]
    collection = db["auth_table"]

    document = collection.find_one({"URLKey": URLKey})
    client.close()

    if document:
        return generate_policy("user", "Allow", event["routeArn"])
    else:
        return generate_policy("user", "Deny", event["routeArn"])


if __name__ == "__main__":
    test_event = {
        "headers": {"authorization": "BBF091C2-9FBC-46CE-951C-AC797CA0AF78"},
        "body": json.dumps({
            "tenant_id": "DA9909F1-AB16-4F53-8AAA-800B19A8BEE6"
        }),
        "routeArn": "arn:aws:execute-api:ap-south-1:022499044345:m4e6s68p3l/$default/GET/",
    }
    print(lambda_handler(test_event, None))
