from langdetect import detect
import random

def reddit_query_generator(terms, n_strong_terms=None):
    if n_strong_terms:
        strong_terms, weak_terms = terms[:n_strong_terms], terms[n_strong_terms:]    
        chosen_strong_term = random.sample(strong_terms, 1)
        chosen_weak_terms = random.sample(weak_terms, 2)
        chosen_terms = map(lambda x: f"\"{x}\"" if " " in x else x, chosen_strong_term + chosen_weak_terms)
    else:
        chosen_terms = random.sample(terms, min(3, len(terms)))
        chosen_terms = map(lambda x: f"\"{x}\"" if " " in x else x, chosen_terms)
        
    return " ".join(chosen_terms)

def search_reddit_submissions(reddit_client, query, lang="en", limit=100, verbose=True):
    if isinstance(query, str): query = [query]
    all = reddit_client.subreddit("all")
    
    submissions = set()
    for _query in query:
        for submission in all.search(_query, limit=limit):
            try:
                if detect(submission.title) == lang: submissions.add(submission)
            except:
                continue
    return submissions

def bodify_submission(submission):
    title = submission.get("title")
    body = submission.get("selftext")
    if title and body:
        return f"Title: {title}\n\nBody: {body}"
    elif title:
        return title
    else:
        return body
    
def submission_dict(submission):
    values = dict()
    accepted_types = [dict, list, str, int, float, bool, type(None)]
    
    for attr in dir(submission):
        if attr.startswith("_"):
            continue
        
        val = getattr(submission, attr)
        if type(val) in accepted_types:
            values[attr] = val
    
    return values

def bodify_submission_object(submission):
    title = submission.title if hasattr(submission, "title") else None
    body = submission.selftext if hasattr(submission, "selftext") else None
    if title and body:
        return f"Title: {title}\n\nBody: {body}"
    elif title:
        return title
    else:
        return body


    