# 接口层

from abc import ABC, abstractmethod

from vnpy.event import Event, EventEngine
from .event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE,
    EVENT_POSITION,
    EVENT_ACCOUNT,
    EVENT_CONTRACT,
    EVENT_LOG,
    EVENT_QUOTE,
)
from .object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    LogData,
    QuoteData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest,
    QuoteRequest,
    Exchange,
    BarData
)


class BaseGateway(ABC):
    """
    网关抽象类，用于创建与不同交易系统的网关连接。
    Abstract gateway class for creating gateways connection
    to different trading systems.

    如何实现一个网关：
    # How to implement a gateway:

    ---
    基本要求：
    ## Basics
    一个网关应该满足：
    A gateway should satisfies:
    应该是线程安全的类
    * this class should be thread-safe:
        所有方法都应该是线程安全的
        * all methods should be thread-safe
        所有对象之间不应该有可变的共享属性
        * no mutable shared properties between objects.
    所有方法都应该是非阻塞的
    * all methods should be non-blocked
    满足每一个方法和回调的文档注释中的所有要求
    * satisfies all requirements written in docstring for every method and callbacks.
    丢失连接后应该自动重连
    * automatically reconnect if connection lost.

    ---
    方法必须实现：@abstractmethod
    ## methods must implements:
    all @abstractmethod

    # 回调务必手动响应：
    ---
    ## callbacks must response manually:
    * on_tick
    * on_trade
    * on_order
    * on_position
    * on_account
    * on_contract

    # 所有传递给回调的 XxxData 都应该是常量对象，也就是说在传递给 on_xxxx 后不应该再修改该对象。
    # 因此如果你使用了缓存来存储数据的引用，请在传递该数据到 on_xxxx 之前使用 copy.copy 创建一个新的对象。
    All the XxxData passed to callback should be constant, which means that
        the object should not be modified after passing to on_xxxx.
    So if you use a cache to store reference of data, use copy.copy to create a new object
    before passing that data into on_xxxx



    """

    # Default name for the gateway.
    default_name: str = ""

    # Fields required in setting dict for connect function.
    default_setting: dict[str, str | int | float | bool] = {}

    # Exchanges supported in the gateway.
    exchanges: list[Exchange] = []

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """"""
        self.event_engine: EventEngine = event_engine
        self.gateway_name: str = gateway_name

    def on_event(self, type: str, data: object = None) -> None:
        """
        核心：把数据包装成事件对象，放入事件引擎队列
        一切事件发射的底层方法
        General event push.
        """
        event: Event = Event(type, data)
        self.event_engine.put(event)

# Tick事件是市场动态
    def on_tick(self, tick: TickData) -> None:
        """
        Tick Data：市场变动，报价变化，就算没有成交量（volume），也会有tick数据。
        Tick event push.
        Tick event of a specific vt_symbol is also pushed.
        """
        self.on_event(EVENT_TICK, tick)
        self.on_event(EVENT_TICK + tick.vt_symbol, tick)

# Trade事件是事实发生
    def on_trade(self, trade: TradeData) -> None:
        """
        Trade Data：逐笔成交数据，只包含真实发生的买卖记录。
        Trade event push.
        Trade event of a specific vt_symbol is also pushed.
        """
        self.on_event(EVENT_TRADE, trade)
        self.on_event(EVENT_TRADE + trade.vt_symbol, trade)

# Order事件是你的意愿
    def on_order(self, order: OrderData) -> None:
        """
        Order Data：订单/委托单，这是向交易所发出的买卖请求，表示“我想买/卖多少数量的股票，价格是多少”
        Order event push.
        Order event of a specific vt_orderid is also pushed.
        """
        self.on_event(EVENT_ORDER, order)
        self.on_event(EVENT_ORDER + order.vt_orderid, order)

# Position事件是你的持仓
    def on_position(self, position: PositionData) -> None:
        """
        Position event push.
        Position event of a specific vt_symbol is also pushed.
        """
        self.on_event(EVENT_POSITION, position)
        self.on_event(EVENT_POSITION + position.vt_symbol, position)

# Account事件是你的账户，包括余额，冻结，可用资金
    def on_account(self, account: AccountData) -> None:
        """
        Account event push.
        Account event of a specific vt_accountid is also pushed.
        """
        self.on_event(EVENT_ACCOUNT, account)
        self.on_event(EVENT_ACCOUNT + account.vt_accountid, account)

# Quote事件是报价事件
    def on_quote(self, quote: QuoteData) -> None:
        """
        Quote event push.
        Quote event of a specific vt_symbol is also pushed.
        """
        self.on_event(EVENT_QUOTE, quote)
        self.on_event(EVENT_QUOTE + quote.vt_symbol, quote)

