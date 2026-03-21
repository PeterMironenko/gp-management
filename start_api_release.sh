#!/bin/bash
port=$1

if [ -z "$port" ]; then
    port=5000
    echo "No port specified. Using default port $port."
fi


export FLASK_APP=app.py
flask --app app run --host 0.0.0.0 -p $port