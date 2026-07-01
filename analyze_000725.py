"""
A股技术分析脚本，纯 numpy 计算指标，数据来源 akshare（免费）。

用法：
    python analyze_000725.py                           # 默认分析 京东方A
    python analyze_000725.py 600519                     # 分析贵州茅台（上海）
    python analyze_000725.py 000858                     # 分析五粮液（深圳）
    python analyze_000725.py sz000001                   # 直接传 akshare 格式代码
"""
import sys
from datetime import datetime, timedelta

import akshare as ak
import numpy as np


# ── 指标计算函数 ──
def sma(close: np.ndarray, n: int) -> np.ndarray:
    """简单移动平均"""
    weights = np.ones(n) / n
    return np.convolve(close, weights, mode='valid')


def ema(close: np.ndarray, n: int) -> np.ndarray:
    """指数移动平均"""
    alpha = 2 / (n + 1)
    result = np.zeros_like(close)
    result[0] = close[0]
    for i in range(1, len(close)):
        result[i] = alpha * close[i] + (1 - alpha) * result[i - 1]
    return result


def rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    """RSI 相对强弱指标"""
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.zeros_like(close)
    avg_loss = np.zeros_like(close)
    avg_gain[n] = np.mean(gain[1:n + 1])
    avg_loss[n] = np.mean(loss[1:n + 1])
    for i in range(n + 1, len(close)):
        avg_gain[i] = (avg_gain[i - 1] * (n - 1) + gain[i]) / n
        avg_loss[i] = (avg_loss[i - 1] * (n - 1) + loss[i]) / n
    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    return 100 - 100 / (1 + rs)


