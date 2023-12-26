# Step 1: Zip up Lambda Code and generate deps:
Run
```
cd services/labeling
chmod +x setup_zip.sh
./setup_zip.sh
```

# Step 2: Deploy Lambda Code and generate deps:
Run
```
cdk synth --all
cdk bootstrap
cdk deploy --all
```
Change `--all` to specific stack name if you want to deploy only one stack.
