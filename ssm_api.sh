#!/bin/bash

read -d '' json_data
url="http://127.0.0.1:8000/start_research"
content_type="Content-Type: application/json"
response=$(curl -s -X POST "$url" -H "$content_type" -d "$json_data")
echo "Response from server: $response"
