#!/bin/bash
set -e

cd /home/user/myproject
wmill workspace switch myworkspace

RUN_ID="${ZEALT_RUN_ID:-zr-12345}"
SANITIZED_RUN_ID=$(echo "$RUN_ID" | tr '-' '_')

# 1. Resource Type
cat << JSON > rt.json
{
  "\$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "apiUrl": {
      "type": "string"
    },
    "token": {
      "type": "string",
      "format": "password"
    }
  },
  "required": ["apiUrl", "token"]
}
JSON
wmill resource-type push rt.json "my_api_creds_${SANITIZED_RUN_ID}"

# 2. Resource
cat << JSON > res.json
{
  "value": {
    "apiUrl": "https://api.example.com/${RUN_ID}",
    "token": "secret_token_value"
  },
  "resource_type": "my_api_creds_${SANITIZED_RUN_ID}",
  "description": "API credentials for run ${RUN_ID}"
}
JSON
wmill resource push res.json "f/zealt/creds_${SANITIZED_RUN_ID}"

# 3. Script
cat << TS > script.ts
import * as wmill from "windmill-client";

export async function main() {
  const res = await wmill.getResource("f/zealt/creds_${SANITIZED_RUN_ID}");
  return res.apiUrl;
}
TS
wmill script push script.ts "f/zealt/read_api_url_${SANITIZED_RUN_ID}"

# 4. Run the script
OUTPUT=$(wmill script run "f/zealt/read_api_url_${SANITIZED_RUN_ID}")
echo "Raw output:"
echo "$OUTPUT"

URL=$(echo "$OUTPUT" | grep -o "https://api.example.com/${RUN_ID}")
echo "apiUrl: ${URL}" > output.log

