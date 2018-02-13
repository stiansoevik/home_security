#!/bin/bash

echo "\n=== Arming === "
curl -i -X POST http://localhost:5000/send_event/ARM

echo "\n=== Sending user code ==="
curl -i -X POST http://localhost:5000/send_event/USER_CODE -d '{ "param": 1234 }' -H "Content-Type: application/json"
