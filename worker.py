import pika
import json
import time
import os
from pymongo import MongoClient
from flask_mail import Mail, Message
from twilio.rest import Client
from flask import Flask
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Configuration
class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

flask_app = Flask(__name__)
flask_app.config.from_object(Config)
mail = Mail(flask_app)
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

# MongoDB
mongo_client = MongoClient('localhost', 27017)
db = mongo_client.notification_db
notifications = db.notifications

def process_notification(notification, max_retries=3):
    attempt = 0
    success = False
    last_error = None

    
    if "_id" in notification:
        try:
            notification["_id"] = ObjectId(notification["_id"])
        except:
            pass

    while attempt < max_retries and not success:
        try:
            # Email
            if "email" in notification.get("type", []) and notification.get("to_email"):
                with flask_app.app_context():
                    msg = Message(
                        subject="New Notification",
                        recipients=[notification["to_email"]],
                        body=notification["message"]
                    )
                    mail.send(msg)
                    print(f"Email sent to {notification['to_email']}")

            # SMS
            if "sms" in notification.get("type", []) and notification.get("to_phone"):
                twilio_client.messages.create(
                    body=notification["message"],
                    from_=Config.TWILIO_PHONE_NUMBER,
                    to=notification["to_phone"]
                )
                print(f"SMS sent to {notification['to_phone']}")

            # Update status
            notifications.update_one(
                {"_id": notification["_id"]},
                {"$set": {"status": "sent"}}
            )
            success = True

        except Exception as e:
            attempt += 1
            last_error = str(e)
            print(f"Attempt {attempt} failed: {last_error}")
            time.sleep(2 ** attempt)  # Exponential backoff

    if not success:
        notifications.update_one(
            {"_id": notification["_id"]},
            {"$set": {"status": "failed", "error": last_error}}
        )
        print(f"Permanent failure after {max_retries} attempts")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='notifications', durable=True)

    def callback(ch, method, properties, body):
        notification = json.loads(body)
        process_notification(notification)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='notifications', on_message_callback=callback)
    print(" [*] Worker started. Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    main()
