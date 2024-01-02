import praw
import time
from extraction import KeywordExtraction
from utils import reddit_query_generator, search_reddit_submissions, bodify_submission_object
import time

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
    reddit_credentials = dict(
        client_id=event["reddit"].get("REDDIT_CLIENT_ID"),
        client_secret=event["reddit"].get("REDDIT_CLIENT_SECRET"),
        user_agent=event["reddit"].get("REDDIT_USER_AGENT"),
    )
    reddit_client = praw.Reddit(**reddit_credentials)
    
    topic = event["topic"]    
    openai_key = event["openai_key"]    
    kw_extractor = KeywordExtraction()
    t0 = time.time()
    keywords = kw_extractor.get_extraction(openai_key, dict(topic=topic))["outputs"].get("outputs")
    print(f"keyword extraction took {time.time() - t0} seconds")
    t0 = time.time()
    
    queries_per_topic = event.get("queries_per_topic", 1)
    topic_qs = [reddit_query_generator(keywords, n_strong_terms=3) for i in range(queries_per_topic)]
    print(f"took {time.time()-t0} seconds to generate {queries_per_topic} queries for topic {topic}")
    t0 = time.time()
    
    trials = 0
    while True:
        try:
            topic_submissions = search_reddit_submissions(reddit_client, topic_qs, limit=200)
            break
        except Exception as e:
            trials += 1
            if trials > 3:
                raise ValueError("failed to search reddit with error {e}")
            time.sleep(1.0)
    print(f"took {time.time()-t0} seconds to generate {len(topic_submissions)} submissions for topic {topic}")
    t0 = time.time()
    
    submissions = [bodify_submission_object(submission) for submission in topic_submissions]
    print(f"took {time.time()-t0} seconds to bodify all submissions")
    return dict(
        submissions=submissions
    )
