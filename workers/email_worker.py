#!/usr/bin/env python3
"""
MHRS SaaS — Email Worker (Standalone RabbitMQ Consumer)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This script runs as an independent process (separate from the FastAPI app).
It continuously listens to the RabbitMQ 'email_verification' queue and
dispatches emails via SMTP for each message consumed.

Run:
    python workers/email_worker.py

Production run (with systemd service):
    See README.md — systemd section for Ubuntu VM setup.

Environment:
    Reads from .env file in the project root.
"""

import json
import sys
import os
import time
import logging

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.config import get_settings
from app.services.email_service import send_verification_email, send_appointment_reminder

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("email_worker")

settings = get_settings()

QUEUE_NAME = "email_verification"
EXCHANGE_NAME = "mhrs.emails"
RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_ATTEMPTS = 10


# ── Message Handler ───────────────────────────────────────────────────────────
def handle_message(ch, method, properties, body: bytes) -> None:
    """
    Processes a single RabbitMQ message.

    Supported message types:
        - "email_verification": sends 6-digit code email
        - "appointment_reminder": sends appointment reminder email

    On success: ACKs the message (removes from queue).
    On failure: NACKs with requeue=False (moves to DLQ if configured).
    """
    try:
        data = json.loads(body.decode("utf-8"))
        msg_type = data.get("type")
        logger.info(f"📩 Processing message type='{msg_type}' for email={data.get('email')}")

        if msg_type == "email_verification":
            send_verification_email(
                email=data["email"],
                name=data["name"],
                code=data["code"],
            )
            logger.info(f"✅ Verification email sent to {data['email']}")

        elif msg_type == "appointment_reminder":
            send_appointment_reminder(
                email=data["email"],
                name=data["name"],
                doctor_name=data.get("doctor_name", ""),
                appointment_dt=data.get("appointment_dt", ""),
            )
            logger.info(f"✅ Reminder email sent to {data['email']}")

        else:
            logger.warning(f"⚠️  Unknown message type: '{msg_type}'. Discarding.")

        # ACK — message processed successfully
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in message: {e}. Discarding.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except KeyError as e:
        logger.error(f"❌ Missing required field in message: {e}. Discarding.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        logger.error(f"❌ Failed to process message: {e}. Requeueing for retry.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# ── Worker Main Loop ──────────────────────────────────────────────────────────
def start_worker() -> None:
    """
    Connects to RabbitMQ and starts consuming messages.
    Automatically reconnects on connection failure with exponential backoff.
    """
    attempt = 0
    while attempt < MAX_RECONNECT_ATTEMPTS:
        try:
            logger.info(
                f"🔌 Connecting to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port} "
                f"(attempt {attempt + 1}/{MAX_RECONNECT_ATTEMPTS})"
            )
            params = pika.URLParameters(settings.rabbitmq_url)
            params.heartbeat = 60
            params.blocked_connection_timeout = 300

            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            attempt = 0  # Reset counter after successful connect

            # Declare durable exchange and queue (idempotent)
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="direct",
                durable=True,
            )
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(
                exchange=EXCHANGE_NAME,
                queue=QUEUE_NAME,
                routing_key=QUEUE_NAME,
            )

            # Process one message at a time — don't overwhelm SMTP
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

            logger.info(f"🚀 Email worker started. Listening on queue: '{QUEUE_NAME}'")
            logger.info("   Press Ctrl+C to stop.\n")
            channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("🛑 Email worker stopped by user.")
            break

        except (AMQPConnectionError, AMQPChannelError) as e:
            attempt += 1
            wait = min(RECONNECT_DELAY_SECONDS * attempt, 60)
            logger.error(f"Connection error: {e}. Retrying in {wait}s...")
            time.sleep(wait)

        except Exception as e:
            attempt += 1
            wait = RECONNECT_DELAY_SECONDS * attempt
            logger.exception(f"Unexpected error: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    logger.critical("💀 Max reconnect attempts reached. Email worker exiting.")
    sys.exit(1)


if __name__ == "__main__":
    start_worker()
