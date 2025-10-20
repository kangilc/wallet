# wallet

바이낸스에서 **FDUSD API를 외부에서 사용**하려면 다음 단계를 따르면 됩니다:

---

### ✅ **1. 바이낸스 개발자 API 문서 접속**
- 공식 문서: [Binance API Docs](https://www.binance.com/en/binance-api)  
  여기서 REST API, WebSocket API, SDK 예제(Python, Java 등)를 확인할 수 있습니다.citeturn7search9

---

### ✅ **2. 바이낸스 계정 생성 및 보안 설정**
- **계정 생성**: [바이낸스 공식 사이트](https://www.binance.com)에서 가입 후 **KYC 인증** 완료
- **2단계 인증(2FA)**: Google Authenticator 또는 SMS 인증 필수
- **피싱 방지 코드** 설정 권장[1](https://codelenz.tistory.com/entry/%EB%B0%94%EC%9D%B4%EB%82%B8%EC%8A%A4-%EA%B0%80%EC%9E%85-API-%EB%B0%9C%EA%B8%89-%EB%B0%A9%EB%B2%95-%EA%B8%B0%EC%B4%88-%EA%B0%80%EC%9D%B4%EB%93%9C)

---

### ✅ **3. API 키 발급**
1. 로그인 후 **[프로필 → API Management]** 이동
2. **Create API** 클릭 → 이름 지정 (예: `fdusd-bot`)
3. **보안 인증**(이메일 코드 + 2FA) 완료
4. **API Key & Secret Key** 발급 → Secret Key는 최초 1회만 표시되므로 안전하게 저장
5. **권한 설정**:
   - ✅ *Enable Spot & Margin Trading* (FDUSD 거래용)
   - ✅ *Read* (데이터 조회)
   - ⛔ *Enable Withdrawals* (절대 활성화 금지)
6. **IP 화이트리스트** 등록 (고정 IP 또는 VPS IP 권장)[2](https://binance.sozon.co.kr/entry/API-%ED%82%A4-%EB%B0%9C%EA%B8%89-%EA%B0%80%EC%9D%B4%EB%93%9C-%EB%B0%94%EC%9D%B4%EB%82%B8%EC%8A%A4-%EC%B4%88%EB%B3%B4%EC%9A%A9)

---

### ✅ **4. FDUSD 거래 API 사용**
- FDUSD는 **Spot 마켓**에서 USDT, BUSD와 유사하게 사용 가능
- 예시 엔드포인트:
  - **시세 조회**:  
    ```
    GET /api/v3/ticker/price?symbol=FDUSDUSDT
    ```
  - **주문 생성**:  
    ```
    POST /api/v3/order
    ```
    (파라미터: `symbol=FDUSDUSDT`, `side=BUY`, `type=LIMIT`, `quantity`, `price`)
- 인증: `X-MBX-APIKEY` 헤더 + HMAC SHA256 서명 필요[3](https://m.blog.naver.com/stockjeonsa/223019261844)

---

### ✅ **5. 테스트넷에서 먼저 검증**
- Binance Testnet에서 API 키 발급 후 시뮬레이션 가능
- 실거래 전 반드시 테스트넷에서 코드 검증 권장[4](https://bitkan.com/ko/learn/%EB%B0%94%EC%9D%B4%EB%82%B8%EC%8A%A4-api%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EC%9A%94-%EB%B0%94%EC%9D%B4%EB%82%B8%EC%8A%A4-api-%EC%82%AC%EC%9A%A9-%EB%B0%A9%EB%B2%95-61454)

## ✅ 1. **FDUSD 거래용 Python 샘플 코드**

```python
import time
import hmac
import hashlib
import requests

API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
BASE_URL = "https://api.binance.com"

def sign(params):
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return query_string + "&signature=" + signature

# 예: FDUSD/USDT 시세 조회
def get_price(symbol="FDUSDUSDT"):
    url = f"{BASE_URL}/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol})
    return response.json()

# 예: FDUSD 매수 주문
def place_order(symbol="FDUSDUSDT", side="BUY", quantity="10", price="0.999"):
    endpoint = "/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": price,
        "timestamp": timestamp
    }
    signed_params = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    response = requests.post(BASE_URL + endpoint, headers=headers, data=signed_params)
    return response.json()

# 실행 예시
print("FDUSD 시세:", get_price())
# print(place_order())  # 실제 주문 시 주석 해제
```

**주의**:  
- `API_KEY`와 `SECRET_KEY`는 안전하게 보관하세요.
- 테스트는 반드시 Binance Testnet에서 먼저 진행하세요.

---

## ✅ 2. **API 권한·보안 체크리스트**

| 항목 | 설명 | 권장 설정 |
|------|------|-----------|
| **API Key 생성** | [프로필 → API Management]에서 생성 | ✅ |
| **권한 설정** | Spot & Margin Trading 활성화 | ✅ |
| **출금 권한** | 절대 활성화 금지 | ❌ |
| **IP 화이트리스트** | 고정 IP 또는 VPS IP 등록 | ✅ |
| **2FA 인증** | Google Authenticator 필수 | ✅ |
| **Secret Key 관리** | 안전한 비밀 저장소(Vault) 사용 | ✅ |
| **테스트넷 사용** | 실거래 전 반드시 테스트 | ✅ |

---

## ✅ 3. **바이낸스 API 사용 팁**
- **속도 제한**: REST API는 초당 요청 제한이 있으므로 공식 레이트 리밋 확인
- **서명 필수**: 주문, 계정 관련 API는 HMAC SHA256 서명 필요
- **WebSocket 활용**: 실시간 시세는 REST보다 WebSocket이 효율적
- **에러 처리**: `-1021` (타임스탬프 오류) → 서버 시간 동기화 필요
- **리스크 관리**: 주문 전 `GET /api/v3/exchangeInfo`로 최소 주문 수량 확인
- **API Key 보안**: GitHub 등 공개 저장소에 절대 업로드 금지

---

## ✅ 1. **FDUSD 자동매매 봇 기본 구조 (Python)**  
아래 코드는 **시세 모니터링 + 조건부 매수/매도** 로직을 포함하며, **예외 처리**를 강화했습니다.

```python
import time
import hmac
import hashlib
import requests

API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
BASE_URL = "https://api.binance.com"
SYMBOL = "FDUSDUSDT"

def sign(params):
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return query_string + "&signature=" + signature

def get_price():
    try:
        response = requests.get(f"{BASE_URL}/api/v3/ticker/price", params={"symbol": SYMBOL}, timeout=5)
        response.raise_for_status()
        return float(response.json()["price"])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 시세 조회 실패: {e}")
        return None

def place_order(side, quantity, price):
    try:
        endpoint = "/api/v3/order"
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": SYMBOL,
            "side": side,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp
        }
        signed_params = sign(params)
        headers = {"X-MBX-APIKEY": API_KEY}
        response = requests.post(BASE_URL + endpoint, headers=headers, data=signed_params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 주문 실패: {e}")
        return None

# 자동매매 로직
TARGET_BUY = 0.995
TARGET_SELL = 1.005
QUANTITY = "10"

while True:
    price = get_price()
    if price:
        print(f"현재 FDUSD 시세: {price}")
        if price <= TARGET_BUY:
            print("매수 조건 충족 → 주문 실행")
            print(place_order("BUY", QUANTITY, str(TARGET_BUY)))
        elif price >= TARGET_SELL:
            print("매도 조건 충족 → 주문 실행")
            print(place_order("SELL", QUANTITY, str(TARGET_SELL)))
    time.sleep(3)
```

**예외 처리 포인트**:
- `requests.exceptions.RequestException`으로 네트워크 오류 처리
- `response.raise_for_status()`로 HTTP 오류 감지
- `timeout` 설정으로 무한 대기 방지

---

## ✅ 2. **API 권한·보안 체크리스트 (Confluence용 표)**

| 항목 | 설명 | 권장 설정 |
|------|------|-----------|
| **API Key 생성** | [프로필 → API Management]에서 생성 | ✅ |
| **권한 설정** | Spot & Margin Trading 활성화 | ✅ |
| **출금 권한** | 절대 활성화 금지 | ❌ |
| **IP 화이트리스트** | 고정 IP 또는 VPS IP 등록 | ✅ |
| **2FA 인증** | Google Authenticator 필수 | ✅ |
| **Secret Key 관리** | 안전한 비밀 저장소(Vault) 사용 | ✅ |
| **테스트넷 사용** | 실거래 전 반드시 테스트 | ✅ |

---

## ✅ 3. **바이낸스 API 가이드 문서 (Confluence 포맷)**

```
h1. 바이낸스 API 가이드

h2. 1. 개요
* 본 문서는 FDUSD 거래를 포함한 바이낸스 API 사용 방법을 정리합니다.

h2. 2. API 키 발급 절차
# 바이낸스 로그인 → [프로필 → API Management]
# API 생성 후 이름 지정 (예: fdusd-bot)
# 보안 인증(이메일 + 2FA) 완료
# API Key & Secret Key 발급 (Secret Key는 최초 1회만 표시)

h2. 3. 권한 설정
* Spot & Margin Trading: 활성화
* 출금 권한: 비활성화
* IP 화이트리스트: 고정 IP 등록

h2. 4. FDUSD 거래 API 예시
* 시세 조회:
```
GET /api/v3/ticker/price?symbol=FDUSDUSDT
```
* 주문 생성:
```
POST /api/v3/order
```

h2. 5. 보안 체크리스트
|| 항목 || 설명 || 권장 설정 ||
| API Key 생성 | [프로필 → API Management] | ✅ |
| 출금 권한 | 절대 활성화 금지 | ❌ |
| IP 화이트리스트 | 고정 IP 등록 | ✅ |

h2. 6. 참고 자료
* [Binance API Docs|https://www.binance.com/en/binance-api]
* [Binance Testnet|https://testnet.binance.vision]
```

---

👉 다음 중 어떤 걸 추가로 해줄까요?  
✅ **자동매매 봇에 손절/익절 로직 추가**  
✅ **Confluence 문서에 “자동매매 봇 가이드” 섹션 포함**  
✅ **Docker로 배포 가능한 구조**  

아래는 **FDUSD 자동매매 봇을 Docker로 배포하는 기본 구조**입니다.

---

## ✅ 1. **프로젝트 구조**
```
fdusd-bot/
├── app/
│   ├── bot.py          # 자동매매 로직 (앞서 만든 Python 코드)
│   ├── requirements.txt # Python 의존성
├── Dockerfile
└── docker-compose.yml   # (옵션) 환경 변수 관리 및 실행
```

---

## ✅ 2. **requirements.txt**
```text
requests==2.31.0
```

---

## ✅ 3. **Dockerfile**
```dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY app/ .

# 환경 변수 (API Key는 Docker Secrets 또는 .env로 관리)
ENV API_KEY=your_api_key
ENV SECRET_KEY=your_secret_key

# 실행 명령
CMD ["python", "bot.py"]
```

---

## ✅ 4. **docker-compose.yml** (선택)
```yaml
version: '3.8'
services:
  fdusd-bot:
    build: .
    container_name: fdusd-bot
    restart: always
    environment:
      - API_KEY=${API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./app:/app
```

---

## ✅ 5. **실행 방법**
```bash
# 빌드
docker build -t fdusd-bot .

# 실행
docker run -d --name fdusd-bot \
  -e API_KEY="your_api_key" \
  -e SECRET_KEY="your_secret_key" \
  fdusd-bot
```

---

## ✅ **보안 팁**
- **API Key는 .env 파일 + docker-compose로 관리**  
- **Docker Secrets** 사용 가능 (특히 서버 환경)
- **로그에 API Key 출력 금지**

---

👉 다음 중 어떤 걸 추가로 해줄까요?  
✅ **Docker + .env 파일 예시**  
✅ **자동 재시작 + 로그 관리 전략**  
✅ **Kubernetes 배포 YAML 템플릿**  

아래에 요청하신 세 가지를 모두 정리했습니다:

---

## ✅ 1. **Docker + .env 파일 예시**

### **프로젝트 구조**
```
fdusd-bot/
├── app/
│   ├── bot.py
│   ├── requirements.txt
├── .env
├── Dockerfile
└── docker-compose.yml
```

### **.env 파일**
```
API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

### **docker-compose.yml**
```yaml
version: '3.8'
services:
  fdusd-bot:
    build: .
    container_name: fdusd-bot
    restart: always
    env_file:
      - .env
    volumes:
      - ./app:/app
```

---

## ✅ 2. **자동 재시작 및 로그 관리 전략**
- **자동 재시작**: `restart: always` (docker-compose에서 설정)
- **로그 관리**:
  - Docker 기본 로그는 `docker logs fdusd-bot`으로 확인
  - 장기 운영 시:
    - `logging` 옵션으로 **json-file** 또는 **syslog** 설정
    - 예시:
      ```yaml
      logging:
        driver: "json-file"
        options:
          max-size: "10m"
          max-file: "3"
      ```
    - 또는 ELK(Stack) / Loki + Grafana 연동

---

## ✅ 3. **Kubernetes 배포 YAML 템플릿**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fdusd-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fdusd-bot
  template:
    metadata:
      labels:
        app: fdusd-bot
    spec:
      containers:
      - name: fdusd-bot
        image: your-dockerhub-username/fdusd-bot:latest
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: fdusd-secrets
              key: api-key
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: fdusd-secrets
              key: secret-key
        resources:
          limits:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Secret
metadata:
  name: fdusd-secrets
type: Opaque
data:
  api-key: <base64_encoded_api_key>
  secret-key: <base64_encoded_secret_key>
```

**배포 순서**:
1. `kubectl apply -f fdusd-bot.yaml`
2. Secret 값은 `echo -n "your_api_key" | base64`로 인코딩 후 YAML에 삽입

---

### ✅ **보안 & 운영 팁**
- **API Key는 절대 이미지에 하드코딩 금지**
- **Kubernetes Secret** 또는 **Vault** 사용
- **Helm Chart**로 배포 자동화 가능
- **Horizontal Pod Autoscaler(HPA)**로 확장성 확보 가능

---

👉 다음 중 어떤 걸 추가로 해줄까요?  
✅ **Helm Chart 템플릿**  
✅ **자동매매 봇에 손절/익절 로직 추가**  
✅ **Prometheus + Grafana 모니터링 설정**  

