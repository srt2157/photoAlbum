import json
import boto3
import requests

def getImagenamesFromElastic(keyword):
    data = json.dumps({
        'query': {'match':{'labels': keyword}}
    })
    res = requests.get(
        'https://search-photos-x4ifi7k73wn4zcrjj5dx2nndme.us-east-1.es.amazonaws.com/photos/_search',
        data=data,
        auth=('ccbd', 'Ccbd@2021'),
        headers={'Content-Type': 'application/json',}
    )
    
    respDict = json.loads(res.text)
    if 'hits' in respDict and 'hits' in respDict['hits']:
        hits = respDict['hits']['hits']
        imageNames = []
        for hit in hits:
            imageNames.append(hit['_source']['objectKey'])
        print('[imageNames] for', keyword, '[are]', imageNames)
        return imageNames
    else:
        return []

def lambda_handler(event, context):
    print('[event]', event)
    q = event['queryStringParameters']['q'].strip()
    print('[q]', q)
    
    keywords = []
    
    if len(q.split(' ')) == 1:
        keywords = [q]
    
    else:
        client = boto3.client('lex-runtime')
        resp = client.post_text(botName='photos_bot', botAlias='photos_bot_a', userId='12', inputText=q)
        
        if resp['intentName'] == 'SearchIntent':
            if resp['slots']['keywordA']:
                keywords.append(resp['slots']['keywordA'])
            if resp['slots']['keywordB']:
                keywords.append(resp['slots']['keywordB'])
    
    print('[keywords]', keywords)
    
    imageNames = []
    for keyword in keywords:
        imageNames += getImagenamesFromElastic(keyword)
    imageNames = list(set(imageNames))
    print('[imageNames]', imageNames)
    
    prefix = 'https://jcs2281-b2.s3.amazonaws.com/'
    imageNames = [prefix + img for img in imageNames]
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps({'imageNames': imageNames})
    }
