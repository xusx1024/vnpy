# 模块级字符串常量

# 该文件等于Java的常量接口（虽然Java不推荐，见Effective Java）
# Python没有接口，直接用模块级别的字符串常量

"""
Event type string used in the trading platform.
"""
# noqa = No Quality Assurance，告诉IDE不要检查代码质量
# 实际用途：其他模块可以直接import这个模块，然后使用这些字符串常量作为事件类型，避免手动输入字符串导致的拼写错误。
from vnpy.event import EVENT_TIMER  # noqa

# 常量的值后面有个.,方便字符串拼接。比如eTick.000725.SZSE
EVENT_TICK = "eTick."
EVENT_TRADE = "eTrade."
EVENT_ORDER = "eOrder."
EVENT_POSITION = "ePosition."
EVENT_ACCOUNT = "eAccount."
EVENT_QUOTE = "eQuote."
EVENT_CONTRACT = "eContract."
EVENT_LOG = "eLog"
