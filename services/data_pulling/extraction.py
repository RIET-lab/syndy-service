import os
import re
import openai

def clean_gpt_output(text):
    return text.strip("\n").strip()

def parse_numbered_list(text, minlen=1):
    REGEX_STRING = "(^|\n)[0-9]*[\.\)]"
    bullets = re.split(REGEX_STRING, text)
    bullets = map(clean_gpt_output, bullets)
    return list(filter(lambda t: len(t) > minlen, bullets))

class Extraction:
    def extraction_prompt(self, prompt_args):
        raise NotImplementedError("Need to implement extraction prompt method")
    
    def _setup_model_args(self, model_args):
        gpt_model_args = dict(
            model="text-davinci-003",
            temperature=0.3,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0        
        )
        gpt_model_args.update(model_args)
        return gpt_model_args
        
    def _parse_response(self, response, parse_args):
        completion = response.choices[0].text
        return parse_numbered_list(completion, minlen=parse_args["minlen"])
    
    def get_extraction(self, 
                       api_key, 
                       prompt_args,
                       model_args=dict(),
                       minlen=5):
        openai.api_key = api_key
        prompt = self.extraction_prompt(prompt_args)
        model_args.update(prompt)
        gpt_model_args = self._setup_model_args(model_args)
        model_cls = openai.Completion if not "turbo" in gpt_model_args.get("model") \
            else openai.ChatCompletion
        response = model_cls.create(**gpt_model_args)
        outputs = self._parse_response(response, dict(minlen=minlen))
        return dict(
            prompt_inputs=prompt_args,
            prompt=prompt,
            outputs=outputs
        )

class ChatExtraction(Extraction):
    def _setup_model_args(self, model_args):
        gpt_model_args = dict(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0        
        )
        gpt_model_args.update(model_args)
        return gpt_model_args
    
    def _parse_response(self, response, parse_args):
        completion = response.choices[0].message.content
        return dict(
            completion=completion,
            outputs=parse_numbered_list(completion, minlen=parse_args["minlen"])
        )

class SocialMediaClaimTopicExtraction(ChatExtraction):
    def system_content(self, prompt_args):
        system_content = ("You are a system designed to extract topics and claims from social media posts, "
                          "following each of these rules with no exceptions.\n\n"
                          "Rules:\n"  
                          "- You should write all outputs as numbered lists\n"
                          "- Claims and topics should be as concise as possible\n"
                          "- Do not write more topics or claims than you need\n"
                          "- Claims should not reference the post or poster it was extracted from\n"
                          "- Claims should only be arguments presented in the post written plainly\n"
                          "- Claims need not be factual and may include opinions\n"
                          "- Ignore claims that require additional context or assumptions to be understood\n"
                          "- Ignore anecdotes or claims that aren't generalizable\n"
                          "- Do not include claims that break the rules\n\n"
                          "Output should look like:\n"
                          "Topics:\n"
                          "1. <Topic 1>\n"
                          "etc...\n\n"
                          "Claims:\n"
                          "1. <Claim 1>\n"
                          "etc...")
        return system_content
    
    def extraction_prompt(self, prompt_args):
        post = prompt_args.get("post")
        system_content = self.system_content(prompt_args)
        # user_content = ("\n" + "-"*50 + "\n").join([self.post_string(post) for post in posts])
        user_content = f"Post: \"{post}\""
        
        return dict(messages=[
            dict(role="system", content=system_content),
            dict(role="user", content=user_content)
        ])
    
    def _parse_response(self, response, parse_args):
        completion = response.choices[0].message.content
        try:
            topics_nl, claims_nl = completion.split("\n\n")
            topics_nl = topics_nl.replace("Topics:", "")
            topics_nl = parse_numbered_list(topics_nl)
            claims_nl = claims_nl.replace("Claims:", "")
            claims_nl = parse_numbered_list(claims_nl)
            return dict(topics=topics_nl, claims=claims_nl, completion=completion)
        
        except Exception as e:
            return dict(completion=completion)
        
