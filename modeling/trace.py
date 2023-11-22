import torch
import json
from sentence_transformers import SentenceTransformer
from transformers import AutoConfig

# Load your fine-tuned model
with open('config.json') as config_file:
    config = json.load(config_file)
    
MODEL_STRING = config.get("model_string")
MAX_LENGTH = config.get("max_length")

def load_sentence_model(model_string):
    sentence_model = SentenceTransformer(model_string)
    tokenizer = sentence_model.tokenizer
    config = AutoConfig.from_pretrained(model_string)
    sentence_model.config = config
    return sentence_model

model = load_sentence_model(MODEL_STRING)
tokenizer = model.tokenizer

input_text = "test text"
inputs = tokenizer.encode_plus(input_text, max_length=MAX_LENGTH, truncation=True, return_tensors='pt')
inputs = {k:v for k,v in inputs.items()}

traced_model = torch.jit.trace(model, (inputs,), strict=False)
# traced_model = torch.jit.trace(model, example_kwarg_inputs=inputs)

traced_model.save("model_traced.pt")
