# Real-Time Notification Service with Retry Mechanism

A robust notification system supporting **email**, **SMS**, and **real-time in-app notifications**, built with Flask, MongoDB, RabbitMQ, and Twilio. Designed for reliability with queue integration and automatic retries.

---

## Features
- **Multi-Channel Notifications**: Send via email, SMS, or in-app.
- **Queue Integration**: Uses RabbitMQ to decouple request handling from processing.
- **Automatic Retries**: 3 retries with exponential backoff for failed notifications.
- **Real-Time Updates**: In-app notifications via Socket.IO.
- **Status Tracking**: MongoDB stores notification status (`queued`, `sent`, `failed`).

---

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Retry Logic](#retry-logic)
- [Improvements](#possible-improvements)

---

## Installation

### Prerequisites
- Python 3.8+
- MongoDB
- RabbitMQ
- Twilio Account (for SMS)
- Gmail App Password (for email)

### Steps
1. **Clone the repository**:

2. **Install dependencies**:

3. **Set up RabbitMQ**:
- [Install Erlang](https://erlang.org/download/otp_win64_26.2.exe) (Windows)
- [Install RabbitMQ](https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.13.0/rabbitmq-server-3.13.0.exe)
- Enable management plugin:
  ```
  rabbitmq-plugins enable rabbitmq_management
  ```

---

## Configuration

1. **Environment Variables**  
Create a `.env` file:

2. **MongoDB**  
Ensure MongoDB is running on `localhost:27017`.

---

## Running the Application

1. **Start the Flask API**:

2. **Start the Worker** (in a separate terminal):

---

## API Endpoints

| Endpoint                      | Method | Description                               |
|-------------------------------|--------|-------------------------------------------|
| `/notifications`              | POST   | Send a notification (email/SMS/in-app)    |
| `/users/<user_id>/notifications` | GET  | Fetch all notifications for a user        |

---

## Testing

### Sample Requests

**1. Send In-App Notification**:

**2. Send Email Notification**:

**3. Send SMS Notification**:

**4. Combined Notification**:

---

## Monitoring

1. **RabbitMQ Dashboard**  
   Access at [http://localhost:15672](http://localhost:15672) (login: `guest`/`guest`).  
   Monitor the `notifications` queue for pending jobs.

2. **MongoDB**  
   Use MongoDB Compass or the shell to check the `notification_db.notifications` collection.

---

## Retry Logic

- **3 retries** with exponential backoff (2s, 4s, 8s).
- Notifications marked as `failed` after all retries.
- Errors logged in MongoDB with the final exception message.

---

## Possible Improvements

1. **Dashboard**: Build a UI to view notifications and retry failed ones.
2. **Rate Limiting**: Prevent abuse of SMS/email endpoints.
3. **User Preferences**: Let users opt-in/out of notification types.
4. **Deployment**: Dockerize the app and deploy to cloud platforms.

---

**Developed by [nandini bhardwaj]**  
*For [Pepsales AI] Technical Assignment*
