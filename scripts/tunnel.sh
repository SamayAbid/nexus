#!/usr/bin/env bash
# Starts ngrok static domain tunnel to FastAPI
# Requires: NGROK_AUTHTOKEN env var and NGROK_DOMAIN env var
ngrok http --domain="${NGROK_DOMAIN}" 8000
