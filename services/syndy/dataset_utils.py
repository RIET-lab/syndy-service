import boto3
import json
import os

def get_dataset(lambda_client, topic, queries_per_topic):
    response = lambda_client.invoke(
        FunctionName=os.getenv("DATAPULL_ARN"),
        InvocationType='RequestResponse',
        Payload=json.dumps(dict(
            reddit=dict(
                REDDIT_CLIENT_ID=os.getenv("REDDIT_CLIENT_ID"),
                REDDIT_CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET"),
                REDDIT_USER_AGENT=os.getenv("REDDIT_USER_AGENT")
            ),
            openai_key=os.getenv("OPENAI_KEY"),
            topic=topic,
            queries_per_topic=queries_per_topic
        ))
    )

    payload = json.loads(response['Payload'].read()).get("submissions", [])
    return payload