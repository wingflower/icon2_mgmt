# ICONFRA WEB API
---
## Install
```bash
$ pip install -r requirements.txt
```

## Usage
- 
```bash
$ docker-compose -f maria-docker-compose.yml up -d && docker logs -f fastapi
# or
$ uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```
