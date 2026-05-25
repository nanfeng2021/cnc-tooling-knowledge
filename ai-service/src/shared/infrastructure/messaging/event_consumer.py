"""
RabbitMQ Event Consumer

监听cutter-management发布的领域事件，同步更新ChromaDB向量索引。
使用topic exchange模式，监听routing key：cutter.created / cutter.updated / cutter.deleted
"""

import json
import os
import threading
from typing import Any, Callable

import pika
from pika import BasicProperties, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingConnection

from src.shared.events.cutter_events import CutterEvent, CutterCreatedEvent, CutterUpdatedEvent, CutterDeletedEvent


class RabbitMQEventConsumer:
    """RabbitMQ事件消费者"""

    EXCHANGE = "cnc.events"
    EXCHANGE_TYPE = "topic"
    QUEUE = "ai-service.cutter-events"

    def __init__(self) -> None:
        self._rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@111.228.18.127:5672/")
        self._connection = None
        self._channel = None
        self._handlers: dict[str, list[Callable]] = {}
        self._running = False

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

        # 声明队列
        self._channel.queue_declare(queue=self.QUEUE, durable=True)

        # 绑定队列到交换机
        self._channel.queue_bind(
            exchange=self.EXCHANGE,
            queue=self.QUEUE,
            routing_key="cutter.*",
        )

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """注册事件处理器"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def _process_message(self, channel, method, properties, body) -> None:
        """处理消息"""
        try:
            data = json.loads(body.decode("utf-8"))
            event_type = data.get("event_type", "")
            routing_key = method.routing_key

            print(f"[EventConsumer] Received {routing_key}: {data.get('event_id', 'unknown')}")

            # 调用注册的处理器
            for handler in self._handlers.get(event_type, []):
                try:
                    handler(data)
                except Exception as e:
                    print(f"[EventConsumer] Handler error for {event_type}: {e}")

            # 确认消息
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[EventConsumer] Error processing message: {e}")
            # 拒绝消息，不重新入队
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self) -> None:
        """开始消费消息"""
        self._connect()
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(
            queue=self.QUEUE,
            on_message_callback=self._process_message,
        )

        print("[EventConsumer] Waiting for messages...")
        self._running = True

        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self._channel.stop_consuming()
        finally:
            self._connection.close()

    def start_async(self) -> None:
        """在后台线程中开始消费消息"""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        print("[EventConsumer] Background consumer started")

    def stop(self) -> None:
        """停止消费"""
        self._running = False
        if self._channel:
            self._channel.stop_consuming()
        if self._connection:
            self._connection.close()


def create_cutter_event_handler(vector_repo) -> Callable:
    """创建刀具事件处理器"""

    def handle_cutter_event(data: dict[str, Any]) -> None:
        """处理刀具事件"""
        event = CutterEvent.from_dict(data)

        if isinstance(event, CutterCreatedEvent):
            # 新刀具创建，需要从cutter-management获取详情并索引
            # 这里简化处理，实际应该调用cutter-management API获取完整数据
            print(f"[EventHandler] Cutter created: {event.cutter_id}, scheduling index update")
            # TODO: 实现从cutter-management获取刀具详情并索引到ChromaDB

        elif isinstance(event, CutterUpdatedEvent):
            print(f"[EventHandler] Cutter updated: {event.cutter_id}, scheduling index update")
            # TODO: 实现更新ChromaDB中的向量索引

        elif isinstance(event, CutterDeletedEvent):
            print(f"[EventHandler] Cutter deleted: {event.cutter_id}, removing from index")
            # 删除向量
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(vector_repo.delete(event.cutter_id))
            except RuntimeError:
                asyncio.run(vector_repo.delete(event.cutter_id))

    return handle_cutter_event


def setup_event_consumer(vector_repo) -> RabbitMQEventConsumer:
    """设置事件消费者"""
    consumer = RabbitMQEventConsumer()

    # 注册处理器
    handler = create_cutter_event_handler(vector_repo)
    consumer.register_handler("cutter.created", handler)
    consumer.register_handler("cutter.updated", handler)
    consumer.register_handler("cutter.deleted", handler)

    return consumer
