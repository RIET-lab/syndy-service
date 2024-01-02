import requests
import os
import json
import numpy as np
from collections import defaultdict
import math

def _run_inference(texts):
    url = os.getenv("INFERENCE_URL")
    response = requests.post(url, data=dict(data=json.dumps(texts)))
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return response.status_code, response.content
    
def run_inference(texts):
    if not isinstance(texts, list):
        texts = [texts]
    
    LIMIT = 64
    nsteps = math.ceil(len(texts) / LIMIT)
    outputs = []
    for i in range(nsteps):
        try:
            run = _run_inference(texts[i*LIMIT:(i+1)*LIMIT])
            outputs.extend(run)
        except:
            return run
    return outputs

class ClaimModelAnalyzer:
    
    @staticmethod
    def get_scores(claims):
        encoded_claims = run_inference(claims)
        encoded_claims = np.array(encoded_claims).astype(dtype=np.float32)
        scores = encoded_claims @ encoded_claims.T
        return scores
    
    @classmethod
    def get_duplicates(cls, claims, threshold=0.95):
        scores = cls.get_scores(claims)
        scores = np.triu(scores, k=1)
        duplicate_inds = np.where(scores >= threshold)
        
        duplicates = defaultdict(set)
        vals = set(range(len(claims)))
        redirects = {}
        for i, j in zip(*duplicate_inds):
            ival = i if i in vals else redirects[i]
            
            if j in vals:
                duplicates[ival].add(j)
                vals.remove(j)
                redirects[j] = ival
            elif redirects[j] != ival:                
                duplicates[redirects[j]].update(duplicates[ival])
                redirects[ival] = redirects[j]
                if ival in duplicates.keys(): del duplicates[ival]
        
        return duplicates
    
    @classmethod
    def remove_noisy_duplicates(cls, values, qrels, qrel_col="target", threshold=0.95):
        """Remove noisy duplicates from a dataframe of qrels. Noisy duplicated based on similarity 
        scores. values is either targets_df or queries_df.
        """
        # values = values[values[qrel_col+"_id"].isin(qrels[qrel_col+"_id"])]
        values_id_list = values[qrel_col+"_id"].to_list()
        values_list = values[qrel_col].to_list()
        
        duplicates = cls.get_duplicates(values_list, threshold=threshold)
        all_v_ids = set()
        for k, v in duplicates.items():
            k_id = values_id_list[k]
            v_ids = set([values_id_list[i] for i in v])
            all_v_ids.update(v_ids)
            
            if isinstance(qrels, list):
                for q in qrels:
                    q.loc[q[qrel_col+"_id"].isin(v_ids), qrel_col+"_id"] = k_id
            else:
                qrels.loc[qrels[qrel_col+"_id"].isin(v_ids), qrel_col+"_id"] = k_id
        
        values = values[~values[qrel_col+"_id"].isin(all_v_ids)].reset_index(drop=True)
        return values, qrels
                
            