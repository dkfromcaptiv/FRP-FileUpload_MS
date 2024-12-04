import boto3
import logging
import json
import base64
import pymongo
from botocore.exceptions import ClientError
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
MONGO_URI = ("mongodb://FRP_admin:App%402020%40FRP%4024@45.79.122.7:27017/FRP?authSource=FRP")
mongo_client = pymongo.MongoClient(MONGO_URI)
auth_collection = mongo_client["FRP"]["main_table"]

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"]) if "body" in event else event
        headers = event.get("headers", {})
        authorization = headers.get("authorization")
        file_data_base64 = body.get("fileContent")
        metatag = body.get("metatag")
        filename = body.get("filename")

        if not authorization:
            return {"statusCode": 400,"body": json.dumps("Missing 'authorization' in headers")}
        if not file_data_base64:
            return {"statusCode": 400,"body": json.dumps("Missing 'fileContent' in event body")}
        if not metatag:
            return {"statusCode": 400,"body": json.dumps("Missing 'metatag' in event body")}
        if not filename:
            return {"statusCode": 400,"body": json.dumps("Missing 'filename' in event body")}

        document = auth_collection.find_one({"URLKey": authorization})
        if not document:
            return {"statusCode": 404,"body": json.dumps("Invalid 'authorization' token")}

        tenant_id = document.get("tenant_id")
        if not tenant_id:
            return {"statusCode": 500,"body": json.dumps("Missing 'tenant_id' in database record")}

        bucket_name = tenant_id.lower()
        subfolder_name = f"{metatag}/"

        create_bucket(bucket_name)
        create_folder(bucket_name, subfolder_name)

        file_data = base64.b64decode(file_data_base64)
        s3_file_path = subfolder_name + filename

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_file_path,
            Body=file_data,
            Metadata={"Meta-Tag": metatag},
        )

        file_extension = get_file_extension(filename)
        time_of_uploading = format_date(datetime.utcnow())

        update_userfiles_in_db(tenant_id, metatag, filename, file_extension, time_of_uploading)

        return {
            "statusCode": 200,
            "body": json.dumps(f"File uploaded successfully to {bucket_name}/{s3_file_path}")
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

def create_bucket(bucket_name):
    region = "ap-south-1"
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region}
        )
        logger.info(f"Bucket {bucket_name} created.")

def create_folder(bucket_name, subfolder_name):
    folder_key = subfolder_name
    s3_client.put_object(Bucket=bucket_name, Key=folder_key)
    logger.info(f"Subfolder {subfolder_name} created in bucket {bucket_name}.")

def get_file_extension(filename):
    return filename.split(".")[-1] if "." in filename else ""

def format_date(date):
    return date.strftime("%Y-%m-%d__%H:%M:%S")

def update_userfiles_in_db(tenant_id, metatag, filename, file_extension, time_of_uploading):
    document = auth_collection.find_one({"tenant_id": tenant_id})

    if not document:
        logger.error(f"Tenant with ID {tenant_id} not found.")
        return

    userfiles = document.get("userfiles", [])
    metatag_exists = False
    for userfile in userfiles:
        if userfile["metatag"] == metatag:
            userfile["files"].append({
                    "filename": filename,
                    "file_extension": file_extension,
                    "time_of_uploading": time_of_uploading,
                })
            metatag_exists = True
            break

    if not metatag_exists:
        userfiles.append({
                "metatag": metatag,
                "files": [{
                        "filename": filename,
                        "file_extension": file_extension,
                        "time_of_uploading": time_of_uploading,
                    }]
                })

    auth_collection.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"userfiles": userfiles}}
    )
    logger.info(f"Updated userfiles for tenant {tenant_id} with new file {filename}.")

if __name__ == "__main__":
    event = {
        "headers": {"authorization": "BBF091C2-9FBC-46CE-951C-AC797CA0AF78"},
        "body": json.dumps(
            {
                "fileContent": "VGhpcyBpcyBhIHRlc3QgZmlsZS4=",
                "metatag": "certificates",
                "filename": "SUMMA.pdf",
            }
        ),
    }
    print(lambda_handler(event, None))
