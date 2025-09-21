import json
from src.core import build_payload_dict

def handler(event, context):
    payload = build_payload_dict()
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload)
    }
