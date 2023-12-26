from extraction import SocialMediaClaimTopicExtraction as Extractor

def handle(event, context):
    extractor = Extractor()
    openai_key = event["openai_key"]
    text = event["text"]
    outputs = extractor.get_extraction(openai_key, dict(post=text))["outputs"]
    return outputs 