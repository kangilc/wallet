아래는 **Java 기반 REST API 서버**로 FDUSD 자동매매 기능을 제공하는 예시입니다. Spring Boot를 사용해 구현합니다.

---

## ✅ 1. **프로젝트 구조**
```
fdusd-bot-rest/
├── src/main/java/com/example/fdusdbot/
│   ├── FdusdBotApplication.java
│   ├── controller/
│   │   └── TradingController.java
│   ├── service/
│   │   └── BinanceService.java
│   └── util/
│       └── SignatureUtil.java
└── pom.xml
```

---

## ✅ 2. **pom.xml (필요 의존성)**
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
    <dependency>
        <groupId>org.apache.httpcomponents.client5</groupId>
        <artifactId>httpclient5</artifactId>
    </dependency>
</dependencies>
```

---

## ✅ 3. **SignatureUtil.java**
```java
package com.example.fdusdbot.util;

import javax.crypto.Mac;
import SignatureUtil {
    public static String sign(String data, String secretKey) throws Exception {
        Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
        SecretKeySpec secretKeySpec = new SecretKeySpec(secretKey.getBytes(), "HmacSHA256");
        sha256_HMAC.init(secretKeySpec);
        byte[] hash = sha256_HMAC.doFinal(data.getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) sb.append(String.format("%02x", b));
        return sb.toString();
    }
}
```

---

## ✅ 4. **BinanceService.java**
```java
package com.example.fdusdbot.service;

import com.example.fdusdbot.util.SignatureUtil;
import org.springframework.stereotype.Service;
import java.net.*;
import java.io.*;
import java.util.*;

@Service
public class BinanceService {
    private final String API_KEY = System.getenv("API_KEY");
    private final String SECRET_KEY = System.getenv("SECRET_KEY");
    private final String BASE_URL = "https://api.binance.com";

    public String getPrice(String symbol) throws IOException {
        URL url = new URL(BASE_URL + "/api/v3/ticker/price?symbol=" + symbol);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) response.append(line);
        in.close();
        return response.toString();
    }

    public String placeOrder(String symbol, String side, String quantity, String price) throws Exception {
        long timestamp = System.currentTimeMillis();
        String query = String.format("symbol=%s&side=%s&type=LIMIT&timeInForce=GTC&quantity=%s&price=%s&timestamp=%d",
                symbol, side, quantity, price, timestamp);
        String signature = SignatureUtil.sign(query, SECRET_KEY);
        String fullQuery = query + "&signature=" + signature;

        URL url = new URL(BASE_URL + "/api/v3/order");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("X-MBX-APIKEY", API_KEY);
        conn.setDoOutput(true);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(fullQuery.getBytes());
            os.flush();
        }

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) response.append(line);
        in.close();
        return response.toString();
    }
}
```

---

## ✅ 5. **TradingController.java**
```java
package com.example.fdusdbot.controller;

import com.example.fdusdbot.service.BinanceService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/trade")
public class TradingController {
    private final BinanceService binanceService;

    public TradingController(BinanceService binanceService) {
        this.binanceService = binanceService;
    }

    @GetMapping("/price")
    public String getPrice(@RequestParam(defaultValue = "FDUSDUSDT") String symbol) throws Exception {
        return binanceService.getPrice(symbol);
    }

    @PostMapping("/order")
    public String placeOrder(@RequestParam String symbol,
                              @RequestParam String side,
                              @RequestParam String quantity,
                              @RequestParam String price) throws Exception {
        return binanceService.placeOrder(symbol, side, quantity, price);
    }
}
```

---

## ✅ 6. **실행 및 테스트**
- **환경 변수 설정**:
  ```bash
  export API_KEY=your_api_key
  export SECRET_KEY=your_secret_key
  ```
- **실행**:
  ```bash
  mvn spring-boot:run
  ```
- **API 호출 예시**:
  - 시세 조회:  
    `GET http://localhost:8080/api/trade/price?symbol=FDUSDUSDT`
  - 주문 생성:  
    `POST http://localhost:8080/api/trade/order?symbol=FDUSDUSDT&side=BUY&quantity=10&price=0.999`

