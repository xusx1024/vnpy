"""
练习 1-A：手写一个微型 EventBus（单线程版）
需求：
    1. register(event_type: str, handler: callable) → 注册处理器
    2. post(event_type: str, data) → 派发事件
    3. 同一个 type 可以有多个 handler

写完后用底部的测试代码验证。
"""

from collections import defaultdict
from typing import Any, Callable
from vnpy.event.engine import Event


# 提示：Event 类只需要 type + data 两个字段

# 你的 MyEventBus 类写在这里 ↓
class MyEventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event_type: str, handler: Callable) -> None:
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def post(self, event_type: str, data: Any = None) -> None:
        event = Event(event_type, data)
        for handler in self._handlers[event_type]:
            handler(event)


# ============================================================
# 测试代码（不要改）
# ============================================================
if __name__ == "__main__":
    bus = MyEventBus()

    received_ticks = []
    received_orders = []

    def on_tick(event):
        received_ticks.append(event.data)

    def on_order(event):
        received_orders.append(event.data)

    bus.register("eTick", on_tick)
    bus.register("eTick", on_tick)  # 重复注册，不应重复触发
    bus.register("eOrder", on_order)

    bus.post("eTick", {"symbol": "000725", "price": 5.28})
    bus.post("eOrder", {"orderid": "T001"})

    assert len(received_ticks) == 1, f"期望 1 个 tick，实际 {len(received_ticks)}"
    assert len(received_orders) == 1, f"期望 1 个 order，实际 {len(received_orders)}"
    print("[OK] Tick handler 收到:", received_ticks[0])
    print("[OK] Order handler 收到:", received_orders[0])
    print("测试通过！")
