"""
MHRS SaaS — RabbitMQ Producer
Publishes email verification tasks to the 'email_verification' queue.
"""
import json
import pika
from app.config import get_settings

settings = get_settings()

QUEUE_NAME = "email_verification"
EXCHANGE_NAME = "mhrs.emails"


def _get_connection() -> pika.BlockingConnection:
    """Creates a blocking RabbitMQ connection from URL in settings."""
    params = pika.URLParameters(settings.rabbitmq_url)
    params.socket_timeout = 5
    return pika.BlockingConnection(params)


def publish_email_verification(email: str, name: str, code: str) -> None:
    """
    Publishes an email verification task to RabbitMQ.

    The message payload:
        {
            "type": "email_verification",
            "email": "user@example.com",
            "name": "User Name",
            "code": "123456"
        }

    Args:
        email: Recipient email address.
        name: Recipient display name.
        code: 6-digit verification code.

    Raises:
        pika.exceptions.AMQPConnectionError: If RabbitMQ is unreachable.
    """
    connection = _get_connection()
    channel = connection.channel()

    # Declare a durable exchange (survives broker restart)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )

    # Declare a durable queue (survives broker restart)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Bind queue to exchange
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=QUEUE_NAME,
    )

    message = json.dumps({
        "type": "email_verification",
        "email": email,
        "name": name,
        "code": code,
    })

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=QUEUE_NAME,
        body=message.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,   # Message survives restart
            content_type="application/json",
        ),
    )

    connection.close()
    print(f"📨 Email verification task published for {email}")


def publish_appointment_reminder(email: str, name: str, doctor_name: str, appointment_dt: str) -> None:
    """Publishes an appointment reminder task. Extend worker to handle 'appointment_reminder' type."""
    connection = _get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    message = json.dumps({
        "type": "appointment_reminder",
        "email": email,
        "name": name,
        "doctor_name": doctor_name,
        "appointment_dt": appointment_dt,
    })
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=message.encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )
    connection.close()
