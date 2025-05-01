import os
import json
import sys

# 환경 변수에서 시크릿 값 가져오기
secret_key = os.environ.get('DJANGO_SECRET', '')
openai_api = os.environ.get('OPENAI_API', '')

if not secret_key or not openai_api:
    print("Error: Required environment variables DJANGO_SECRET or OPENAI_API not set.")
    sys.exit(1)

# secrets.json 파일 생성
secrets = {
    "SECRET": secret_key,
    "OPENAIAPI": openai_api
}

# 파일에 저장
with open('secrets.json', 'w') as f:
    json.dump(secrets, f)

print("Secrets file generated successfully!")
