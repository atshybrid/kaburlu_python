import boto3
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import tempfile

# def upload(file_path,folder_name):
#     endpoint_url = "https://kaburlu.blr1.digitaloceanspaces.com"
#     session = boto3.session.Session()
#     client = session.client('s3',endpoint_url=endpoint_url, region_name='blr1',aws_access_key_id='DO004ZRZ6PZLG9KVM3BE',aws_secret_access_key='6o1+PcGB4h7LbtZqapsq/igOH/ecXAxGZ1gL1pzBRgg')
#     if isinstance(file_path, InMemoryUploadedFile):
#         print("jhyifh")
#         # If the file is uploaded via Django form
#         with tempfile.NamedTemporaryFile() as temp_file:
#             temp_file.write(file_path.read())
#             temp_file.flush()
#             with open(temp_file.name, 'rb') as file:
#                 file_content = file.read()
#                 # your remaining code for uploading
#         client.put_object(Bucket='kaburlu-space-name', Key=f'kaburlu/{folder_name}/{file_path}', Body=file_content,ACL='public-read', Metadata={'x-amz-meta-my-key': 'your-value'},ContentDisposition='inline',ContentType='image/png')
#         url = endpoint_url+f"/kaburlu-space-name/kaburlu/{folder_name}/{file_path.name.replace(' ', '%20')}"
#         return url
#     else:
#         print("dnfjgwf")
#         file_name = os.path.basename(file_path)
#         # If the file is already on disk
#         with open(file_path, 'rb') as file:
#             file_content = file.read()
#         client.put_object(Bucket='kaburlu-space-name', Key=f'kaburlu/{folder_name}/{file_name}', Body=file_content,ACL='public-read', Metadata={'x-amz-meta-my-key': 'your-value'},ContentDisposition='inline',ContentType='image/png')
#         url = endpoint_url+f"/kaburlu-space-name/kaburlu/{folder_name}/{file_name.replace(' ', '%20')}"
#         return url

def upload(file_path,folder_name):
    check_file = file_path.name.split(".")
    endpoint_url = "https://kaburlu.blr1.digitaloceanspaces.com"
    session = boto3.session.Session()
    client = session.client('s3',endpoint_url=endpoint_url, region_name='blr1',aws_access_key_id='DO004ZRZ6PZLG9KVM3BE',aws_secret_access_key='6o1+PcGB4h7LbtZqapsq/igOH/ecXAxGZ1gL1pzBRgg')    
    file_name = os.path.basename(file_path.name)
    with file_path.open('rb') as file:
        file_content = file.read()
    client.put_object(Bucket='kaburlu-space-name', Key=f'kaburlu/{folder_name}/{file_name}', Body=file_content,ACL='public-read', Metadata={'x-amz-meta-my-key': 'your-value'},ContentDisposition='inline',ContentType=f'image/{check_file[-1].lower()}')
    url = endpoint_url+f"/kaburlu-space-name/kaburlu/{folder_name}/{file_name.replace(' ', '%20')}"
    return url