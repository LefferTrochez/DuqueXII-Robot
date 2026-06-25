from flask import Flask, render_template, jsonify, send_from_directory
import time

app = Flask(__name__)

# Global variables for local demo mode.
warning_message = "everything is all right."
warning_active = False
last_stop_click_time = 0

# Simulated sensor values.
sensor_values = {
    'noise_level': 9,
    'ambient_temp': 17,
    'body_temp': 36,
    'gas_level': 1
}


def simulate_publish(variable_name, value):
    print(f"[DEBUG] Published {variable_name}: {value}")


def publish_mode_operation(mode):
    mode_value = "1" if mode else "0"
    simulate_publish("mode_operation", mode_value)


def publish_buzzer_off():
    simulate_publish("buzzer", "3")


def publish_motion_pan(value):
    simulate_publish("motion_pan", value)


def publish_motion_til(value):
    simulate_publish("motion_til", value)


@app.route("/")
def index():
    return render_template(
        "index.html",
        warning_message=warning_message,
        warning_active=warning_active,
        sensor_values=sensor_values
    )


@app.route("/video_feed")
def video_feed():
    # Static image used instead of a real video stream.
    return send_from_directory(app.static_folder, "child_playing.png", mimetype="image/png")


@app.route("/set_mode_on")
@app.route("/set_mode_active")
def set_mode_on():
    publish_mode_operation(True)
    print("[DEBUG] Active button pressed")
    return "Operation mode = On"


@app.route("/set_mode_off")
@app.route("/set_mode_sleep")
def set_mode_off():
    publish_mode_operation(False)
    publish_motion_pan("00")
    publish_motion_til("0000")
    print("[DEBUG] Sleep button pressed")
    return "Operation mode = Off"


@app.route("/buzzer_off")
@app.route("/set_buzzer_off")
def buzzer_off():
    publish_buzzer_off()
    publish_motion_pan("00")
    publish_motion_til("0000")
    print("[DEBUG] Silent button pressed")
    return "Buzzer = Off"


@app.route("/move_up")
def move_up():
    publish_motion_til("0101")
    print("[DEBUG] Up arrow pressed")
    return "Movement: Up"


@app.route("/move_down")
def move_down():
    publish_motion_til("0111")
    print("[DEBUG] Down arrow pressed")
    return "Movement: Down"


@app.route("/move_left")
def move_left():
    publish_motion_pan("10")
    print("[DEBUG] Left arrow pressed")
    return "Movement: Left"


@app.route("/move_right")
def move_right():
    publish_motion_pan("01")
    print("[DEBUG] Right arrow pressed")
    return "Movement: Right"


@app.route("/move_stop")
def move_stop():
    global last_stop_click_time
    current_time = time.time()

    if current_time - last_stop_click_time < 1.0:
        publish_motion_pan("00")
        publish_motion_til("1111")
        print("[DEBUG] Double click on Stop")
    else:
        publish_motion_pan("00")
        publish_motion_til("0000")
        print("[DEBUG] Single click on Stop")

    last_stop_click_time = current_time
    return "Movement: Stop"


@app.route("/get_sensor_data", methods=["GET"])
def get_sensor_data():
    try:
        data = {
            "warning_message": warning_message,
            "warning_active": warning_active,
            "sensor_values": sensor_values
        }
        app.logger.info(f"Data sent to frontend: {data}")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error sending data to frontend: {e}")
        return jsonify({"error": "Sensor data could not be retrieved"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
