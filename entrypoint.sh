#!/bin/bash
set -e

case "$1" in
    develop)
        echo "Running Development Server"
        exec python main.py
        ;;
    test)
        echo "Running tests"
        exec pytest --cov=composite composite/tests/
        ;;
    start)
        echo "Running Start"
        exec gunicorn -c gunicorn.py composite:app
        ;;
    *)
        exec "$@"
esac