# Log事件是用来记录日志消息的
    def on_log(self, log: LogData) -> None:
        """
        Log event push.
        """
        self.on_event(EVENT_LOG, log)

# 合同事件包含每笔交易合同的基本信息
    def on_contract(self, contract: ContractData) -> None:
        """
        Contract event push.
        """
        self.on_event(EVENT_CONTRACT, contract)

# 快捷从网关写日志
    def write_log(self, msg: str) -> None:
        """
        Write a log event from gateway.
        """
        log: LogData = LogData(msg=msg, gateway_name=self.gateway_name)
        self.on_log(log)

    @abstractmethod
    def connect(self, setting: dict) -> None:
        """
        # 开始网关连接
        Start gateway connection.

        to implement this method, you must:
        # 如有必要，连接到服务器
        * connect to server if necessary
        # 连接成功后，写日志
        * log connected if all necessary connection is established
        # 连接成功后，查询账户信息，合约信息，持仓信息，订单信息，成交信息并且写日志
        * do the following query and response corresponding on_xxxx and write_log
            * contracts : on_contract
            * account asset : on_account
            * account holding: on_position
            * orders of account: on_order
            * trades of account: on_trade
        # 如果以上任何查询失败，写日志
        * if any of query above is failed,  write log.

        future plan:
        # 未来计划：响应回调/改变状态，而不是写日志
        response callback/change status instead of write_log

        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close gateway connection.
        """
        pass

    @abstractmethod
    def subscribe(self, req: SubscribeRequest) -> None:
        """
        Subscribe tick data update.
        """
        pass

    @abstractmethod
    def send_order(self, req: OrderRequest) -> str:
        """
        Send a new order to server.
        # 发送委托单到服务器
        implementation should finish the tasks blow:
        # 创建一个OrderData对象，使用OrderRequest.create_order_data方法
        * create an OrderData from req using OrderRequest.create_order_data
        # 给OrderData.orderid分配一个唯一的id（网关实例范围内唯一）
        * assign a unique(gateway instance scope) id to OrderData.orderid
        * send request to server
            # 如果请求发送成功，OrderData.status应该设置为Status.SUBMITTING
            * if request is sent, OrderData.status should be set to Status.SUBMITTING
            # 如果请求发送失败，OrderData.status应该设置为Status.REJECTED
            * if request is failed to sent, OrderData.status should be set to Status.REJECTED
        * response on_order:
        * return vt_orderid

        :return str vt_orderid for created OrderData
        """
        pass

    @abstractmethod
    def cancel_order(self, req: CancelRequest) -> None:
        """
        # 取消已经存在的委托单
        Cancel an existing order.
        implementation should finish the tasks blow:
        * send request to server
        """
        pass

    def send_quote(self, req: QuoteRequest) -> str:
        """
        Send a new two-sided quote to server.
        # 发送双向报价到服务器

        implementation should finish the tasks blow:
        # 通过QuoteRequest.create_quote_data方法创建一个QuoteData对象
        * create an QuoteData from req using QuoteRequest.create_quote_data
        # 给QuoteData.quoteid分配一个唯一的id（网关实例范围内唯一）
        * assign a unique(gateway instance scope) id to QuoteData.quoteid
        * send request to server
            # 如果请求发送成功，QuoteData.status应该设置为Status.SUBMITTING
            * if request is sent, QuoteData.status should be set to Status.SUBMITTING
            # 如果请求失败，QuoteData.staus应该设置为Status.REJECTED
            * if request is failed to sent, QuoteData.status should be set to Status.REJECTED
        * response on_quote:
        * return vt_quoteid

        :return str vt_quoteid for created QuoteData
        """
        return ""

    def cancel_quote(self, req: CancelRequest) -> None:
        """
        # 取消已存在的报价
        Cancel an existing quote.
        # 该实现应该关闭下列任务：
        implementation should finish the tasks blow:
        # 发送报价到服务
        * send request to server
        """
        return

    @abstractmethod
    def query_account(self) -> None:
        """
        查询账户余额
        Query account balance.
        """
        pass

    @abstractmethod
    def query_position(self) -> None:
        """
        查询持仓情况
        Query holding positions.
        """
        pass

    def query_history(self, req: HistoryRequest) -> list[BarData]:
        """
        查询K线图
        Query bar history data.
        """
        return []

    def get_default_setting(self) -> dict[str, str | int | float | bool]:
        """
        返回默认设置字典
        Return default setting dict.
        """
        return self.default_setting
