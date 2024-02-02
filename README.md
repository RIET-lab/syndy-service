# Setup / Build
## Step 1: Create a `.env` file in the root directory with the following content:
```
OPENAI_KEY =

REDDIT_CLIENT_ID = 
REDDIT_CLIENT_SECRET = 
REDDIT_USER_AGENT = 
```

## Step 2: Zip up Lambda Code and generate deps:
I didnt want to store all dependencies in git nor the zipped lambda in its entirety. Workaround i did was just setup some shell scripts to do the packge handling and zipping. So for the labelling service run:
```
cd services/labeling
chmod +x setup_zip.sh
./setup_zip.sh
cd -
```
For the datapulling service run:
```
cd services/data_pulling
chmod +x setup_zip.sh
./setup_zip.sh
cd -
```

## Step 3: Creating the resources
Run
```
npm install package.json
cdk synth --all --profile <your_aws_profile>
cdk bootstrap --profile <your_aws_profile>
cdk deploy --all --profile <your_aws_profile>
```
Change `--all` to specific stack name if you want to deploy only one stack.

# Testing
## Lambda functions
I recommend just creating python environments using their respective `requirements.txt` files and running the lambda functions locally.

## SynDy service
If you have deployed the stacks, you can test the syndy service locally by first creating a `.env` file in `/services/syndy` with the following content:
```
OPENAI_KEY =

REDDIT_CLIENT_ID = 
REDDIT_CLIENT_SECRET = 
REDDIT_USER_AGENT = 

DATAPULL_ARN = 
ANNOTATE_ARN = 

DATASET_BUCKET = 

INFERENCE_URL =

AWS_ACCESS_KEY_ID = 
AWS_SECRET_ACCESS_KEY = 
```
note this is similar to root dir `.env` with some additions to hardcode the resources + aws credentials

Additionally, since in production the env is setup during resource creation, for local testing use `Dockerfile.test` to build the image and run the container. This will setup the env and run the service for local use.

# Notes
- A lot of the keys are handled via a `.env` file, I would reccomend migrating them to AWS Secrets Manager
- A huge performance bottleneck is running inference on a whole dataset during deduplication. Should be parallelized or compute optimized to speed up.
- The datapulling relies on PRAW which ratelimits with the wind, so finding future solutions will be helpful.
- SynDy asynchronously starts dataset creation using pythons threading, which is not ideal for production. I would reccomend using a queueing service like SQS or a message broker like RabbitMQ.


# Debugging / Troubleshooting
- If you are encountering permission errors after running `cdk deploy --all`, you may need to manually set file permissions for some of the files under `services/`. Run `chmod 755 xyz.py` for executables and `chmod 644 xyz.abc` for non-executables (e.g. config files).