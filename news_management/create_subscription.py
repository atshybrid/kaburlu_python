import json
import base64
import uuid
import hashlib
import requests

# Function to generate a unique identifier
def generate_unique_id(prefix):
    return f"{prefix}{uuid.uuid4().hex}"

# Function to compute the X-Verify header value
def compute_x_verify(payload_base64, endpoint, salt_key, salt_index):
    combined_string = payload_base64 + endpoint + salt_key
    sha256_hash = hashlib.sha256(combined_string.encode()).hexdigest()
    return f"{sha256_hash}###{salt_index}"

# Initialize the mobile to merchant user ID mapping
mobile_to_user_id = {}

# Endpoint and salt information
endpoint = "/v3/recurring/subscription/create"
salt_key = "5d8b52ef-95c2-4b00-afda-d919207624de"
salt_index = 1

# Function to create and send the subscription request
def create_subscription(mobile_number, amount, recurring_count):
    print("duivjneg",mobile_number, amount, recurring_count)
    # Check if the mobile number already exists
    if mobile_number in mobile_to_user_id:
        merchant_user_id = mobile_to_user_id[mobile_number]
    else:
        merchant_user_id = generate_unique_id("KB")
        mobile_to_user_id[mobile_number] = merchant_user_id
    
    # Always generate a new merchant subscription ID
    merchant_subscription_id = generate_unique_id("OMS")
    
    # Create the JSON payload
    payload = {
        "merchantId": "AMOGHNYAONLINE",
        "merchantSubscriptionId": merchant_subscription_id,
        "merchantUserId": merchant_user_id,
        "authWorkflowType": "PENNY_DROP",
        "amountType": "FIXED",
        "amount": amount,
        "frequency": "DAILY",
        "recurringCount": recurring_count,
        "mobileNumber": mobile_number,
        "deviceContext": {
            "phonePeVersionCode": 400922
        }
    }
    
    # Convert payload to JSON and then encode it in base64
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode()).decode()
    
    # Create the request payload
    request_payload = json.dumps({"request": payload_base64})
    
    # Compute the X-Verify header value
    x_verify = compute_x_verify(payload_base64, endpoint, salt_key, salt_index)
    
    # Set the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Verify': x_verify
    }
    
    # Production base URL
    base_url = "https://mercury-t2.phonepe.com"
    
    # Send the request
    response = requests.post(base_url + endpoint, headers=headers, data=request_payload)
    response_data = {
        "StatusCode": response.status_code,
        "ResponseBody": response.text,
        "MerchantUserID": merchant_user_id,
        "MerchantSubscriptionID": merchant_subscription_id
    }
    return response_data
    