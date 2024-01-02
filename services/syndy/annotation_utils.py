import boto3
import json
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import pandas as pd

from utils import get_hash

def annotate_text(lambda_client, text):
    text_response = lambda_client.invoke(
        FunctionName=os.getenv("ANNOTATE_ARN"),
        InvocationType='RequestResponse',
        Payload=json.dumps(dict(
            openai_key=os.getenv("OPENAI_KEY"),
            text=text
        ))
    )
    response = json.loads(text_response['Payload'].read())
    response["text"] = text
    return response

def annotate_texts(lambda_client, texts):
    async def annotate_texts_async(texts):
        cpu_count = os.cpu_count() or 1
        with ThreadPoolExecutor(max_workers=cpu_count) as executor:
            loop = asyncio.get_event_loop()
            tasks = []

            for text in texts:
                task = loop.run_in_executor(executor, annotate_text, lambda_client, text)
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            return responses
    return asyncio.run(annotate_texts_async(texts))

def format_annotation_into_dfs(annotation):
    text = annotation["text"]
    text_id = get_hash(text)
    claims = annotation.get("claims", [])
    claim_ids = [get_hash(claim) for claim in claims]
    topics = annotation.get("topics", [])
    topic_ids = [get_hash(topic) for topic in topics]
    
    q = pd.DataFrame(dict(query=[text], query_id=[text_id]))
    c_qrels = pd.DataFrame(dict(query_id=[text_id]*len(claim_ids), target_id=claim_ids))
    t_qrels = pd.DataFrame(dict(query_id=[text_id]*len(topic_ids), target_id=topic_ids))
    c_targs = pd.DataFrame(dict(target_id=claim_ids, target=claims))
    t_targs = pd.DataFrame(dict(target_id=topic_ids, target=topics))
    
    return q, c_qrels, t_qrels, c_targs, t_targs
    
def format_annotations(annotations):
    formatted_annotations = [format_annotation_into_dfs(ann) for ann in annotations]
    q = pd.concat([ann[0] for ann in formatted_annotations]).drop_duplicates(ignore_index=True)
    c_qrels = pd.concat([ann[1] for ann in formatted_annotations]).drop_duplicates(ignore_index=True)
    t_qrels = pd.concat([ann[2] for ann in formatted_annotations]).drop_duplicates(ignore_index=True)
    c_targs = pd.concat([ann[3] for ann in formatted_annotations]).drop_duplicates(ignore_index=True)
    t_targs = pd.concat([ann[4] for ann in formatted_annotations]).drop_duplicates(ignore_index=True)
    
    return q, c_qrels, t_qrels, c_targs, t_targs