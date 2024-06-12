import requests
import hashlib
import base64
import json
import uuid

# API base URL and endpoint
base_url = "https://mercury-t2.phonepe.com"
endpoint = "/v3/recurring/auth/init"
url = base_url + endpoint

# Salt key and salt index
salt_key = "5d8b52ef-95c2-4b00-afda-d919207624de"
salt_index = "1"

# Common parameters
merchant_id = "AMOGHNYAONLINE"
# merchant_user_id = "KBd2c8835261fa4930aede5441fdabe035"
# subscription_id = "OMS2406031248181473229493D"
# vpa = "nagendra.nagarthi@ybl"

# Function to generate a unique authRequestId
def generate_auth_request_id():
    return "TX" + str(uuid.uuid4().int)[:10]

# Function to generate SHA256 hash
def generate_sha256(base64_payload, endpoint, salt_key):
    concatenated_str = base64_payload + endpoint + salt_key
    sha256_hash = hashlib.sha256(concatenated_str.encode('utf-8')).hexdigest()
    return sha256_hash

# Function to create the payload based on flow type
def create_payload(flow_type,merchant_user_id,subscription_id,vpa):
    auth_request_id = generate_auth_request_id()
    if flow_type == "Intent":
        payload = {
            "merchantId": merchant_id,
            "merchantUserId": merchant_user_id,
            "subscriptionId": subscription_id,
            "authRequestId": auth_request_id,
            "paymentInstrument": {
                "type": "UPI_INTENT",
                "targetApp": "com.phonepe.app"
            },
            "deviceContext": {
                "deviceOS": "ANDROID"
            }
        }
    elif flow_type == "Collect":
        payload = {
            "merchantId": merchant_id,
            "merchantUserId": merchant_user_id,
            "subscriptionId": subscription_id,
            "authRequestId": auth_request_id,
            "paymentInstrument": {
                "type": "UPI_COLLECT",
                "vpa": vpa
            }
        }
    # elif flow_type == "QR":
    #     payload = {
    #         "merchantId": merchant_id,
    #         "merchantUserId": merchant_user_id,
    #         "subscriptionId": subscription_id,
    #         "authRequestId": auth_request_id,
    #         "paymentInstrument": {
    #             "type": "UPI_QR"
    #         }
    #     }
    else:
        raise ValueError("Invalid flow type")
    return payload

# Function to create headers with SHA256 and Base64 encoding
def create_headers(payload_base64):
    x_verify = generate_sha256(payload_base64, endpoint, salt_key) + "###" + salt_index
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": x_verify
    }
    return headers

# Function to make the API request
def make_request(merchant_user_id,subscription_id, flow_type,vpa):
    payload = create_payload(flow_type,merchant_user_id,subscription_id,vpa)
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    headers = create_headers(payload_base64)
    request_payload = json.dumps({"request": payload_base64})
    
    response = requests.post(url, headers=headers, data=request_payload)
    
#     print("Status Code:", response.status_code)
#     print("Response Body:", response.json())
#     #print("Base64 Payload:", payload_base64)
#    # print("SHA256 Hash:", generate_sha256(payload_base64, endpoint, salt_key))
#     print("authRequestId:", payload['authRequestId'])
    response_data = {
        "StatusCode": response.status_code,
        "ResponseBody": response.json(),
        "authRequestId": payload['authRequestId'],
    }
    return response_data

# # Choose the flow type (Intent, Collect, QR)
# flow_type = "Collect"  # Change this to "Intent" or "QR" as needed
# make_request(flow_type)
