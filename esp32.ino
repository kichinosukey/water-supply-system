#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <Ticker.h>

// Wi-Fi設定
const char* ssid = "WIFI_SSID"; // ここに実際のSSIDを入力
const char* password = "WIFI_PASSWORD"; // ここに実際のパスワードを入力

// GPIO設定
const int RELAY_PIN = 5;

// Webサーバ
WebServer server(80);
Ticker relayTimer;

void stopPump() {
  digitalWrite(RELAY_PIN, LOW);
  Serial.println("Pump OFF");
}

void handleWatering() {
  if (server.hasArg("plain") == false) {
    server.send(400, "application/json", "{\"error\":\"No body\"}");
    return;
  }

  String body = server.arg("plain");
  DynamicJsonDocument doc(256);
  DeserializationError error = deserializeJson(doc, body);
  if (error) {
    server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }

  int duration = doc["duration"] | 3;
  digitalWrite(RELAY_PIN, HIGH);
  relayTimer.once(duration, stopPump);
  Serial.printf("Pump ON for %d seconds\n", duration);

  server.send(200, "application/json", "{\"status\":\"accepted\"}");
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // デバッグ用 ping 確認エンドポイント
  server.on("/ping", HTTP_GET, []() {
    Serial.println("Received /ping");
    server.send(200, "text/plain", "pong");
  });

  // 水やりAPI
  server.on("/water", HTTP_POST, handleWatering);

  server.begin();
  Serial.println("ESP32 REST API server ready!");
}

void loop() {
  server.handleClient();
}