class RelatedClaimExtraction(ChatExtraction):
    def extraction_prompt(self, prompt_args):
        claim = prompt_args.get("claim")
        top_n = prompt_args.get("top_n", 3)
        system_content = (f"You are a system designed to find premises or claims that may support, undermine or "
                          f"be a duplicate of the given claim, following each of these rules with no exceptions.\n\n"
                          f"Rules:\n"
                          f"- You should output a numbered list\n"
                          f"- All premises should be unique in writing style and phrasing \n"
                          f"- Ignore premises that require additional context or assumptions to be understood\n"
                          f"- All premises should not use ambiguous language or vague pronouns\n"
                          f"- List upto {top_n} premises for each category- it is preferred to return less rather than lower quality premises\n"
                          f"- Outputs should output in order of Duplicate, Supporting, and then Undermining\n"
                          f"- Do not include premises that break the rules\n\n"
                          f"Outputs should look like:\n"
                          f"Duplicate Premises:\n"
                          f"1. <Duplicate Premise 1>\n"
                          f"etc...\n\n"
                          f"Supporting Premises:\n"
                          f"1. <Supporting Premise 1>\n"
                          f"etc...\n\n"
                          f"Undermining Premises:\n"
                          f"1. <Undermining Premise 1>\n"
                          f"etc...")             
        user_content = f"Claim: \"{claim}\""
        return dict(messages=[
            dict(role="system", content=system_content),
            dict(role="user", content=user_content)
        ])
        
    def _parse_response(self, response, parse_args):
        completion = response.choices[0].message.content
        portion_map = dict(
            duplicate="Duplicate Premises:",
            support="Supporting Premises:",
            undermine="Undermining Premises:"
        )
        try:
            duplicate_nl, support_nl, undermine_nl = "", "", ""
            for portion in completion.split("\n\n"):
                if portion_map["duplicate"] in portion:
                    duplicate_nl = portion
                elif portion_map["support"] in portion:
                    support_nl = portion
                elif portion_map["undermine"] in portion:
                    undermine_nl = portion
            
            duplicate_nl = duplicate_nl.replace("Duplicate Premises:", "")
            duplicate_nl = parse_numbered_list(duplicate_nl)
            
            support_nl = support_nl.replace("Supporting Premises:", "")
            support_nl = parse_numbered_list(support_nl)
            
            undermine_nl = undermine_nl.replace("Undermining Premises:", "")
            undermine_nl = parse_numbered_list(undermine_nl)
            
            return dict(
                    duplicate=duplicate_nl, 
                    support=support_nl, 
                    undermine=undermine_nl,
                    completion=completion
                )
        except Exception as e:
            return dict(completion=completion)
        
class RelatedAndUnrelatedClaimExtraction(RelatedClaimExtraction):
    def _setup_model_args(self, model_args):
        gpt_model_args = dict(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0        
        )
        gpt_model_args.update(model_args)
        return gpt_model_args
    
    def extraction_prompt(self, prompt_args):
        claim = prompt_args.get("claim")
        top_n = prompt_args.get("top_n", 3)
        system_content = (f"You are a system designed to produce claims, sentences, or posts that may support, undermine or "
                          f"have no association to the given claim, following each of these rules with no exceptions.\n\n"
                          f"Rules:\n"
                          f"- You should output a numbered list\n"
                          f"- All sentences should be unique in writing style and phrasing \n"
                          f"- Ignore sentences that require additional context or assumptions to be understood\n"
                          f"- All sentences should not use ambiguous language or vague pronouns\n"
                          f"- List upto {top_n} sentences for each category- it is preferred to return less rather than lower quality ones\n"
                          f"- Outputs should output in order of Unrelated, Supporting, and then Undermining\n"
                          f"- Do not include sentences that break the rules\n\n"
                          f"Outputs should look like:\n"
                          f"Unrelated Premises:\n"
                          f"1. <Unrelated Premise 1>\n"
                          f"etc...\n\n"
                          f"Supporting Premises:\n"
                          f"1. <Supporting Premise 1>\n"
                          f"etc...\n\n"
                          f"Undermining Premises:\n"
                          f"1. <Undermining Premise 1>\n"
                          f"etc...")             
        user_content = f"Claim: \"{claim}\""
        return dict(messages=[
            dict(role="system", content=system_content),
            dict(role="user", content=user_content)
        ])
        
    def _parse_response(self, response, parse_args):
        completion = response.choices[0].message.content
        portion_map = dict(
            none="Unrelated Premises:",
            support="Supporting Premises:",
            undermine="Undermining Premises:"
        )
        try:
            none_nl, support_nl, undermine_nl = "", "", ""
            for portion in completion.split("\n\n"):
                if portion_map["none"] in portion:
                    none_nl = portion
                elif portion_map["support"] in portion:
                    support_nl = portion
                elif portion_map["undermine"] in portion:
                    undermine_nl = portion
            
            none_nl = none_nl.replace("Unrelated Premises:", "")
            none_nl = parse_numbered_list(none_nl)
            
            support_nl = support_nl.replace("Supporting Premises:", "")
            support_nl = parse_numbered_list(support_nl)
            
            undermine_nl = undermine_nl.replace("Undermining Premises:", "")
            undermine_nl = parse_numbered_list(undermine_nl)
            
            return dict(
                    none=none_nl, 
                    support=support_nl, 
                    undermine=undermine_nl,
                    completion=completion
                )
        except Exception as e:
            return dict(completion=completion)

class KeywordExtraction(ChatExtraction):
    def system_content(self, prompt_args):
        system_content = ("You are a system designed to list keywords that could help search engines "
                          "looks for articles or posts associated with the given topic. All responses "
                          "should just be a numbered list of all keywords. Also have the first 3 keywords "
                          "be short, concise, and highly likely to return results of the topic.")
        return system_content
    
    def extraction_prompt(self, prompt_args):
        topic = prompt_args.get("topic")
        system_content = self.system_content(prompt_args)
        user_content = f"Topic: \"{topic}\""
        
        return dict(messages=[
            dict(role="system", content=system_content),
            dict(role="user", content=user_content)
        ])
    