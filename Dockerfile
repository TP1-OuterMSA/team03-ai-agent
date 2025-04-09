FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트 파일 복사 및 권한 설정
COPY generate_secrets.py .
RUN chmod +x generate_secrets.py

# 프로젝트 파일 복사
COPY . .

# 시작 스크립트 생성
RUN echo '#!/bin/bash\n\
python generate_secrets.py\n\
python manage.py collectstatic --noinput\n\
gunicorn --bind 0.0.0.0:8000 config.wsgi:application\n\
' > start.sh && \
chmod +x start.sh

# 서비스 실행
EXPOSE 8000
CMD ["./start.sh"]
