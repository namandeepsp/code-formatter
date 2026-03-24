#!/bin/bash
set -e
apt-get update
apt-get install -y golang-go default-jre default-jdk
pip install --upgrade pip
pip install -r requirements.txt

# Download Google Java Format
if [ ! -f "google-java-format.jar" ]; then
  curl -L https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar -o google-java-format.jar
fi
