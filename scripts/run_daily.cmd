@echo off
set REPO=%~dp0..
cd /d "%REPO%"
if not exist logs mkdir logs
py -3 main.py 1>> logs\run.log 2>> logs\error.log
