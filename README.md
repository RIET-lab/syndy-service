# Step 1: Zip up Lambda Code and generate deps:
For the labelling service run:
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

# Step 2: Deploy Lambda Code and generate deps:
Run
```
cdk synth --all
cdk bootstrap
cdk deploy --all
```
Change `--all` to specific stack name if you want to deploy only one stack.
