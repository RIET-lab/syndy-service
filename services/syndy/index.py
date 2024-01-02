from flask import Flask, request
import boto3
from threading import Thread
import time
import numpy as np

from utils import *
from annotation_utils import *
from dataset_utils import *
from inference_utils import *

import dotenv
dotenv.load_dotenv()

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return {"success": True}

def _create_dataset(topic, queries_per_topic):
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    print(f"Creating dataset for topic: {topic}, with {queries_per_topic} queries per topic")
    t = time.time()
    print("Getting dataset...")
    texts = get_dataset(lambda_client, topic, queries_per_topic)
    print("Got Dataset. There are {} texts to annotate. took {} sec".format(len(texts), time.time() - t))
    t = time.time()
    print("Annotating texts...")
    annotations = annotate_texts(lambda_client, texts)
    formatted_dfs = format_annotations(annotations)
    print("Annotated texts. Took {} sec. Uploading to S3...".format(time.time() - t))
    t = time.time()
    upload_dataframes(topic, *formatted_dfs)
    print("Uploaded to S3. Took {} sec".format(time.time() - t))
    return {"success": True}

@app.route('/create_dataset', methods=['POST'])
def create_dataset():
    topic = request.form.get("topic")
    queries_per_topic = int(request.form.get("queries_per_topic", 1))
    Thread(target=_create_dataset, args=(topic, queries_per_topic)).start()
    return {"creation_started": True}

@app.route('/list_topics', methods=['GET'])
def list_topics_endpoint():
    s3_client = boto3.client('s3')
    bucket_name = os.getenv("DATASET_BUCKET")
    return {"topics": list_topics(s3_client, bucket_name)}

@app.route('/sample_dataset', methods=['GET'])
def get_dataset_sample():
    topic = request.args.get("topic").replace("_", " ")
    n = request.args.get("n", 10)
    
    q, c_qrels, t_qrels, c_targs, t_targs = get_dataset_from_s3(topic)
    claims_df = merge_dataset_dfs(q, c_qrels, c_targs)
    topics_df = merge_dataset_dfs(q, t_qrels, t_targs)
    chosen_qids = q.sample(n).query_id.to_list()
    queries = [q[q.query_id == qid]["query"].to_list()[0] for qid in chosen_qids]
    claims = [claims_df[claims_df.query_id == qid].target.to_list() for qid in chosen_qids]
    topics = [topics_df[topics_df.query_id == qid].target.to_list() for qid in chosen_qids]
    
    return {
        "queries": queries,
        "claims": claims,
        "topics": topics
    }
    
def _dedup_dataset(topic):
    q, c_qrels, t_qrels, c_targs, t_targs = get_dataset_from_s3(topic)
    c_targs, c_qrels = ClaimModelAnalyzer.remove_noisy_duplicates(c_targs, c_qrels)
    t_targs, t_qrels = ClaimModelAnalyzer.remove_noisy_duplicates(t_targs, t_qrels)
    
    upload_dataframes(topic, q, c_qrels, t_qrels, c_targs, t_targs, suffix="-deduped")
    return dict(
        success=True,
        prev_num_claims=len(c_targs),
        num_claims=len(c_targs),
        prev_num_topics=len(t_targs),
        num_topics=len(t_targs)
    )
    
@app.route('/dedup_dataset', methods=['POST'])
def dedup_dataset():
    topic = request.form.get("topic")
    if not topic:
        return {"success": False, "error": "No topic specified"}
    Thread(target=_dedup_dataset, args=(topic,)).start()
    return {"dedup_started": True}
    

if __name__ == '__main__':
    app.run(debug=True)
