import praw
import time
from extraction import KeywordExtraction
from utils import reddit_query_generator, search_reddit_submissions, bodify_submission, submission_dict

def handle(event, context):
    """Args:
        event: 
        {
            reddit: {
                REDDIT_CLIENT_ID: str,
                REDDIT_CLIENT_SECRET: str,
                REDDIT_USER_AGENT: str
            },
            openai_key: str,
            topic: str,
            queries_per_topic: int
        }
        context: ignore
    """
    kw_extractor = KeywordExtraction()
    reddit_credentials = dict(
        client_id=event["reddit"].get("REDDIT_CLIENT_ID"),
        client_secret=event["reddit"].get("REDDIT_CLIENT_SECRET"),
        user_agent=event["reddit"].get("REDDIT_USER_AGENT"),
    )
    reddit_client = praw.Reddit(**reddit_credentials)
    
    openai_key = event["openai_key"]
    topic = event["topic"]
    keywords = kw_extractor.get_extraction(openai_key, dict(topic=topic))["outputs"].get("outputs")
    
    queries_per_topic = event.get("queries_per_topic", 10)
    topic_qs = [reddit_query_generator(keywords, n_strong_terms=3) for i in range(queries_per_topic)]
    trials = 0
    while True:
        try:
            topic_submissions = search_reddit_submissions(reddit_client, topic_qs, limit=1000)
            break
        except Exception as e:
            trials += 1
            if trials > 3:
                raise ValueError("failed to search reddit with error {e}")
            time.sleep(1.0)
    
    submissions = [submission_dict(submission) for submission in topic_submissions]
    return dict(
        submissions=submissions
    )
