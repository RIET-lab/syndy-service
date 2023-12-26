import json
import torch
from ts.torch_handler.base_handler import BaseHandler
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class Handler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load config.json
        with open('config.json') as config_file:
            config = json.load(config_file)

        # Use a value from the config file
        self.MAX_LENGTH = config.get("max_length")
        self.MODEL_STRING = config.get("model_string")

        # Initialize the tokenizer
        
    def initialize(self, context):
        self.manifest = context.manifest

        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        # Read model serialize/pt file
        self.model = SentenceTransformer(self.MODEL_STRING)
        self.tokenizer = self.model.tokenizer

        self.model.to(self.device)
        self.model.eval()

        logger.debug('Transformer model from path {0} loaded successfully'.format(model_dir))

        self.initialized = True

    def preprocess(self, data):
        input_text = data[0].get("data")
        if input_text is None:
            input_text = data[0].get("body")

        if type(input_text) == bytearray:
            input_text = input_text.decode()
        
        inputs = self.tokenizer.encode_plus(input_text, max_length=self.MAX_LENGTH, return_tensors='pt')
        return inputs

    def postprocess(self, output):
        return output.get("sentence_embedding").detach().numpy().tolist()

    def handle(self, data, context):
        if not data:
            return {"result": "No data received"}
        with torch.no_grad():
            model_output = self.model(self.preprocess(data))
        response = self.postprocess(model_output)
        return response