"""
用 akshare 下载历史K线数据，存入 vnpy 本地 SQLite 数据库。
用法：
    python download_data.py              # 默认下载京东方A(000725)近1年日线
    python download_data.py 600519       # 下载贵州茅台
    python download_data.py 000858 300750 000001   # 批量下载
"""
import sys
from datetime import datetime, timedelta

import akshare as ak
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData
from vnpy.trader.database import get_database

# 交易所映射
def get_akshare_symbol(code: str) -> tuple[str, Exchange]:
    """'000725' -> ('sz000725', Exchange.SZSE)"""
    code = code.zfill(6)
    if code.startswith(("6", "9")):
        return f"sh{code}", Exchange.SSE
    else:
        return f"sz{code}", Exchange.SZSE

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
        turnover=float(row.get("amount", 0) or 0),
        open_interest=0,
    )

def download(code: str):
    akshare_sym, exchange = get_akshare_symbol(code)

    # 拉取全部历史
    df = ak.stock_zh_a_daily(symbol=akshare_sym, adjust="qfq")

    # 只取近1年
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    df["date"] = df["date"].astype(str)
    df = df[df["date"] >= one_year_ago]

    # 附加 symbol/exchange 字段
    df["symbol"] = code
    df["exchange"] = exchange

    # 转为 BarData
    bars = [to_bar(row) for _, row in df.iterrows()]

    # 存入数据库
    db = get_database()
    db.save_bar_data(bars)

    print(f"[OK] {code}  {len(bars)} 条日线数据已存入数据库 "
          f"({df['date'].values[0]} ~ {df['date'].values[-1]})")

if __name__ == "__main__":
    codes = sys.argv[1:] if len(sys.argv) > 1 else ["000725"]
    db = get_database()
    for code in codes:
        download(code)
