from copy import copy
from typing import TYPE_CHECKING

from .object import (
    ContractData,
    OrderData,
    TradeData,
    PositionData,
    OrderRequest
)
from .constant import Direction, Offset, Exchange

if TYPE_CHECKING:
    from .engine import OmsEngine


class PositionHolding:
    """
    合约的仓位账本
    """

    def __init__(self, contract: ContractData) -> None:
        """"""
        self.vt_symbol: str = contract.vt_symbol
        self.exchange: Exchange = contract.exchange

        self.active_orders: dict[str, OrderData] = {}

        # 多头总持仓
        self.long_pos: float = 0
        # 多头昨仓
        self.long_yd: float = 0
        # 多头今仓
        self.long_td: float = 0

        # 空头总持仓
        self.short_pos: float = 0
        # 空头昨仓
        self.short_yd: float = 0
        # 空头今仓
        self.short_td: float = 0

        # 多头持仓被冻结的
        self.long_pos_frozen: float = 0
        # 多头昨仓被冻结的
        self.long_yd_frozen: float = 0
        # 多头今仓被冻结的
        self.long_td_frozen: float = 0

        # 空头持仓被冻结的
        self.short_pos_frozen: float = 0
        # 空头昨仓被冻结的
        self.short_yd_frozen: float = 0
        # 空头今仓被冻结的
        self.short_td_frozen: float = 0

    def update_position(self, position: PositionData) -> None:
        """"""
        if position.direction == Direction.LONG:
            self.long_pos = position.volume
            self.long_yd = position.yd_volume
            self.long_td = self.long_pos - self.long_yd
        else:
            self.short_pos = position.volume
            self.short_yd = position.yd_volume
            self.short_td = self.short_pos - self.short_yd

    def update_order(self, order: OrderData) -> None:
        """"""
        if order.is_active():
            self.active_orders[order.vt_orderid] = order
        else:
            if order.vt_orderid in self.active_orders:
                self.active_orders.pop(order.vt_orderid)

        self.calculate_frozen()

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """"""
        gateway_name, orderid = vt_orderid.split(".")

        order: OrderData = req.create_order_data(orderid, gateway_name)
        self.update_order(order)

    def update_trade(self, trade: TradeData) -> None:
        """
        核心方法
        """
        if trade.direction == Direction.LONG:  # 多头
            if trade.offset == Offset.OPEN:    # 开仓买入
                self.long_td += trade.volume   # 今仓增加成交量
            elif trade.offset == Offset.CLOSETODAY: # 平今
                self.short_td -= trade.volume  # 空头今仓减去成交量
            elif trade.offset == Offset.CLOSEYESTERDAY: # 平昨
                self.short_yd -= trade.volume  # 空头昨仓减去成交量
            elif trade.offset == Offset.CLOSE: # 平仓
                if trade.exchange in {Exchange.SHFE, Exchange.INE}:
                    self.short_yd -= trade.volume # 优先平昨仓
                else:
                    self.short_td -= trade.volume # 优先平今仓

                    if self.short_td < 0:       # 今仓平完后，还有待平的仓
                        self.short_yd += self.short_td # 从昨仓中扣
                        self.short_td = 0       # 今仓归零，不可为负数了，昨仓中补扣了
        else:                                   # 空头                              
            if trade.offset == Offset.OPEN:     # 空头开仓 - 卖出
                self.short_td += trade.volume   # 空头今仓增加成交量
            elif trade.offset == Offset.CLOSETODAY: # 平今
                self.long_td -= trade.volume        # 今仓减去成交量
            elif trade.offset == Offset.CLOSEYESTERDAY: # 平昨
                self.long_yd -= trade.volume        # 昨仓减去成交量
            elif trade.offset == Offset.CLOSE:      # 平仓
                if trade.exchange in {Exchange.SHFE, Exchange.INE}:
                    self.long_yd -= trade.volume # 优先平昨仓的情况
                else:
                    self.long_td -= trade.volume # 优先平今仓的情况

                    if self.long_td < 0: # 今仓平完后，未满足平仓的数量
                        self.long_yd += self.long_td # 继续平昨仓
                        self.long_td = 0 # 今仓 < 0置为0

        self.long_pos = self.long_td + self.long_yd    # 多头持仓量
        self.short_pos = self.short_td + self.short_yd # 空头持仓量

        # Update frozen volume to ensure no more than total volume
        self.sum_pos_frozen()

    def calculate_frozen(self) -> None:
        """
        计算冻结量。下了平仓委托单，但还没有成交 - 这部分仓位不能再被别的委托单用掉
        """
        self.long_pos_frozen = 0
        self.long_yd_frozen = 0
        self.long_td_frozen = 0

        self.short_pos_frozen = 0
        self.short_yd_frozen = 0
        self.short_td_frozen = 0

        for order in self.active_orders.values():
            # Ignore position open orders
            if order.offset == Offset.OPEN: # 忽略开仓单，只看平仓单
                continue

            frozen: float = order.volume - order.traded # 委托量 - 已成交量 = 还在等待成交的量

            if order.direction == Direction.LONG: # 多头的情况
                if order.offset == Offset.CLOSETODAY: # 平今 
                    self.short_td_frozen += frozen  # 空头今仓冻结增加
                elif order.offset == Offset.CLOSEYESTERDAY: # 平昨
                    self.short_yd_frozen += frozen # 空头昨仓冻结增加
                elif order.offset == Offset.CLOSE: # 平
                    self.short_td_frozen += frozen # 空头今仓冻结增加

                    if self.short_td_frozen > self.short_td: # 空头今仓冻结大于空头今仓，说明了有昨仓冻结
                        self.short_yd_frozen += (self.short_td_frozen # 昨仓冻结增加这个多出来的仓，即空头今仓冻结数量减去空头今仓数量
                                                 - self.short_td)
                        self.short_td_frozen = self.short_td # 空头今仓冻结重置为空头今仓的数量，即空头今仓全部冻结啦
            elif order.direction == Direction.SHORT: # 空头的情况
                if order.offset == Offset.CLOSETODAY: # 平今
                    self.long_td_frozen += frozen # 多头今仓冻结增加
                elif order.offset == Offset.CLOSEYESTERDAY: # 平昨
                    self.long_yd_frozen += frozen # 多头昨仓冻结增加
                elif order.offset == Offset.CLOSE: # 平仓
                    self.long_td_frozen += frozen  # 多头今仓冻结增加

                    if self.long_td_frozen > self.long_td: # 多头今仓冻结数量大于多头今仓数量，说明算多了，昨仓冻结算到今仓冻结头上啦
                        self.long_yd_frozen += (self.long_td_frozen # 把多出来的数量，加到多头昨仓冻结数量上
                                                - self.long_td)
                        self.long_td_frozen = self.long_td # 把多头今仓冻结的数量设置为多头今仓数量，多算的应该减去

        self.sum_pos_frozen()

    def sum_pos_frozen(self) -> None:
        """"""
        # Frozen volume should be no more than total volume
        self.long_td_frozen = min(self.long_td_frozen, self.long_td)
        self.long_yd_frozen = min(self.long_yd_frozen, self.long_yd)

        self.short_td_frozen = min(self.short_td_frozen, self.short_td)
        self.short_yd_frozen = min(self.short_yd_frozen, self.short_yd)

        self.long_pos_frozen = self.long_td_frozen + self.long_yd_frozen
        self.short_pos_frozen = self.short_td_frozen + self.short_yd_frozen

    def convert_order_request_shfe(self, req: OrderRequest) -> list[OrderRequest]:
        """
        上期所在平仓时拆单逻辑，优先昨仓。
        """
        if req.offset == Offset.OPEN:
            return [req]

        if req.direction == Direction.LONG:
            pos_available: float = self.short_pos - self.short_pos_frozen
            td_available: float = self.short_td - self.short_td_frozen
        else:
            pos_available = self.long_pos - self.long_pos_frozen
            td_available = self.long_td - self.long_td_frozen

        if req.volume > pos_available:
            return []
        elif req.volume <= td_available:
            req_td: OrderRequest = copy(req)
            req_td.offset = Offset.CLOSETODAY
            return [req_td]
        else:
            req_list: list[OrderRequest] = []

            if td_available > 0:
                req_td = copy(req)
                req_td.offset = Offset.CLOSETODAY
                req_td.volume = td_available
                req_list.append(req_td)

            req_yd: OrderRequest = copy(req)
            req_yd.offset = Offset.CLOSEYESTERDAY
            req_yd.volume = req.volume - td_available
            req_list.append(req_yd)

            return req_list

    def convert_order_request_lock(self, req: OrderRequest) -> list[OrderRequest]:
        """
        锁仓 = 做多同时做空。当你想平仓但交易所不支持直接平仓，反向开仓来锁住。
        """
        if req.direction == Direction.LONG:
            td_volume: float = self.short_td
            yd_available: float = self.short_yd - self.short_yd_frozen
        else:
            td_volume = self.long_td
            yd_available = self.long_yd - self.long_yd_frozen

        close_yd_exchanges: set[Exchange] = {Exchange.SHFE, Exchange.INE}

        # If there is td_volume, we can only lock position
        if td_volume and self.exchange not in close_yd_exchanges:
            req_open: OrderRequest = copy(req)
            req_open.offset = Offset.OPEN
            return [req_open]
        # If no td_volume, we close opposite yd position first
        # then open new position
        else:
            close_volume: float = min(req.volume, yd_available)
            open_volume: float = max(0, req.volume - yd_available)
            req_list: list[OrderRequest] = []

            if yd_available:
                req_yd: OrderRequest = copy(req)
                if self.exchange in close_yd_exchanges:
                    req_yd.offset = Offset.CLOSEYESTERDAY
                else:
                    req_yd.offset = Offset.CLOSE
                req_yd.volume = close_volume
                req_list.append(req_yd)

            if open_volume:
                req_open = copy(req)
                req_open.offset = Offset.OPEN
                req_open.volume = open_volume
                req_list.append(req_open)

            return req_list

    def convert_order_request_net(self, req: OrderRequest) -> list[OrderRequest]:
        """
        净仓：最复杂的转换，合并了SHFE规则 + 拆单 + 不足时反向开仓
        """
        if req.direction == Direction.LONG:
            pos_available: float = self.short_pos - self.short_pos_frozen
            td_available: float = self.short_td - self.short_td_frozen
            yd_available: float = self.short_yd - self.short_yd_frozen
        else:
            pos_available = self.long_pos - self.long_pos_frozen
            td_available = self.long_td - self.long_td_frozen
            yd_available = self.long_yd - self.long_yd_frozen

        # Split close order to close today/yesterday for SHFE/INE exchange
        if req.exchange in {Exchange.SHFE, Exchange.INE}:
            reqs: list[OrderRequest] = []
            volume_left: float = req.volume

            if td_available:
                td_volume: float = min(td_available, volume_left)
                volume_left -= td_volume

                td_req: OrderRequest = copy(req)
                td_req.offset = Offset.CLOSETODAY
                td_req.volume = td_volume
                reqs.append(td_req)

            if volume_left and yd_available:
                yd_volume: float = min(yd_available, volume_left)
                volume_left -= yd_volume

                yd_req: OrderRequest = copy(req)
                yd_req.offset = Offset.CLOSEYESTERDAY
                yd_req.volume = yd_volume
                reqs.append(yd_req)

            if volume_left > 0:
                open_volume: float = volume_left

                open_req: OrderRequest = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs
        # Just use close for other exchanges
        else:
            reqs = []
            volume_left = req.volume

            if pos_available:
                close_volume: float = min(pos_available, volume_left)
                volume_left -= pos_available

                close_req: OrderRequest = copy(req)
                close_req.offset = Offset.CLOSE
                close_req.volume = close_volume
                reqs.append(close_req)

            if volume_left > 0:
                open_volume = volume_left

                open_req = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs


class OffsetConverter:
    """
    门面层
    管所有合约
    """

    def __init__(self, oms_engine: "OmsEngine") -> None:
        """"""
        self.holdings: dict[str, PositionHolding] = {}

        self.get_contract = oms_engine.get_contract

    def update_position(self, position: PositionData) -> None:
        """"""
        if not self.is_convert_required(position.vt_symbol):
            return

        holding: PositionHolding | None = self.get_position_holding(position.vt_symbol)
        if holding:
            holding.update_position(position)

    def update_trade(self, trade: TradeData) -> None:
        """"""
        if not self.is_convert_required(trade.vt_symbol):
            return

        holding: PositionHolding | None = self.get_position_holding(trade.vt_symbol)
        if holding:
            holding.update_trade(trade)

    def update_order(self, order: OrderData) -> None:
        """"""
        if not self.is_convert_required(order.vt_symbol):
            return

        holding: PositionHolding | None = self.get_position_holding(order.vt_symbol)
        if holding:
            holding.update_order(order)

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return

        holding: PositionHolding | None = self.get_position_holding(req.vt_symbol)
        if holding:
            holding.update_order_request(req, vt_orderid)

    def get_position_holding(self, vt_symbol: str) -> PositionHolding | None:
        """"""
        holding: PositionHolding | None = self.holdings.get(vt_symbol, None)

        if not holding:
            contract: ContractData | None = self.get_contract(vt_symbol)
            if contract:
                holding = PositionHolding(contract)
                self.holdings[vt_symbol] = holding

        return holding

    def convert_order_request(
        self,
        req: OrderRequest,
        lock: bool,
        net: bool = False
    ) -> list[OrderRequest]:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return [req]

        holding: PositionHolding | None = self.get_position_holding(req.vt_symbol)

        if not holding:
            return [req]
        elif lock:
            return holding.convert_order_request_lock(req)
        elif net:
            return holding.convert_order_request_net(req)
        elif req.exchange in {Exchange.SHFE, Exchange.INE}:
            return holding.convert_order_request_shfe(req)
        else:
            return [req]

    def is_convert_required(self, vt_symbol: str) -> bool:
        """
        Check if the contract needs offset convert.
        """
        contract: ContractData | None = self.get_contract(vt_symbol)

        # Only contracts with long-short position mode requires convert
        if not contract:
            return False
        elif contract.net_position:
            return False
        else:
            return True
