import os
import json

secret_key = os.environ.get('django-secret', '')
openai_api = os.environ.get('openai-api-key', '')

db_engine = os.environ.get('db-engine', '')
db_name = os.environ.get('db-name', '')
db_user = os.environ.get('db-user', '')
db_password = os.environ.get('db-password', '')
db_host = os.environ.get('db-host', '')
db_port = os.environ.get('db-port', '')

secrets = {
    "SECRET": secret_key,
    "OPENAIAPI": openai_api,
    "ENGINE": db_engine,
    "NAME": db_name,
    "USER": db_user,
    "PASSWORD": db_password,
    "HOST": db_host,
    "PORT": db_port
}

with open('secrets.json', 'w') as f:
    json.dump(secrets, f)

print("Secrets file generated successfully!")