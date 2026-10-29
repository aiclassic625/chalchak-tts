#!/bin/sh
cd "$(dirname "$0")"
exec /tmp/zh_venv/bin/python tts_server.py
