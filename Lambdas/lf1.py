import json
import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    print('[event]', event)
    r = event['Records'][0]
    bucketName = r['s3']['bucket']['name']
    imageName = r['s3']['object']['key']
    
    print('[recognizing]', imageName, '[in]', bucketName)
    
    client = boto3.client('rekognition')
    
    response = client.detect_labels(
                Image={'S3Object':{'Bucket': bucketName,'Name': imageName}},
                MaxLabels=50
            )
    
    label_lst = [label['Name'] for label in response['Labels']]
    print('[recognized labels]:', label_lst)
    
    s3 = boto3.client('s3', region_name='us-east-1')
    head_res = s3.head_object(Bucket=bucketName, Key=imageName)
    print('[head_res]', head_res)
    custom_labels = []
    try:
        custom_labels = head_res['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(',')
    except:
        pass
    
    print('[custom labels]', custom_labels)
    
    labels = list(set([x.lower() for x in (label_lst + custom_labels)]))
    print('[labels]', labels)
    
    data = {
        'objectKey': imageName,
        'bucket': bucketName,
        'createdTimestamp': str(datetime.now()),
        'labels': labels
    }
    data = json.dumps(data)
    response = requests.put(
        'https://search-photos-x4ifi7k73wn4zcrjj5dx2nndme.us-east-1.es.amazonaws.com/photos/_doc/'+imageName,
        headers={'Content-Type': 'application/json'},
        data=data,
        auth=('ccbd', 'Ccbd@2021')
    )
    
    print('[elastic response]:', response.text)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
