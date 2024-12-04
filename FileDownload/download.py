import json
import boto3
import base64
import pymongo

MONGO_URI = "mongodb://FRP_admin:App%402020%40FRP%4024@45.79.122.7:27017/FRP?authSource=FRP"
mongo_client = pymongo.MongoClient(MONGO_URI)
auth_collection = mongo_client["FRP"]["main_table"]

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    authorization = event.get("headers", {}).get("authorization")
    body = json.loads(event["body"]) if "body" in event else event
    filename = body.get("filename")
    subfolder = body.get("meta")

    if not authorization or not filename or not subfolder:
        return {
            "statusCode": 400,
            "body": "Authorization, filename, and meta must be provided"
        }
    
    try:
        tenant = auth_collection.find_one({"URLKey": authorization})
        if not tenant:
            return {
                "statusCode": 404,
                "body": "Tenant ID not found"
            }
        
        tenant_id = tenant.get("tenant_id").lower()
        
        userfiles = tenant.get("userfiles", [])
        file_extension = None

        for folder in userfiles:
            if folder.get("metatag") == subfolder:
                for file in folder.get("files", []):
                    if file.get("filename") == filename:
                        file_extension = file.get("file_extension")
                        break
                if file_extension:
                    break

        if not file_extension:
            return {
                "statusCode": 404,
                "body": "File not found in metadata"
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error fetching tenant data: {str(e)}"
        }
    
    path = f"{subfolder}/{filename}"
    
    try:
        response = s3_client.get_object(Bucket=tenant_id, Key=path)
        file_content = response["Body"].read()
        base64_encoded_content = base64.b64encode(file_content).decode("utf-8")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "base64_content": base64_encoded_content,
                "file_extension": file_extension
            }),
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error fetching file from S3: {str(e)}"
        }

if __name__ == "__main__":
    event = {
        "headers": {"authorization": "BBF091C2-9FBC-46CE-951C-AC797CA0AF78"},
        "body": json.dumps({"filename": "marksheet1.jpg", "meta": "education"})
    }
    print(lambda_handler(event, None))
