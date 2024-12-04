import pymongo
import json

MONGO_URI = "mongodb://FRP_admin:App%402020%40FRP%4024@45.79.122.7:27017/FRP?authSource=FRP"
mongo_client = pymongo.MongoClient(MONGO_URI)
auth_collection = mongo_client["FRP"]["main_table"]

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"]) if "body" in event else event
        tenant_id = body.get('tenant_id')
        
        if not tenant_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "tenant_id is required in the body"})
            }
        
        tenant_id_upper = tenant_id.upper()
        
        tenant_data = auth_collection.find_one({"tenant_id": tenant_id_upper})
        
        if not tenant_data:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Tenant not found"})
            }
        
        subfolders = {}
        
        for userfile in tenant_data.get('userfiles', []):
            metatag = userfile.get('metatag')
            files = [file_info['filename'] for file_info in userfile.get('files', [])]
            subfolders[metatag] = files
        
        result = {
            "file-section-header": subfolders
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


if __name__ == "__main__":
    event = {
        "body": json.dumps({"tenant_id": "DA9909F1-AB16-4F53-8AAA-800B19A8BEE6"})
    }
    print(lambda_handler(event, None))
