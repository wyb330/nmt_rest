### 소개

영어-한국어 번역 엔진을 이용한 번역 REST API 서버

**주요 기능**

1. 영어->한국어, 한국어->영어 양방향 번역 지원

2. 영어->한국어 번역 시 높임말 설정 가능

3. 텍스트, 자막 파일 번역 지원

### 설치

 setup.bat 또는 setup_gpu.bat를 실행하여 번역 모델을 다운로드받고, 

 서버 실행에 필요한 라이브러리를 설치합니다.

  setup.bat : CPU를 이용해서 번역 서비스를 하는 경우

  setup_gpu.bat : Nvidia GPU를 이용해서 번역 서비스를 하는 경우

### 실행

```commandline
run.bat
```
또는
```commandline
uv run server.py
```
**server.py 실행 옵션**

  -p : 서버의 포트 번호. 기본값은 5000

  -m : 번역 모델의 경로. 기본값은 ./models/BlueT

  -b : 배치 크기. 기본값은 8

사용 예
```commandline
uv run server.py -m ./models/BlueT -p 5000 -b 16
```

**REST API 옵션**

   sl: 번역 대상 언어
   
   tl: 번역 목표 언어

   hn: 높임말 여부('Y', 'N')

   q: 번역할 텍스트

```python
import requests
import json

API_HOST = 'http://127.0.0.1:5000/translate'
headers = {"Content-Type": "application/json"}

def translate(source, source_language_code, target_language_code, hn='Y'):
    url = API_HOST
    data = {'q': source,
            "sl": source_language_code,
            "tl": target_language_code,
            "hn": hn}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        return "[ERROR]" + str(response.status_code)
    else:
        target = json.loads(response.text)
        return target["translated_text"]

source = "This model is an English-Korean translation model."
target = translate(source, "en","ko", 'Y')
print(target)
```
 
  
