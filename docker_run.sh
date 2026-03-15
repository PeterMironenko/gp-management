#!/bin/bash
docker run -d -p 5000:5000 -v "${PWD}":/app --name container-store-app-flask simple-store-app-flask:latest