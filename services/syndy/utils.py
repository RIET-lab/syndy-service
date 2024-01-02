from io import StringIO
import hashlib
import boto3
import os
import pandas as pd

def get_hash(x):
    return str(hashlib.sha256(x.encode()).hexdigest())

def bodify_submission(submission):
    title = submission.get("title")
    body = submission.get("selftext")
    if title and body:
        return f"Title: {title}\n\nBody: {body}"
    elif title:
        return title
    else:
        return body
    
def upload_df_to_s3(
        s3_client, 
        bucket_name, 
        df,
        filename
    ):
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket_name, Key=filename, Body=csv_buffer.getvalue())
    
def upload_dataframes(topic, q, c_qrels, t_qrels, c_targs, t_targs, suffix=""):
    format_topic_name = lambda t: t.replace(" ", "_").replace("/", "_") + suffix
    
    s3_client = boto3.client('s3')
    bucket_name = os.getenv("DATASET_BUCKET")
    upload_df_to_s3(s3_client, bucket_name, q, f"{format_topic_name(topic)}-queries.csv")
    upload_df_to_s3(s3_client, bucket_name, c_qrels, f"{format_topic_name(topic)}-qrels-claims.csv")
    upload_df_to_s3(s3_client, bucket_name, t_qrels, f"{format_topic_name(topic)}-qrels-topics.csv")
    upload_df_to_s3(s3_client, bucket_name, c_targs, f"{format_topic_name(topic)}-targets-claims.csv")
    upload_df_to_s3(s3_client, bucket_name, t_targs, f"{format_topic_name(topic)}-targets-topics.csv")

def list_topics(s3_client, bucket_name):
    paginator = s3_client.get_paginator('list_objects_v2')

    topics = []
    for page in paginator.paginate(Bucket=bucket_name):
        if "Contents" in page:
            for obj in page['Contents']:
                suffix = "-queries.csv"
                if obj['Key'].endswith(suffix):
                    topics.append(obj['Key'][:-len(suffix)].replace("_", " "))
    return topics

def get_df_from_s3(filename):
    s3_path = f's3://{os.getenv("DATASET_BUCKET")}/{filename}'
    return pd.read_csv(s3_path)

def get_dataset_from_s3(topic, suffix=""):
    format_topic_name = lambda t: t.replace(" ", "_").replace("/", "_") + suffix
    q = get_df_from_s3(f"{format_topic_name(topic)}-queries.csv")
    c_qrels = get_df_from_s3(f"{format_topic_name(topic)}-qrels-claims.csv")
    t_qrels = get_df_from_s3(f"{format_topic_name(topic)}-qrels-topics.csv")
    c_targs = get_df_from_s3(f"{format_topic_name(topic)}-targets-claims.csv")
    t_targs = get_df_from_s3(f"{format_topic_name(topic)}-targets-topics.csv")
    return q, c_qrels, t_qrels, c_targs, t_targs

def merge_dataset_dfs(q, qrels, t):
    if q is not None:
        qrels.target_id = qrels.target_id.astype(str)
        t.target_id = t.target_id.astype(str)
        df = qrels.merge(q, on="query_id", how="inner").merge(t, on="target_id", how="inner")
        return df.drop_duplicates().reset_index(drop=True)
    else:
        return None
    