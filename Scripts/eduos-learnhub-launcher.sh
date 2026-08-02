#!/bin/bash
/usr/bin/python3 /opt/eduos/LearnHub/learnhub_app.py &
sleep 2
xdg-open "http://localhost:5050"