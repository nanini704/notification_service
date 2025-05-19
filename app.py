from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import datetime
import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB
client = MongoClient('localhost', 27017)
db = client.notification_db
notifications = db.notifications

# RabbitMQ
def enqueue_notification(notification):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='notifications', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(notification),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print("RabbitMQ Error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notifications', methods=["POST"])
def send_notification():
    data = request.get_json()
    
    # Validation
    required_fields = ["user_id", "type", "message"]
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Process types
    notif_types = [data["type"]] if isinstance(data["type"], str) else data["type"]
    
    # Create notification document
    notification = {
        "user_id": data["user_id"],
        "type": notif_types,
        "message": data["message"],
        "to_email": data.get("to_email"),
        "to_phone": data.get("to_phone"),
        "status": "queued",
        "is_new": True,
        "timestamp": datetime.datetime.utcnow()
    }

    # Real-time in-app
    if "in-app" in notif_types:
        socketio.emit('new_notification', notification)
        notification["status"] = "sent"

    # Save to DB
    result = notifications.insert_one(notification.copy())
    notification["_id"] = str(result.inserted_id)
    notification["timestamp"] = notification["timestamp"].isoformat()

    # Queue email/SMS
    if any(t in notif_types for t in ["email", "sms"]):
        enqueue_notification(notification)

    return jsonify(notification), 202

@app.route('/users/<user_id>/notifications', methods=["GET"])
def get_user_notifications(user_id):
    user_notifs = list(notifications.find({"user_id": user_id}))
    for n in user_notifs:
        n["_id"] = str(n["_id"])
        n["timestamp"] = n["timestamp"].isoformat() if isinstance(n["timestamp"], datetime.datetime) else n["timestamp"]
    return jsonify(user_notifs), 200

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
