"""
Event-driven framework of VeighNa framework.
"""

# 懒创建handler列表
from collections import defaultdict
# 类型注解：这是一个回调函数
from collections.abc import Callable
# 线程安全的事件队列
from queue import Empty, Queue
# 后台线程
from threading import Thread
# 定时器等待
from time import sleep
# 类型注解：Any表示任意类型
from typing import Any

# 常量放模块顶层，没用Enum。为什么？ 
# 因为vnpy的设计允许用户自定义事件类型，Enum不允许动态添加成员，所以用字符串常量更灵活。
# 缺点：需要手动管理字符串常量，容易出错。

EVENT_TIMER = "eTimer"

# 注意，这里没有使用@dataclass装饰器， 而是手动实现了__init__方法。原因是Event对象的data属性可以是任意类型，而@dataclass默认会对所有属性生成__init__方法，可能不适合这种灵活的设计。
class Event:
    """
    Event object consists of a type string which is used
    by event engine for distributing event, and a data
    object which contains the real data.
    """

# 双下划线方法，被称为魔术方法或特殊方法
# 主要由Python解释器在特定时刻调用
# 不是由程序员显示调用
# 作用：为类提供钩子，允许自定义类的行为，使其更像内置类型（整数，列表，字典，字符串）一样工作。
    def __init__(self, type: str, data: Any = None) -> None:
        """"""
        # 事件类型字符串，用于事件引擎分发事件
        self.type: str = type
        # 事件数据，可以是任意类型
        self.data: Any = data

# 读法： Callable[[参数类型], 返回值类型]。 [[Event], None] 表示这是一个接收Event对象，返回None的一个函数。
# Defines handler function to be used in event engine.
HandlerType = Callable[[Event], None]


# 有6部分
class EventEngine:
    """
    Event engine distributes event object based on its type
    to those handlers registered.

    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    """

# 1. 初始化
    def __init__(self, interval: int = 1) -> None:
        """
        Timer event is generated every 1 second by default, if
        interval not specified.
        """
        # 事件引擎的定时器间隔，单位为秒
        self._interval: int = interval
        # 事件队列，用于存放待处理的事件对象
        self._queue: Queue = Queue()
        # 事件引擎的运行状态，True表示正在运行，False表示停止
        self._active: bool = False
        # 事件引擎的后台线程，用于处理事件（消费者线程）,此时Thread已经创建，尚未启动。
        self._thread: Thread = Thread(target=self._run)
        # 定时器线程，用于生成定时事件
        self._timer: Thread = Thread(target=self._run_timer)
        # 事件类型到处理函数列表的映射，使用defaultdict方便管理，访问不存在的键时会自动创建一个空列表
        # java：
        # Map<String, List<HandlerType>> handlers = new HashMap<>();
        # handlers.putIfAbsent(type, new ArrayList<>());
        self._handlers: defaultdict = defaultdict(list)
        # 处理所有事件的通用处理函数列表
        self._general_handlers: list = []

# 2. 事件引擎的主循环，获取事件并处理
    def _run(self) -> None:
        """
        Get event from queue and then process it.
        从队列中获取事件，然后处理它。
        """
        # active，默认false，在start()方法中被设置为True，表示事件引擎正在运行。在stop()方法中被设置为False，表示事件引擎停止运行。
        while self._active:
            try:
                # block = True表示如果队列为空，线程会阻塞等待，直到有事件被放入队列。timeout=1表示最多等待1秒，如果1秒内没有事件到来，会抛出Empty异常。
                event: Event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                # pass 忽略，回到while循环的开头，检测active。继续等待事件到来
                pass

# 3. 处理事件，分发给注册的处理函数
    def _process(self, event: Event) -> None:
        """
        First distribute event to those handlers registered listening
        to this type.

        Then distribute event to those general handlers which listens
        to all types.
        """
        # 特定处理器，只关心特定类型的事件
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        # 通用处理器，关心所有类型的事件，用于全局日志记录、监控等
        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

# 4. 定时器线程，定期生成定时事件
    def _run_timer(self) -> None:
        """
        Sleep by interval second(s) and then generate a timer event.
        """
        # 一个独立线程，每秒向队列塞一个Event("eTimer").策略可以用它做心跳检测，定时调仓等。
        while self._active:
            sleep(self._interval)
            event: Event = Event(EVENT_TIMER)
            self.put(event)

# 5. 生命周期start/stop
    def start(self) -> None:
        """
        Start event engine to process events and generate timer events.
        """
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """
        Stop event engine.
        """
        self._active = False
        # 先退出定时器，再退出事件处理线程，避免事件处理线程在定时器线程还在运行时退出，导致定时器线程向已关闭的队列发送事件，引发异常。
        self._timer.join() 
        # join()方法会阻塞当前线程(一般是主线程)，直到被调用的线程(一般是子线程例如这里的定时器或事件处理线程)终止。这里是为了确保事件处理线程在stop()方法返回前已经完全退出，避免资源泄漏或未处理的事件。
        self._thread.join()

# 6. register/put 事件引擎的接口，提供给外部使用 - 生产者
    def put(self, event: Event) -> None:
        """
        Put an event object into event queue.
        """
        self._queue.put(event)

# 增加新的type事件
    def register(self, type: str, handler: HandlerType) -> None:
        """
        Register a new handler function for a specific event type. Every
        function can only be registered once for each event type.
        """
        handler_list: list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        Unregister an existing handler function from event engine.
        """
        handler_list: list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """
        Register a new handler function for all event types. Every
        function can only be registered once for each event type.
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """
        Unregister an existing general handler function.
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)
