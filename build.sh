#!/bin/bash
set -e
apt-get update
apt-get install -y golang-go
pip install --upgrade pip
pip install -r requirements.txt
