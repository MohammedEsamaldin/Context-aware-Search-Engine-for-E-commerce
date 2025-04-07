#!/bin/bash
# run.sh: A script to set up and run the project locally.

# Start the FastAPI server using uvicorn.
echo "Starting server..."
uvicorn app:app --reload
