#!/bin/bash

if [ -f "deployment.zip" ]; then
    echo "Removing existing deployment.zip"
    rm "deployment.zip"
fi

if [ -d "packages" ]; then
    echo "Removing existing packages/"
    rm -rf "packages"
fi

echo "Creating packages directory and downloading all dependencies"
mkdir packages
pip install -r requirements.txt -t packages/

echo "Zipping contents of packages/ into deployment.zip"
cd packages
zip -r ../deployment.zip .
cd ..

echo "Adding ext* files to deployment.zip"
zip deployment.zip ext*

echo "Process completed."
