import json
import boto3
from boto3.session import Session


session = boto3.Session() # 환경변수로 이미 값 등록해 둠
ec2_client = session.client('ec2') # AWS_SERVICE_NAME
response = ec2_client.describe_instances()

InstanceDatas = []
for Reservation in response['Reservations']:
    for Instance in Reservation['Instances']:
        if Instance['State']['Name'] != 'running': print("no running instance")
        NameTag = next((item for item in Instance['Tags'] if item['Key'] == 'Name'), {}).get('Value', '')
        InstanceDatas.append({
            'NameTag': NameTag,
            'InstanceId' : Instance['InstanceId'],
        })

print(response)
print()
print('InstanceDatas:', json.dumps(InstanceDatas, indent=4))