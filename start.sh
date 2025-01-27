#!/bin/bash
# Start both processes
cat static/css/tailwind.css &
uvicorn main:app --host 0.0.0.0 --port "$PORT" &
sudo cloudflared service install "$TUNNEL_TOKEN" &

# Wait for background processes to finish
wait
