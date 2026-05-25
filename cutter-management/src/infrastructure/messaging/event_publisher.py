"""
RabbitMQ Event Publisher

发布领域事件到RabbitMQ，供其他服务（如ai-service）消费。
使用topic exchange模式，routing key格式：cutter.created / cutter.updated / cutter.deleted
"""

import json
import os
from typing import Any

import pika
from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingConnection

from src.domain.events.cutter_events import DomainEvent


class RabbitMQEventPublisher:
    """RabbitMQ事件发布者"""

    EXCHANGE = "cnc.events"
    EXCHANGE_TYPE = "topic"

    def __init__(self) -> None:
        self._connection = None
        self._channel = None
        self._rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@111.228.18.127:5672/")

    def _connect(self) -> None:
        """建立连接"""
        if self._connection and self._connection.is_open:
            return

        params = pika.URLParameters(self._rabbitmq_url)
        self._connection = BlockingConnection(params)
        self._channel = self._connection.channel()

        # 声明交换机
        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
        )

    def publish(self, event: DomainEvent) -> None:
        """发布领域事件"""
        try:
            self._connect()

            # 确定routing key
            routing_key = event.event_type  # e.g., "cutter.created"

            # 序列化事件
            message = json.dumps(event.to_dict(), ensure_ascii=False, default=str)

            # 发布消息
            self._channel.basic_publish(
                exchange=self.EXCHANGE,
                routing_key=routing_key,
                body=message.encode("utf-8"),
                properties=BasicProperties(
                    delivery_mode=2,  # 持久化消息
                    content_type="application/json",
                    message_id=str(event.event_id),
                ),
            )
            print(f"[EventPublisher] Published {routing_key}: {event.event_id}")
        except Exception as e:
            print(f"[EventPublisher] Failed to publish event: {e}")
            # 不抛出异常，避免影响主业务流程
            self._connection = None

    def close(self) -> None:
        """关闭连接"""
        if self._connection and self._connection.is_open:
            self._connection.close()


class AsyncRabbitMQEventPublisher:
    """异步RabbitMQ事件发布者（使用pika的异步适配器）"""

    EXCHANGE = "cnc.events"
    EXCHANGE_TYPE = "topic"

    def __init__(self) -> None:
        self._rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@111.228.18.127:5672/")
        self._publisher = RabbitMQEventPublisher()

    async def publish(self, event: DomainEvent) -> None:
        """异步发布事件（在线程中执行）"""
        import asyncio
        await asyncio.to_thread(self._publisher.publish, event)

    async def close(self) -> None:
        """关闭连接"""
        import asyncio
        await asyncio.to_thread(self._publisher.close)


def create_event_publisher() -> AsyncRabbitMQEventPublisher:
    """创建事件发布者实例"""
    return AsyncRabbitMQEventPublisher()
