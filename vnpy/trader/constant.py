# 1. Python枚举没有类型约束，java中enum里字段类型统一
# 2. Python枚举没有values，用list(Interval)遍历
# 3. Python Enum实例是全局单例，可以直接==比较

"""
General constant enums used in the trading platform.
"""

# Python 标准库 Enum基类
from enum import Enum

# 相对导入
# 从当前包下locale模块导入_函数，用于国际化翻译
from .locale import _


class Direction(Enum):
    """
    Direction of order/trade/position.
    """
    # 构造函数中传入的参数是枚举成员的值，_()函数用于国际化翻译
    LONG = _("多")
    SHORT = _("空")
    NET = _("净") # 净持仓
 
class Offset(Enum):
    """
    
    Offset of order/trade.
    中国期货市场有一条特殊规则： 
    - 今天开仓2手，这是今仓
    - 昨天开仓3手，这是昨仓

    现在你想平掉4手：
    - 上期所（SHFE）：优先平昨仓，先扣3手昨仓，再扣1手今仓
    - 大商所（DCE）：优先平今仓，先扣2手今仓，再扣2手昨仓
    平今，免手续费，所以扣的顺序影响成本。

    """
    NONE = ""
    # 开仓
    OPEN = _("开")
    # 平仓
    CLOSE = _("平")
    # 平今日开的仓
    CLOSETODAY = _("平今")
    # 平昨日及以前开的仓
    CLOSEYESTERDAY = _("平昨")

# 订单状态机
class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = _("提交中")
    NOTTRADED = _("未成交")
    PARTTRADED = _("部分成交")
    ALLTRADED = _("全部成交")
    CANCELLED = _("已撤销")
    REJECTED = _("拒单")


class Product(Enum):
    """
    Product class.
    """
    EQUITY = _("股票")
    FUTURES = _("期货")
    OPTION = _("期权")
    INDEX = _("指数")
    FOREX = _("外汇")
    SPOT = _("现货")
    ETF = "ETF"
    BOND = _("债券")
    WARRANT = _("权证")
    SPREAD = _("价差")
    FUND = _("基金")
    CFD = "CFD"
    SWAP = _("互换")


class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = _("限价")
    MARKET = _("市价")
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = _("询价")
    ETF = "ETF"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = _("看涨期权")
    PUT = _("看跌期权")

# 交易所枚举
class Exchange(Enum):
    """
    Exchange.
    Financial Futures 金融期货
    Futures 期货
    Commodity 大宗商品
    International Energy 国际能源
    Stock 证券
    """
    # Chinese
    CFFEX = "CFFEX"         # China Financial Futures Exchange
    SHFE = "SHFE"           # Shanghai Futures Exchange
    CZCE = "CZCE"           # Zhengzhou Commodity Exchange
    DCE = "DCE"             # Dalian Commodity Exchange
    INE = "INE"             # Shanghai International Energy Exchange
    GFEX = "GFEX"           # Guangzhou Futures Exchange
    SSE = "SSE"             # Shanghai Stock Exchange
    SZSE = "SZSE"           # Shenzhen Stock Exchange
    BSE = "BSE"             # Beijing Stock Exchange
    SHHK = "SHHK"           # Shanghai-HK Stock Connect
    SZHK = "SZHK"           # Shenzhen-HK Stock Connect
    SGE = "SGE"             # Shanghai Gold Exchange
    WXE = "WXE"             # Wuxi Steel Exchange 无锡不锈钢电子交易中心
    CFETS = "CFETS"         # CFETS Bond Market Maker Trading System 中国外汇交易中心本币交易系统
    XBOND = "XBOND"         # CFETS X-Bond Anonymous Trading System 中国外汇交易中心 X-Bond 匿名点击成交系统

    # Global
    SMART = "SMART"         # Smart Router for US stocks
    NYSE = "NYSE"           # New York Stock Exchnage
    NASDAQ = "NASDAQ"       # Nasdaq Exchange
    ARCA = "ARCA"           # ARCA Exchange
    EDGEA = "EDGEA"         # Direct Edge Exchange
    ISLAND = "ISLAND"       # Nasdaq Island ECN
    BATS = "BATS"           # Bats Global Markets
    IEX = "IEX"             # The Investors Exchange
    AMEX = "AMEX"           # American Stock Exchange
    TSE = "TSE"             # Toronto Stock Exchange
    NYMEX = "NYMEX"         # New York Mercantile Exchange
    COMEX = "COMEX"         # COMEX of CME
    GLOBEX = "GLOBEX"       # Globex of CME
    IDEALPRO = "IDEALPRO"   # Forex ECN of Interactive Brokers
    CME = "CME"             # Chicago Mercantile Exchange
    ICE = "ICE"             # Intercontinental Exchange
    SEHK = "SEHK"           # Stock Exchange of Hong Kong
    HKFE = "HKFE"           # Hong Kong Futures Exchange
    SGX = "SGX"             # Singapore Global Exchange
    CBOT = "CBOT"           # Chicago Board of Trade
    CBOE = "CBOE"           # Chicago Board Options Exchange
    CFE = "CFE"             # CBOE Futures Exchange
    DME = "DME"             # Dubai Mercantile Exchange
    EUREX = "EUX"           # Eurex Exchange
    APEX = "APEX"           # Asia Pacific Exchange
    LME = "LME"             # London Metal Exchange
    BMD = "BMD"             # Bursa Malaysia Derivatives
    TOCOM = "TOCOM"         # Tokyo Commodity Exchange
    EUNX = "EUNX"           # Euronext Exchange
    KRX = "KRX"             # Korean Exchange
    OTC = "OTC"             # OTC Product (Forex/CFD/Pink Sheet Equity)
    IBKRATS = "IBKRATS"     # Paper Trading Exchange of IB

    # Special Function
    LOCAL = "LOCAL"         # For local generated data
    GLOBAL = "GLOBAL"       # For those exchanges not supported yet


class Currency(Enum):
    """
    Currency.
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"

# K线周期
class Interval(Enum):
    """
    Interval of bar data.
    """
    MINUTE = "1m"
    HOUR = "1h"
    DAILY = "d"
    WEEKLY = "w"
    TICK = "tick"