---

### ✅ 추가 가능 기능
- **자동매매 로직을 REST API로 제어** (시작/중지)
- **손절/익절 조건 API**
- **Swagger UI 연동**
- **Dockerfile + Kubernetes 배포**

---

👉 다음 중 어떤 걸 추가할까요?  
✅ **자동매매 로직을 REST API로 제어하는 엔드포인트**  
✅ **Swagger 문서화**  
✅ **Java용 Dockerfile + Kubernetes YAML**  

아래는 요청하신 세 가지 기능을 모두 반영한 **Java Spring Boot REST API 서버 확장 버전**입니다:

---

## ✅ 1. **자동매매 로직을 REST API로 제어하는 엔드포인트**

### **추가 기능**
- `/api/bot/start` → 자동매매 시작
- `/api/bot/stop` → 자동매매 중지
- `/api/bot/status` → 현재 상태 확인

### **BotController.java**
```java
package com.example.fdusdbot.controller;

import com.example.fdusdbot.service.BotService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/bot")
public class BotController {
    private final BotService botService;

    public BotController(BotService botService) {
        this.botService = botService;
    }

    @PostMapping("/start")
    public String startBot(@RequestParam double buyPrice, @RequestParam double sellPrice) {
        botService.startBot(buyPrice, sellPrice);
        return "자동매매 봇이 시작되었습니다.";
    }

    @PostMapping("/stop")
    public String stopBot() {
        botService.stopBot();
        return "자동매매 봇이 중지되었습니다.";
    }

    @GetMapping("/status")
    public String getStatus() {
        return botService.getStatus();
    }
}
```

### **BotService.java**
```java
package com.example.fdusdbot.service;

import org.springframework.stereotype.Service;

@Service
public class BotService {
    private volatile boolean running = false;
    private Thread botThread;

    public void startBot(double buyPrice, double sellPrice) {
        if (running) return;
        running = true;
        botThread = new Thread(() -> {
            while (running) {
                try {
                    double price = Double.parseDouble(new BinanceService().getPrice("FDUSDUSDT").replaceAll("[^0-9.]", ""));
                    System.out.println("현재 시세: " + price);
                    if (price <= buyPrice) {
                        System.out.println("매수 조건 충족 → 주문 실행");
                        new BinanceService().placeOrder("FDUSDUSDT", "BUY", "10", String.valueOf(buyPrice));
                    } else if (price >= sellPrice) {
                        System.out.println("매도 조건 충족 → 주문 실행");
                        new BinanceService().placeOrder("FDUSDUSDT", "SELL", "10", String.valueOf(sellPrice));
                    }
                    Thread.sleep(3000);
                } catch (Exception e) {
                    System.err.println("[ERROR] " + e.getMessage());
                }
            }
        });
        botThread.start();
    }

    public void stopBot() {
        running = false;
    }

    public String getStatus() {
        return running ? "봇 실행 중" : "봇 중지됨";
    }
}
```

---

## ✅ 2. **Swagger 문서화 추가**

### **pom.xml**
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

### **Swagger UI 접속**
- 서버 실행 후:  
  `http://localhost:8080/swagger-ui.html`

---

## ✅ 3. **Java용 Dockerfile**
```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/fdusd-bot.jar fdusd-bot.jar
ENV API_KEY=your_api_key
ENV SECRET_KEY=your_secret_key
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "fdusd-bot.jar"]
```

---

## ✅ 4. **Kubernetes 배포 YAML**
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
        ports:
        - containerPort: 8080
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
---
apiVersion: v1
kind: Secret
metadata:
  name: fdusd-secrets
type: Opaque
data:
  api-key: <base64_encoded_api_key>
  secret-key: <base64_encoded_secret_key>
---
apiVersion: v1
kind: Service
metadata:
  name: fdusd-bot-service
spec:
  selector:
    app: fdusd-bot
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

---

### ✅ **이제 가능한 추가 작업**
- **Helm Chart로 배포 자동화**
- **Prometheus + Grafana로 모니터링**
- **자동매매 전략(손절/익절, 트레일링 스탑) 추가**

