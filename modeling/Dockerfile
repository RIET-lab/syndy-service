FROM pytorch/torchserve:latest

RUN pip install torchserve torch-model-archiver transformers sentence_transformers

# Set up the model store and copy the model
RUN mkdir -p /home/model-server/model-store
COPY handler.py config.json trace.py /home/model-server/model-store/
RUN cd /home/model-server/model-store && python trace.py

# Archive the model to .mar format for TorchServe
RUN torch-model-archiver --model-name test-sentence-transformer \
    --version 1.0 \
    --serialized-file /home/model-server/model-store/model_traced.pt \
    --handler /home/model-server/model-store/handler.py \
    --extra-files /home/model-server/model-store/config.json \
    --export-path /home/model-server/model-store

# Set up the entry point for TorchServe
CMD ["torchserve", \
     "--start", \
     "--ncs", \
     "--model-store", "/home/model-server/model-store", \
     "--models", "test-sentence-transformer.mar"]
