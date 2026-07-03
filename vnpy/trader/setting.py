# 模块级dict配置

# python 特有的模式：直接用.py文件当配置文件
# 优点： 零配置，直接import即可使用
# 缺点： 全局可变状态，任何模块都可以修改，没有访问控制
"""
Global setting of the trading platform.
"""

from logging import INFO
from tzlocal import get_localzone_name

from .utility import load_json

# 模块全局变量
SETTINGS: dict = {
    # 用.分隔符模拟命名空间
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": INFO,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "",
    "datafeed.username": "",
    "datafeed.password": "",

    "database.timezone": get_localzone_name(),
    "database.name": "sqlite",
    "database.database": "database.db",
    "database.host": "",
    "database.port": 0,
    "database.user": "",
    "database.password": ""
}


# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
# 文件路径：~/.vntrader/vt_setting.json
# 用另一个dict的键值对覆盖当前dict，有冲突时读取文件的值，没冲突时保留默认值。
SETTINGS.update(load_json(SETTING_FILENAME))
