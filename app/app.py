from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 必須設定：ESP32のAPIベースURL（例: http://192.168.2.163）
ESP32_API_BASE = os.getenv("WATERING_API_BASE_URL")
if not ESP32_API_BASE:
    raise RuntimeError("環境変数 WATERING_API_BASE_URL が設定されていません")

DEFAULT_DURATION = int(os.getenv("WATERING_DURATION", "10"))


@app.route("/api/water", methods=["POST"])
def water():
    data = request.get_json() or {}
    duration = data.get("duration", DEFAULT_DURATION)

    if not isinstance(duration, (int, float)) or not (1 <= duration <= 30):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "水やり時間は1〜30秒の間で指定してください",
                }
            ),
            400,
        )

    try:
        response = requests.post(
            f"{ESP32_API_BASE}/water",
            json={"duration": duration},
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        print(f"[DEBUG] posting to {ESP32_API_BASE}/water with duration={duration}")
        return jsonify(
            {"success": True, "message": result.get("status", ""), "result": result}
        )
    except requests.RequestException as e:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "ESP32への接続に失敗しました",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/api/ping", methods=["GET"])
def ping():
    try:
        r = requests.get(f"{ESP32_API_BASE}/ping", timeout=3)
        return jsonify({"pong": r.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
