from flask import Flask, render_template, jsonify, request
from relay_control import WateringSystem
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

gpio_pin = int(os.getenv("GPIO_PIN", "17"))
watering_duration = int(os.getenv("WATERING_DURATION", "3"))

watering_system = WateringSystem(gpio_pin)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/water", methods=["POST"])
def water():
    data = request.get_json() or {}
    duration = data.get("duration", watering_duration)

    if not isinstance(duration, (int, float)) or duration < 1 or duration > 10:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "水やり時間は1〜10秒の間で指定してください",
                }
            ),
            400,
        )

    success, message = watering_system.water_plants(duration)

    return jsonify(
        {"success": success, "message": message, "status": watering_system.get_status()}
    ), (200 if success else 409)


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(watering_system.get_status())


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "mock_mode": watering_system.mock_mode})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    debug = os.getenv("FLASK_ENV") == "development"

    logger.info(f"水やりシステム起動中... ポート: {port}")
    logger.info(f"GPIO Pin: {gpio_pin}, デフォルト水やり時間: {watering_duration}秒")

    app.run(host="0.0.0.0", port=port, debug=debug)
