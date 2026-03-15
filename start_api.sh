#!/bin/bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask --app app run --host 0.0.0.0 -p 8888 --debug