def macd(close: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD 指标"""
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    dif = ema_fast - ema_slow
    dea = ema(dif, signal)
    hist = 2 * (dif - dea)
    return dif, dea, hist


def bbands(close: np.ndarray, n: int = 20, k: float = 2):
    """布林带"""
    mid = sma(close, n)
    # pad to same length as close
    mid_full = np.zeros_like(close)
    mid_full[n - 1:] = mid
    # rolling std
    std = np.zeros_like(close)
    for i in range(n - 1, len(close)):
        std[i] = np.std(close[i - n + 1:i + 1], ddof=0)
    upper = mid_full + k * std
    lower = mid_full - k * std
    return upper, mid_full, lower


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> np.ndarray:
    """ATR 平均真实波幅"""
    tr = np.maximum(high - low,
                    np.maximum(np.abs(high - np.roll(close, 1)),
                               np.abs(low - np.roll(close, 1))))
    tr[0] = high[0] - low[0]
    result = np.zeros_like(close)
    result[n] = np.mean(tr[1:n + 1])
    for i in range(n + 1, len(close)):
        result[i] = (result[i - 1] * (n - 1) + tr[i]) / n
    return result


def kdj(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 9, m1: int = 3, m2: int = 3):
    """KDJ 指标"""
    lowest_low = np.zeros_like(close)
    highest_high = np.zeros_like(close)
    for i in range(len(close)):
        start = max(0, i - n + 1)
        lowest_low[i] = np.min(low[start:i + 1])
        highest_high[i] = np.max(high[start:i + 1])

    rsv = np.zeros_like(close)
    denom = highest_high - lowest_low
    mask = denom != 0
    rsv[mask] = (close[mask] - lowest_low[mask]) / denom[mask] * 100

    k = np.zeros_like(close)
    d = np.zeros_like(close)
    j = np.zeros_like(close)
    k[0], d[0] = 50, 50
    for i in range(1, len(close)):
        k[i] = (k[i - 1] * (m1 - 1) + rsv[i]) / m1
        d[i] = (d[i - 1] * (m2 - 1) + k[i]) / m2
        j[i] = 3 * k[i] - 2 * d[i]
    return k, d, j


# ── 1. 解析参数，拉取近1年日K线 ──
STOCK_MAP: dict[str, str] = {
    "000725": ("sz000725", "京东方A"),
    "600519": ("sh600519", "贵州茅台"),
    "000858": ("sz000858", "五粮液"),
    "300750": ("sz300750", "宁德时代"),
    "000001": ("sz000001", "平安银行"),
    "600036": ("sh600036", "招商银行"),
    "601318": ("sh601318", "中国平安"),
}

raw_code: str = sys.argv[1] if len(sys.argv) > 1 else "000725"

# 自动推导 akshare 代码
if raw_code.startswith(("sz", "sh", "bj")):
    akshare_code = raw_code
else:
    code = raw_code.zfill(6)
    if code.startswith(("6", "9")):
        akshare_code = f"sh{code}"
    else:
        akshare_code = f"sz{code}"

stock_name: str = STOCK_MAP.get(raw_code, akshare_code)

print("=" * 60)
print(f"{stock_name} ({akshare_code}) 技术分析报告")
print("=" * 60)

# 使用 akshare 新浪财经接口（数据更新及时，当天盘后可获取）
df = ak.stock_zh_a_daily(symbol=akshare_code, adjust="qfq")

# 取最近1年数据
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
df["date"] = df["date"].astype(str)
df = df[df["date"] >= start_date]

print(f"\n数据区间：{df['date'].values[0]} ~ {df['date'].values[-1]}")
print(f"共获取 {len(df)} 个交易日")

# 提取为 numpy 数组
dates = df["date"].values
opens = df["open"].astype(float).values
highs = df["high"].astype(float).values
lows = df["low"].astype(float).values
closes = df["close"].astype(float).values
volumes = df["volume"].astype(float).values
amounts = df["amount"].astype(float).values

N = len(closes)

# ── 2. 核心分析 ──
latest_close = closes[-1]
latest_date = dates[-1]

# 价格区间
year_high = np.max(highs)
year_low = np.min(lows)

print(f"\n{'─' * 40}")
print(f"【最新行情】日期：{latest_date}")
print(f"收盘价：{latest_close:.2f}")
print(f"近1年最高：{year_high:.2f}  最低：{year_low:.2f}")
print(f"距1年高点：{(latest_close / year_high - 1) * 100:.1f}%")
print(f"距1年低点：{(latest_close / year_low - 1) * 100:.1f}%")

# 均线
ma5_arr = sma(closes, 5)
ma10_arr = sma(closes, 10)
ma20_arr = sma(closes, 20)
ma60_arr = sma(closes, 60)

ma5 = ma5_arr[-1]
ma10 = ma10_arr[-1]
ma20 = ma20_arr[-1]
ma60 = ma60_arr[-1]

print(f"\n{'─' * 40}")
print("【均线系统】")
print(f"MA5:  {ma5:.2f}  {'▲ 站上' if latest_close > ma5 else '▼ 下方'}")
print(f"MA10: {ma10:.2f}  {'▲ 站上' if latest_close > ma10 else '▼ 下方'}")
print(f"MA20: {ma20:.2f}  {'▲ 站上' if latest_close > ma20 else '▼ 下方'}")
print(f"MA60: {ma60:.2f}  {'▲ 站上' if latest_close > ma60 else '▼ 下方'}")

# 均线排列
bullish_alignment = ma5 > ma10 > ma20 > ma60
bearish_alignment = ma5 < ma10 < ma20 < ma60
if bullish_alignment:
    alignment_signal = "多头排列 ✅ — 趋势向上"
elif bearish_alignment:
    alignment_signal = "空头排列 ⚠️  — 趋势向下"
else:
    alignment_signal = "均线交织 — 处于震荡整理"
print(f"均线形态：{alignment_signal}")

# RSI
rsi_arr = rsi(closes, 14)
rsi_6 = rsi(closes, 6)[-1]
rsi_14 = rsi_arr[-1]
rsi_24 = rsi(closes, 24)[-1]

print(f"\n{'─' * 40}")
print("【RSI 相对强弱】")
print(f"RSI(6):  {rsi_6:.1f}", "超买区" if rsi_6 > 80 else ("超卖区" if rsi_6 < 20 else ""))
print(f"RSI(14): {rsi_14:.1f}", "超买区" if rsi_14 > 70 else ("超卖区" if rsi_14 < 30 else ""))
print(f"RSI(24): {rsi_24:.1f}", "超买区" if rsi_24 > 70 else ("超卖区" if rsi_24 < 30 else ""))

# MACD
dif_arr, dea_arr, hist_arr = macd(closes)
macd_dif = dif_arr[-1]
macd_dea = dea_arr[-1]
macd_hist = hist_arr[-1]

print(f"\n{'─' * 40}")
print("【MACD】")
print(f"DIF:   {macd_dif:.4f}")
print(f"DEA:   {macd_dea:.4f}")
print(f"柱值:  {macd_hist:.4f}")

if macd_hist > 0:
    macd_state = "红柱（多方控盘）"
else:
    macd_state = "绿柱（空方控盘）"

if macd_dif > macd_dea:
    macd_state += "，DIF > DEA（金叉区域）"
else:
    macd_state += "，DIF < DEA（死叉区域）"
print(f"状态：{macd_state}")

# 布林带
bb_upper_arr, bb_mid_arr, bb_lower_arr = bbands(closes, 20, 2)
bb_upper = bb_upper_arr[-1]
bb_mid = bb_mid_arr[-1]
bb_lower = bb_lower_arr[-1]

bb_width = (bb_upper - bb_lower) / bb_mid * 100 if bb_mid != 0 else 0
denom = bb_upper - bb_lower
bb_position = (latest_close - bb_lower) / denom if denom != 0 else 0.5

print(f"\n{'─' * 40}")
print("【布林带 (20,2)】")
print(f"上轨：{bb_upper:.2f}")
print(f"中轨：{bb_mid:.2f}")
print(f"下轨：{bb_lower:.2f}")
print(f"带宽：{bb_width:.1f}%  (越窄越可能变盘)")
print(f"价格位置：{bb_position:.0%}  "
      f"({'靠近上轨/强势' if bb_position > 0.8 else ('靠近下轨/弱势' if bb_position < 0.2 else '中轨附近')})")

# ATR
atr_arr = atr(highs, lows, closes, 14)
atr_val = atr_arr[-1]
atr_pct = atr_val / latest_close * 100

print(f"\n{'─' * 40}")
print("【ATR 波动率】")
print(f"ATR(14)：{atr_val:.4f}")
print(f"ATR%:    {atr_pct:.2f}%  (日均波动幅度)")

# KDJ
k_arr, d_arr, j_arr = kdj(highs, lows, closes)
k = k_arr[-1]
d = d_arr[-1]
j = j_arr[-1]

print(f"\n{'─' * 40}")
print("【KDJ (9,3,3)】")
print(f"K: {k:.2f}")
print(f"D: {d:.2f}")
print(f"J: {j:.2f}")
kdj_signal = "超买区" if j > 100 else ("超卖区" if j < 0 else "中性")
print(f"状态：{kdj_signal}")

# 成交量
if N >= 20:
    avg_vol_20 = np.mean(volumes[-20:])
    latest_vol = volumes[-1]
    vol_ratio = latest_vol / avg_vol_20 if avg_vol_20 != 0 else 1
else:
    avg_vol_20 = np.mean(volumes)
    latest_vol = volumes[-1]
    vol_ratio = 1

print(f"\n{'─' * 40}")
print("【成交量】")
print(f"最新成交量：{latest_vol:.0f}")
print(f"20日均量：  {avg_vol_20:.0f}")
print(f"量比：      {vol_ratio:.2f}",
      "(放量)" if vol_ratio > 1.5 else ("(缩量)" if vol_ratio < 0.5 else "(正常)"))

# ── 3. 综合评分 ──
print(f"\n{'=' * 60}")
print("【综合评分】(仅供参考)")
print(f"{'=' * 60}")

score = 0
signals = []

# 趋势
if bullish_alignment:
    score += 2
    signals.append("✅ 均线多头排列（+2）")
elif bearish_alignment:
    score -= 2
    signals.append("⚠️  均线空头排列（-2）")
else:
    signals.append("● 均线交织（0）")

# 价格 vs 均线
above_count = sum([latest_close > ma5, latest_close > ma10, latest_close > ma20, latest_close > ma60])
if above_count >= 3:
    score += 1
    signals.append(f"✅ 价格站上{above_count}条均线（+1）")
elif above_count <= 1:
    score -= 1
    signals.append(f"⚠️  价格跌破多条均线（-1）")

# RSI
if 30 < rsi_14 < 70:
    signals.append("● RSI 中性区（0）")
elif rsi_14 > 70:
    score -= 1
    signals.append("⚠️  RSI 超买（-1）")
elif rsi_14 < 30:
    score += 1
    signals.append("✅ RSI 超卖/可能反弹（+1）")

# MACD
if macd_dif > macd_dea and macd_hist > 0:
    score += 1
    signals.append("✅ MACD 金叉+红柱（+1）")
elif macd_dif < macd_dea and macd_hist < 0:
    score -= 1
    signals.append("⚠️  MACD 死叉+绿柱（-1）")

# 布林带
if bb_position < 0.2:
    score += 1
    signals.append("✅ 靠近布林下轨/超卖（+1）")
elif bb_position > 0.8:
    score -= 1
    signals.append("⚠️  靠近布林上轨/超买（-1）")

# KDJ
if j < 0:
    score += 1
    signals.append("✅ KDJ 超卖区（+1）")
elif j > 100:
    score -= 1
    signals.append("⚠️  KDJ 超买区（-1）")

print("\n信号明细：")
for s in signals:
    print(f"  {s}")

print(f"\n综合得分：{score} 分")
if score >= 3:
    conclusion = "偏多信号居多，趋势偏强，可关注做多机会"
elif score <= -3:
    conclusion = "偏空信号居多，趋势偏弱，注意风险"
else:
    conclusion = "信号中性偏震荡，方向不明确，建议观望或轻仓"

print(f"结论：{conclusion}")
print(f"\n⚠️  免责声明：以上仅基于技术指标的计算结果，")
print("    不构成任何投资建议。股市有风险，投资需谨慎。")
