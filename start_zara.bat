@echo off
title Zara Personal AI Server
cd /d "d:\personal assistant"
echo ====================================================
echo Starting Zara Personal AI Server...
echo Local URL: http://127.0.0.1:5000
echo ====================================================
start "" "http://127.0.0.1:5000"
python app.py
pause
