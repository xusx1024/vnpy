# 模块文档字符串（docstring） 相当于java的 /** */，Python/Kotlin 使用三引号包裹文档注释
# Python没有规定docstring必须在文件最开头， 但通常建议将其放在文件开头。
"""
用 akshare 下载历史K线数据，存入 vnpy 本地 SQLite 数据库。
用法：
    python download_data.py              # 默认下载京东方A(000725)近1年日线
    python download_data.py 600519       # 下载贵州茅台
    python download_data.py 000858 300750 000001   # 批量下载
"""

# Python PEP8规范要求：标准库，第三方库，本地库，导入之间用空行分隔

# 相当于java中的system
import sys
# 静态导入
from datetime import datetime, timedelta

# 别名
import akshare as ak
from vnpy.trader.constant import Exchange, Interval
# vnpy定义的dataclass，代表一根K线数据
from vnpy.trader.object import BarData
from vnpy.trader.database import get_database

# 交易所映射
# def 定义一个函数，如果函数名前缀有_，表示私有函数
# code:str 是类型注解，告诉IDE和阅读代码的人，code是一个字符串类型。运行时不强制检查。
# -> tuple[str, Exchange]: 返回（str, Exchange）元祖，Java中的Pair类型，固定两个元素。
def get_akshare_symbol(code: str) -> tuple[str, Exchange]:
    """'000725' -> ('sz000725', Exchange.SZSE)"""
    # zfill(6) 方法将字符串左侧填充0，使其长度为6位
    code = code.zfill(6)
    # 如果以6或9开头
    if code.startswith(("6", "9")):
        # 等价于 return "sh" + code, Exchange.SSE
        return f"sh{code}", Exchange.SSE
    else:
        return f"sz{code}", Exchange.SZSE

# K线数据转换函数
# row是pandas Series，类似于java中的Map<String, Object>，用row["date"]取值
def to_bar(row) -> BarData:
    return BarData(
        symbol=row["symbol"],
        exchange=row["exchange"],
        datetime=datetime.strptime(row["date"], "%Y-%m-%d"),
        interval=Interval.DAILY,
        gateway_name="akshare",
        open_price=float(row["open"]),
        high_price=float(row["high"]),
        low_price=float(row["low"]),
        close_price=float(row["close"]),
        volume=float(row["volume"]),
        # amount列不存在，返回0， amount的值是如果取出来是None/空字符串,返回0
        # 这是双重兜底，列不存在或取出的值为falsy，都返回0
        # 注意：java的or，and返回boolean值，Python的or，and返回实际值
        turnover=float(row.get("amount", 0) or 0),
        open_interest=0,
    )

def download(code: str):

    # get_akshare_symbol是前面我们定义的函数，返回一个元祖，akshare_sym是akshare的symbol，exchange是交易所
    # Java写法示例：
    # var pair = getAkshareSymbol(code);
    # String akshareSym = pair.getLeft();
    # Exchange exchange = pair.getRight();
    akshare_sym, exchange = get_akshare_symbol(code)

    # 拉取全部历史
    # 返回pandas DataFrame，二维表格，类似于Java的List<Map<String, Object>>
    # qfq = 前复权
    df = ak.stock_zh_a_daily(symbol=akshare_sym, adjust="qfq")

    # 只取近1年
    # timedelta 时间偏移量，Python的datetime可以直接做加减
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    # 将date列转为字符串类型，方便比较
    df["date"] = df["date"].astype(str)

    # 这是pandas的过滤语法，类似于Java的stream().filter()，返回一个新的DataFrame
    # 这是pandas的布尔索引，相当于SQL： SELECT * FROM DF WHERE date >= one_year_ago
    # df["date"] >= one_year_ago 生成一个true/false的布尔列，再把它当做索引传给df[]，只保留True的行
    df = df[df["date"] >= one_year_ago]

    # 附加 symbol/exchange 字段
    # 给DataFrame新增两列，所有行赋值都相同，这是pandas的广播机制，单条指令覆盖整列，标量赋值到所有行（底层C向量化，无需for循环） 
    # 本来DataFrame是二维表格，类似于Java的List<Map<String, Object>>，现在新增两列，每个Map新增两个key-value
    df["symbol"] = code
    df["exchange"] = exchange

    # 转为 BarData
    # Python最核心的语法糖之一：列表推导式，类似于Java的stream().map().collect(Collectors.toList())
    # df.iterrows()，迭代器，遍历DataFrame，每次产出一个元祖(index, row)，row是一个Series，类似于Java的Map<String, Object>
    # _: 约定俗成的写法，表示这个变量不会被使用，类似于Java的匿名变量
    # for _, row in df.iterrows()，遍历DataFrame的每一行，row是一个Series，类似于Java的Map<String, Object>
    # to_bar(row) 是我们前面定义的函数，把row转换为BarData
    # 最终生成一个列表，里面是BarData对象，类似于Java的List<BarData>
    # 注意：Python的列表推导式返回一个新的列表，原来的df没有被修改
    # iterrows() 是逐行遍历，性能不如向量化操作（因为每行都创建一个 Python 对象），但数据量小时（几百行）完全够用。数据量大时可以用 df.apply(to_bar, axis=1)。
    bars = [to_bar(row) for _, row in df.iterrows()]

    # 存入数据库
    # 这是工厂函数，默认SQLite，也可以通过vnpy.trader.database.init_database()初始化为MySQL/PostgreSQL
    db = get_database()

    # 批量存入数据库，db.save_bar_data()是vnpy.trader.database.Database类的方法，接受一个列表，里面是BarData对象
    db.save_bar_data(bars)

    print(f"[OK] {code}  {len(bars)} 条日线数据已存入数据库 "
          f"({df['date'].values[0]} ~ {df['date'].values[-1]})")

# Python的入口守卫
# 当文件被直接运行时，__name__ == "__main__" 为True，执行下面的代码
# 当文件被其他文件导入时，__name__ == "download_data" 为True，不执行下面的代码
# java中有public static void main(String[] args){}，Python没有main函数的概念，任何文件都可以是主程序
if __name__ == "__main__":
    # 三目表达式，见Kotlin的写法
    codes = sys.argv[1:] if len(sys.argv) > 1 else ["000725"]
    for code in codes:
        download(code)
