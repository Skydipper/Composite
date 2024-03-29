#!/bin/bash
set -e

case "$1" in
    develop)
        echo "Running Development Server"
        echo -e "$EE_PRIVATE_KEY" | base64 -d > privatekey.json
        exec python main.py
        ;;
    test)
        echo "Running tests"
        echo -e "$EE_PRIVATE_KEY" | base64 -d > privatekey.json
        exec pytest --cov=composite composite/tests/
        ;;
    start)
        echo "Running Start"
        echo -e "$EE_PRIVATE_KEY" | base64 -d > privatekey.json
        exec gunicorn -c gunicorn.py composite:app
        ;;
    *)
        exec "$@"
esac
