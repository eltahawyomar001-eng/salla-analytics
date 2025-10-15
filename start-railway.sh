#!/bin/bash
# Startup script for Railway deployment

# Use Railway's PORT environment variable, default to 8501
PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT"

# Run Streamlit
streamlit run app/main.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
