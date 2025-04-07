#!/bin/bash
# run.sh: A script to set up and run the project locally.

# Activate the virtual environment.
source env/bin/activate

# Start the FastAPI server using uvicorn.
echo "Starting server..."
python -m uvicorn app:app --reload
