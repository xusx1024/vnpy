# vnpy 源码系统学习计划

> **适用人群**：Android 开发者，精通 Java/Kotlin，Python 新手
> **预估总时长**：8 天 × 1.5h ≈ 12 小时（不含选学模块）
> **前置要求**：已完成 `download_data.py` 的逐行学习

---

## 目录

- [学习地图](#学习地图)
- [Phase 0: Python 语法热身](#phase-0-python-语法热身)
- [Phase 1: 事件引擎](#phase-1-事件引擎)
- [Phase 2: 交易领域模型](#phase-2-交易领域模型)
- [Phase 3: 主引擎](#phase-3-主引擎)
- [Phase 4: Alpha AI 流水线（选学）](#phase-4-alpha-ai-流水线选学)
- [Phase 5: 分布式 + 图表（选学）](#phase-5-分布式--图表选学)
- [毕业项目](#毕业项目)
- [进度追踪](#进度追踪)

---

## 学习地图

```
                        ┌──────────────────────────┐
              Phase 0   │  Python 语法热身 (2h)      │
                        │  dataclass / Enum / ABC    │
                        │  = Java record  / enum /   │
                        │    abstract class          │
                        └──────────┬───────────────┘
                                   ↓
              Phase 1   │  事件引擎 (1.5h) ⭐ 必学    │
                        │  event/engine.py            │
                        │  = EventBus / LiveData      │
                        └──────────┬───────────────┘
                                   ↓
              Phase 2   │  交易领域模型 (2h)           │
                        │  constant → object →        │
                        │  gateway → converter        │
                        │  = DTO/VO 层 + DAO 接口     │
                        └──────────┬───────────────┘
                                   ↓
              Phase 3   │  主引擎 (3h) ⭐ 必学         │
                        │  engine.py                   │
                        │  = ApplicationContext       │
                        │  + EventBus Consumer        │
                        └──────────┬───────────────┘
                                   ↓
              Phase 4   │  Alpha AI 流水线 (3h) 选学   │
                        │  dataset → model → strategy  │
                        │  → backtesting               │
                        └──────────┬───────────────┘
                                   ↓
              Phase 5   │  RPC + Chart (1.5h) 选学     │
                        │  ZeroMQ 分布式 + PyQtGraph   │
                        └──────────────────────────────┘
```

---

## Phase 0: Python 语法热身

> **目标**：用 vnpy 自己的简单文件当教材，一次性搞懂 Python 和 Java 的核心语法差异

### 0.1 阅读清单

| # | 文件 | 行数 | 重点 | Java 类比 |
|---|------|------|------|-----------|
| 0.1 | `vnpy/trader/constant.py` | 160 | `Enum`、`IntEnum` | Java `enum`，但 Python 的 Enum 可以直接 `.value` |
| 0.2 | `vnpy/trader/object.py` | 427 | `@dataclass`、`Optional[T]`、`__post_init__` | Java `record`，但 dataclass 有构造后钩子 |
| 0.3 | `vnpy/trader/setting.py` | 43 | 全局配置模式 | Java 的 `.properties` / `application.yml` |
| 0.4 | `vnpy/trader/event.py` | 14 | `Event` 数据结构 | Android `EventBus` 的 Event 包装类 |

### 0.2 练习
constant
#### 练习 0-A：用 @dataclass 定义数据类

```python
# 需求：定义一个 Trade（成交）类，包含以下字段：
#   - trade_id: str      成交编号
#   - symbol: str        合约代码
#   - price: float       成交价
#   - volume: float      成交量
#   - direction: 多/空   方向
#   - trade_time: datetime  成交时间
#
# 要求：
#   1. 用 @dataclass 定义
#   2. 用 __post_init__ 校验 trade_id 不能为空
#   3. 写一个方法 to_dict() 返回 dict
#
# 完成后，运行以下代码验证：
#   t = Trade(trade_id="T001", symbol="000725", price=5.28, volume=100, direction=Direction.LONG, trade_time=datetime.now())
#   print(t)
#   print(t.to_dict())
#
# 你的代码写在这里 ↓
```

#### 练习 0-B：枚举定义与遍历

```python
# 需求：定义 OrderStatus 枚举（已提交/已成交/已撤销/被拒）
#
# 要求：
#   1. 继承 IntEnum
#   2. 遍历所有枚举值，打印 name 和 value
#   3. 写一个 @classmethod parse(value: int) -> OrderStatus
#
# 你的代码写在这里 ↓
```

#### 练习 0-C：类型注解实战

```python
# 下面这段代码有 3 个类型注解错误，找出并修正

from typing import Optional
from datetime import datetime

def find_order(order_id: str) -> Optional[dict]:   # ①
    """查找订单"""
    pass

def calculate_pnl(position: float, price: str) -> float:  # ② ③
    return position * price
```

### 0.3 考查

**Q0-1**：Java 的 `enum` 和 Python 的 `Enum` 最大的两个区别是什么？

**Q0-2**：`@dataclass` 和 Java `record` 有什么本质不同？（提示：可变性、继承）

**Q0-3**：`Optional[str]` 在运行时真的会阻止 `None` 赋值吗？它跟 Kotlin 的 `String?` 有何区别？

**Q0-4**：阅读 `vnpy/trader/event.py`，画一张内存图：`Event` 对象在内存中长什么样？

<details>
<summary>参考答案（做完再看）</summary>

**Q0-1**：① Python 的 Enum 值可以是任意类型，Java 的只能是指定的字段；② Python 的 Enum 实例本身就是单例，可以直接比较 `Direction.LONG == Direction.LONG`，但 Java 通常用 `==` 比较引用。

**Q0-2**：① dataclass 默认可变（需要 `frozen=True` 才不可变），record 强制不可变；② dataclass 可以继承，record 不能 extends 其他类。

**Q0-3**：不会。`Optional[str]` 只是类型提示，运行时完全不检查。Kotlin 的 `String?` 是编译时强制的，运行时也会在赋值时检查（平台类型除外）。

**Q0-4**：`Event` 对象只有两个字段：`type: str` + `data: Any`。`type` 是 `"eTick"` 这样的字符串键，`data` 可以是任何类型，相当于 `EventBus.post(Object event)` 里的 event。

</details>

---

## Phase 1: 事件引擎

> **目标**：理解 vnpy 的"心跳"机制 — 所有组件通信的基础设施

### 1.1 阅读清单

| # | 文件 | 行数 | 重点 |
|---|------|------|------|
| 1.1 | `vnpy/event/engine.py` | 145 | `EventEngine` 类 → `Queue` + `Thread` + `Handler` |

### 1.2 阅读路线（按行号）

| 行号范围 | 内容 | 对照点 |
|----------|------|--------|
| 1-15 | `import` + `EVENT_TIMER` 常量 | `EVENT_TIMER = "eTimer"` — 用字符串当事件 key |
| 16-20 | `HandlerType` 类型别名 | `Callable[[Event], None]` = Java `Consumer<Event>` |
| 22-73 | `EventEngine` 类体 | — |
| 24-39 | `__init__` | `Queue()` = `BlockingQueue`；`Thread(target=..., daemon=True)` = `thread.setDaemon(true)` |
| 50-58 | `_run()` | 核心循环：`while not stop: event = queue.get(); handlers(event)` |
| 60-68 | `_run_timer()` | Timer 线程：`sleep(interval)` → `put(Event(EVENT_TIMER))` |
| 70-73 | `start()` / `stop()` | 启动/停止两个线程 |
| 75-106 | `register()` / `unregister()` / `put()` | `_handler_dict[type]` = `list[Handler]` |
| 108-145 | `register_general()` / `start()` 完整版 | 通用处理器：所有事件都触发 |

### 1.3 练习

#### 练习 1-A：手写一个微型 EventBus

```python
# 需求：实现一个简化版 EventBus，支持：
#   1. register(event_type: str, handler: callable) → 注册处理器
#   2. post(event_type: str, data: Any) → 派发事件
#   3. 单线程版本即可（不用 Queue + Thread）
#
# 要求：
#   - 同一个 event_type 可以有多个 handler
#   - post 时按注册顺序调用所有 handler
#
# 你的代码写在这里 ↓
```

#### 练习 1-B：给 EventEngine 加新功能

```
需求：给 EventEngine 加一个 `dispatch_mode` 属性：
  - "sync" 模式：直接在当前线程调用 handler（不经过 Queue）
  - "async" 模式：现有行为（经 Queue → 后台线程消费）

思考：
  1. 什么场景适合 sync 模式？（提示：回测）
  2. sync 模式下还需要 Queue 吗？
  3. 单线程 sync 模式下，handler 抛异常怎么办？
```

### 1.4 考查

**Q1-1**：`EventEngine` 为什么用两个线程（dispatcher + timer），而不是一个？

**Q1-2**：如果 handler 执行时间超过 timer interval（如 interval=1s 但 handler 耗时 3s），会发生什么？

**Q1-3**：`Queue.get(timeout=1)` 的 timeout 是做什么用的？去掉会怎样？

**Q1-4**：画出 EventEngine 的线程模型图：主线程、dispatcher 线程、timer 线程之间的关系。

<details>
<summary>参考答案</summary>

**Q1-1**：timer 线程负责按固定间隔向 Queue 推送定时事件，dispatcher 线程负责消费 Queue。如果合并为一个线程，`sleep(interval)` 期间无法处理事件，事件处理延迟会累积。

**Q1-2**：事件会在 Queue 中堆积。dispatcher 处理完当前事件后立即取下一个。如果处理速度持续落后生产速度，Queue 无限增长 → 内存溢出。

**Q1-3**：`timeout=1` 让 `get()` 每秒返回一次（可能拿不到东西），目的是检查 `self._active` 标志。去掉会导致 `stop()` 无法让被阻塞的 `get()` 返回，线程永远卡住。

</details>

---

## Phase 2: 交易领域模型

> **目标**：理解金融交易的核心数据结构和接口抽象

### 2.1 阅读清单

| # | 文件 | 行数 | 重点 | Java 类比 |
|---|------|------|------|-----------|
| 2.1 | `vnpy/trader/constant.py` | 160 | `Direction`/`Offset`/`Exchange` 等枚举 | `enum` + 领域常量 |
| 2.2 | `vnpy/trader/object.py` | 427 | `TickData`/`BarData`/`OrderData`/`TradeData`/`PositionData` | DTO/VO 层 |
| 2.3 | `vnpy/trader/gateway.py` | 272 | `BaseGateway` ABC | `interface` / `abstract class` |
| 2.4 | `vnpy/trader/converter.py` | 402 | `OffsetConverter` 仓位计算 | 业务逻辑 Service |
| 2.5 | `vnpy/trader/utility.py` | 1281 | 工具函数集 | `StringUtils` / `FileUtils` |

### 2.2 阅读路线

#### 2.1 `constant.py`（30min）

| 行号 | 内容 | 注意 |
|------|------|------|
| 1-18 | `Direction`(IntEnum) | `LONG=1, SHORT=2`，继承 int → `Direction.LONG == 1` 为 True |
| 19-28 | `Offset`(Enum) | `OPEN`/`CLOSE`/`CLOSETODAY`/`CLOSEYESTERDAY` — 理解这四个词 |
| 29-35 | `Status`(Enum) | 订单状态机：`SUBMITTING → NOTTRADED → PARTTRADED → ALLTRADED` |
| 36-41 | `Product`(Enum) | `EQUITY`/`FUTURES`/`OPTION`/`INDEX` |
| 42-48 | `OrderType`(Enum) | `LIMIT`（限价）/ `MARKET`（市价）/ `STOP` |
| 49-55 | `Exchange`(Enum) | 交易所枚举 |
| 56-69 | `Currency`(Enum) | 币种 |
| 70-84 | `Interval`(Enum) | K线周期：`MINUTE`/`HOUR`/`DAILY`/`WEEKLY` |

#### 2.2 `object.py`（45min）

| 行号 | 内容 | Python 知识点 |
|------|------|--------------|
| 1-30 | `BaseData` dataclass + `vt_symbol` | `__post_init__`：构造后自动拆分 `"IF2406.CFFEX"` |
| 31-80 | `TickData` | 逐笔行情：最新价/买一价/卖一价/成交量/持仓量 |
| 81-130 | `BarData` | K线：开/高/低/收 + 成交量/成交额 |
| 131-300 | `OrderData` + `TradeData` + `PositionData` + `AccountData` | 订单/成交/持仓/账户 |
| 300-400 | `SubscribeRequest` + `OrderRequest` + `CancelRequest` + `HistoryRequest` | 请求 DTO |

#### 2.3 `gateway.py`（30min）

| 行号 | 内容 |
|------|------|
| 1-34 | `BaseGateway`(ABC) 抽象方法定义 |
| 35-80 | `on_tick()` / `on_order()` / `on_trade()` — 回调钩子 |
| 81-200 | `connect()` / `subscribe()` / `send_order()` — 对外接口 |
| 200-272 | 辅助方法：`get_default_setting()` / `get_trading_hours()` |

#### 2.4 `converter.py`（45min）

> 这是整个 Phase 2 最复杂、也是业务含金量最高的文件。
> 核心问题：中国期货区分**今仓**（今天开的）和**昨仓**（昨天及以前开的），
> 平仓时要指定平今还是平昨，平今免手续费。`OffsetConverter` 管理这个逻辑。

### 2.3 练习

#### 练习 2-A：数据流追踪

```
从 "订单请求" 到 "最终持仓更新" 走一遍数据流：

OrderRequest → Gateway.send_order() → 交易所 → Gateway.on_order(OrderData)
→ OmsEngine.process_order() → 缓存更新 → EVENT_ORDER
→ OffsetConverter.update_order() → 仓位计算 → EVENT_POSITION
```

用伪代码/时序图画出上述流程。

#### 练习 2-B：读懂 converter.py 的核心方法

阅读 `OffsetConverter.update_trade()`，回答：
1. 为什么成交方向为 LONG 时要调用 `_open_long()`，SHORT 时调用 `_close_short()`？
2. `_close_long_today()` 和 `_close_long_yesterday()` 有什么区别？
3. 什么是"锁仓"？

#### 练习 2-C：实现一个新的 Gateway 骨架

```python
# 需求：实现一个 "MockGateway"，模拟一个交易所连接
#   1. 继承 BaseGateway
#   2. 实现 connect() — 打印 "connected" 并设置 self.status
#   3. 实现 subscribe(req: SubscribeRequest) — 用定时器每秒生成一条随机 Tick
#   4. 实现 send_order(req: OrderRequest) — 随机返回成交/不成交
#
# 你的代码写在这里 ↓
```

### 2.4 考查

**Q2-1**：`BaseData` 的 `__post_init__` 中 `extract_vt_symbol()` 做了什么？为什么不在 `__init__` 里做？

**Q2-2**：`TickData` 和 `BarData` 的差别是什么？什么场景用 Tick，什么场景用 Bar？

**Q2-3**：为什么 `Offset.OPEN` 和 `Offset.CLOSE` 是独立的枚举值，而不是用 `Direction` + 一个布尔字段？

**Q2-4**：如果有 10 个不同的券商网关，`BaseGateway` 的抽象方法设计是否合理？你会怎么改进？

<details>
<summary>参考答案</summary>

**Q2-1**：`extract_vt_symbol()` 把 `"IF2406.CFFEX"` 拆成 `symbol="IF2406"` + `exchange=CFFEX`。不在 `__init__` 做是因为 dataclass 的 `__init__` 是自动生成的——你声明 `symbol` 字段，生成器就自动在 `__init__` 里接收它。`__post_init__` 在自动 `__init__` 执行后调用，适合做"字段间的派生逻辑"。

**Q2-2**：Tick 是每笔成交/每次盘口变化，频率极高（500ms → 毫秒级）；Bar 是聚合后的 OHLCV K线（1分钟/5分钟/日线）。策略通常用 Bar 做决策，Tick 用于高频/精确回放。

**Q2-3**：因为"买入开仓"和"买入平仓"是完全不同的意图——前者建立多头，后者了结空头。Direction × Offset 构成 4 种组合：`LONG+OPEN`（买开）、`SHORT+OPEN`（卖开）、`LONG+CLOSE`（买平）、`SHORT+CLOSE`（卖平）。用枚举表达比布尔 + 方向更清晰、更不容易出错。

</details>

---

## Phase 3: 主引擎

> **目标**：理解框架的 IoC 容器 — 如何把事件引擎、网关、策略串成一条流水线

### 3.1 阅读清单

| # | 文件 | 行数 | 重点 |
|---|------|------|------|
| 3.1 | `vnpy/trader/engine.py` | 838 | `MainEngine` + `OmsEngine` + `LogEngine` + `EmailEngine` |

### 3.2 阅读路线

| 行号范围 | 内容 | Java 类比 |
|----------|------|-----------|
| 1-80 | imports + 基础初始化函数 | — |
| 81-150 | `MainEngine.__init__()` | Spring `ApplicationContext` 初始化 |
| 150-250 | `MainEngine.add_gateway()` / `get_gateway()` | SPI / ServiceLoader |
| 250-350 | `MainEngine.add_app()` / `init_engines()` | Plugin 注册 |
| 350-450 | `OmsEngine.__init__()` + 缓存初始化 | Repository / DAO 层（内存版） |
| 450-600 | `OmsEngine.process_tick_event()` + `process_order_event()` + `process_trade_event()` | Event Consumer |
| 600-700 | `OmsEngine` 的查询接口 | `findByXxx()` |
| 700-838 | `LogEngine` + `EmailEngine` | 辅助基础设施 |

### 3.3 练习

#### 练习 3-A：画出 MainEngine 的启动时序

```
从 MainEngine() 构造 → add_gateway() → gateway.connect()
→ 第一个 Tick 到达 → OmsEngine.process_tick()
→ 缓存更新 → EVENT_TICK → 策略收到通知

画出每一步的调用栈。
```

#### 练习 3-B：OmsEngine 的缓存设计分析

OmsEngine 维护了这些缓存（dict）：
```
ticks:      Dict[str, TickData]        # key = vt_symbol
orders:     Dict[str, OrderData]       # key = vt_orderid
trades:     Dict[str, TradeData]       # key = vt_tradeid
positions:  Dict[str, PositionData]    # key = vt_positionid
accounts:   Dict[str, AccountData]     # key = vt_accountid
contracts:  Dict[str, ContractData]    # key = vt_symbol
quotes:     Dict[str, QuoteData]       # key = vt_quoteid
```

**问题**：
1. 为什么用内存 dict 而不是数据库？
2. 如果进程崩溃重启，这些数据怎么恢复？
3. 如果要引入 Redis 做分布式缓存，你会改哪些地方？

#### 练习 3-C：实现一个简易策略

```python
# 需求：利用 vnpy 的 MainEngine + OmsEngine，实现一个"双均线"策略
#
# 伪代码：
#   当 5日均线上穿 20日均线 → 买入 100 股
#   当 5日均线下穿 20日均线 → 卖出 100 股
#
# 要求：
#   1. 注册 EVENT_BAR handler
#   2. 在 handler 中计算均线、发信号
#   3. 写清楚哪些是 vnpy 已有的、哪些是你新增的
#
# 你的代码写在这里 ↓
```

### 3.4 考查

**Q3-1**：`MainEngine` 为什么要把 `get_tick()` / `get_order()` 等方法定义为实例方法，而不是让策略直接访问 `OmsEngine` 的缓存？

**Q3-2**：`MainEngine.get_gateway()` 内部用 `__import__()` 动态加载。这和 Java 的 `Class.forName().newInstance()` 有什么区别？

**Q3-3**：`OmsEngine` 的 `process_trade_event()` 里，更新 position 时为什么要调用 `OffsetConverter`？不能直接 `position.volume += trade.volume` 吗？

**Q3-4**：如果同时连接了 CTP 和 IB 两个网关，同一个 `vt_symbol` 的 Tick 会怎么处理？

<details>
<summary>参考答案</summary>

**Q3-1**：① 封装——策略不应该知道 OmsEngine 的存在；② 未来 OmsEngine 可能改成远程调用（RPC），策略不需要改代码；③ MainEngine 可以做权限控制/日志/拦截。

**Q3-2**：Python 的 `__import__()` 返回模块对象，然后 `getattr(module, class_name)` 获取类，最后 `obj()` 实例化。Java 的 `Class.forName()` 直接返回 `Class<?>`。Python 多了一层"模块"概念——类活在模块（`.py` 文件）里。

**Q3-3**：不行。中国期货区分"今仓"和"昨仓"——同一个 `vt_symbol` 的 position 可能包含不同日期的仓位，平仓时要指定平哪个。直接 `volume +=` 会丢失这个信息。`OffsetConverter` 精确追踪每笔开仓的日期和方向。

**Q3-4**：OmsEngine 按 `gateway_name` 区分——`vt_symbol` 相同但 gateway 不同的 Tick 会分别存储。position 也会按 gateway 独立计算。

</details>

---

## Phase 4: Alpha AI 流水线（选学）

> **前置**：对量化因子 + 机器学习有基本了解
> **目标**：理解"因子 → 模型 → 策略 → 回测"的流水线

### 4.1 阅读清单

| # | 文件 | 行数 | 重点 |
|---|------|------|------|
| 4.1 | `vnpy/alpha/dataset/template.py` | 305 | `AlphaDataset` + 因子表达式引擎 |
| 4.2 | `vnpy/alpha/dataset/datasets/alpha_158.py` | 130 | 158 个标准因子 |
| 4.3 | `vnpy/alpha/dataset/cs_function.py` | 64 | 截面算子：`cs_rank()`、`cs_zscore()` |
| 4.4 | `vnpy/alpha/dataset/ts_function.py` | 329 | 时序算子：`ts_delay()`、`ts_corr()` |
| 4.5 | `vnpy/alpha/model/template.py` | 30 | `AlphaModel` ABC：`fit()` + `predict()` |
| 4.6 | `vnpy/alpha/model/models/lgb_model.py` | 170 | LightGBM 实现 |
| 4.7 | `vnpy/alpha/strategy/template.py` | 205 | `AlphaStrategy` 模板 |
| 4.8 | `vnpy/alpha/strategy/backtesting.py` | 944 | 回测引擎 |
| 4.9 | `vnpy/alpha/lab.py` | 480 | `AlphaLab` 总控 |

### 4.2 练习

#### 练习 4-A：理解因子表达式

阅读 `template.py` 中 `calculate_by_expression()` 方法，回答：
1. `"cs_rank(close)"` 这个表达式经历了哪些步骤才变成一列数值？
2. `cs_*` 和 `ts_*` 函数的区别是什么？
3. 表达式引擎使用了什么设计模式？（提示：AST 解析）

#### 练习 4-B：阅读一个完整策略

阅读 `vnpy/alpha/strategy/strategies/equity_demo_strategy.py`，画出信号流：
```
因子数据 → 模型预测 → 信号生成 → 目标权重 → 调仓 → 绩效统计
```

### 4.3 考查

**Q4-1**：`LassoModel`、`LgbModel`、`MLPModel` 都实现了 `AlphaModel`。这个设计的 Java 等价是什么？

**Q4-2**：`BacktestingEngine` 的 `run()` 方法中，逐 bar 回测的逻辑是怎样的？

**Q4-3**：为什么因子表达式不用 Python 的 `eval()` 而自己实现了解析器？

---

## Phase 5: 分布式 + 图表（选学）

> **目标**：理解 RPC 远程调用和图表绘制

### 5.1 阅读清单

| # | 文件 | 行数 | 重点 |
|---|------|------|------|
| 5.1 | `vnpy/rpc/common.py` | 10 | RPC 常量定义 |
| 5.2 | `vnpy/rpc/server.py` | 140 | ZeroMQ REQ/REP + PUB/SUB |
| 5.3 | `vnpy/rpc/client.py` | 169 | RPC 客户端 |
| 5.4 | `vnpy/chart/widget.py` | 556 | PyQtGraph 图表控件 |
| 5.5 | `vnpy/chart/item.py` | 333 | 图表元素（K线、成交量、指标线） |

### 5.2 练习

#### 练习 5-A：搭建 RPC 环境

```
启动 server → 启动 client → 通过 RPC 调用 get_tick("000725.SZSE")
观察返回的数据结构。
```

#### 练习 5-B：RPC 的 PUB/SUB 模式

`server.py` 中有两种 socket 模式：REQ/REP（请求-响应）和 PUB/SUB（发布-订阅）。

1. 为什么 Tick 数据用 PUB/SUB 而不是 REQ/REP？
2. PUB/SUB 的"丢消息"问题怎么解决？

---

## 毕业项目

### 项目：从零搭建一个交易系统

```
┌─────────────────────────────────────────────────────────┐
│ 需求：用 vnpy 框架，搭建一个完整的股票交易系统            │
│                                                         │
│ 要求：                                                   │
│  1. 接入 akshare 数据源（你学过的 download_data.py）     │
│  2. 实现 EventEngine 驱动的主循环                        │
│  3. 定义 TickData/BarData/OrderData 等数据对象           │
│  4. 实现 OmsEngine 的仓位管理                            │
│  5. 写一个简易双均线策略（5日/20日）                      │
│  6. 用 download_data.py 下载的本地数据做回测              │
│  7. 输出回测报告（总收益率、最大回撤、夏普比率）           │
│                                                         │
│ 提示：不需要从零写——复用 vnpy 的核心模块，              │
│       只是把它们"拼装"起来。                             │
│                                                         │
│ 预估代码量：200-300 行                                    │
└─────────────────────────────────────────────────────────┘
```

### 毕业项目检查清单

- [ ] EventEngine 能正常启动/停止
- [ ] 数据源能产生 Tick/Bar 并推入队列
- [ ] OmsEngine 能正确更新订单、成交、持仓
- [ ] 双均线策略能发出买卖信号
- [ ] 回测结果与手动计算的一致
- [ ] 代码有类型注解
- [ ] 代码有 docstring

---

## 进度追踪

| 阶段 | 状态 | 完成日期 | 笔记/问题 |
|------|------|---------|----------|
| Phase 0: 语法热身 | ✅ | | |
| ├─ constant.py | ✅ | | |
| ├─ object.py | ✅ | | |
| ├─ setting.py | ✅ | | |
| └─ event.py | ✅ | | |
| Phase 1: 事件引擎 | ✅ | | |
| ├─ event/engine.py | ✅ | | |
| ├─ 练习 1-A (手写EventBus) | ✅ | | |
| └─ 练习 1-B (dispatch_mode) | ✅ | | |
| Phase 2: 领域模型 | 🔄 | | |
| ├─ gateway.py | ✅ | | |
| ├─ converter.py | ✅ | | |
| ├─ utility.py - load_json链 | ☐ | | ← 下次继续 |
| ├─ utility.py - BarGenerator | ☐ | | ← 下次继续 |
| ├─ utility.py - ArrayManager | ☐ | | ← 下次继续 |
| ├─ 练习 2-A (数据流追踪) | ☐ | | |
| ├─ 练习 2-B (converter核心) | ☐ | | |
| └─ 练习 2-C (MockGateway) | ☐ | | |
| Phase 3: 主引擎 | ☐ | | |
| └─ engine.py (838行) | ☐ | | |
| Phase 4: Alpha | ☐ | | |
| Phase 5: RPC + Chart | ☐ | | |
| 毕业项目 | ☐ | | |

---

## 学习技巧

1. **边读边注释**：像在 `download_data.py` 做的，在源码旁边写 Java 对比注释
2. **每个文件只追问一个核心问题**：读 `event/engine.py` 时只追问"事件从产生到消费经过了几步"
3. **用 `examples/no_ui/run.py` 当入口调试**：打断点，跟踪 `MainEngine` 启动 → Gateway 连接 → Tick 到达 → OmsEngine 更新的完整链路
4. **遇到不认识的 Python 语法，第一时间类比 Java**：`@` 装饰器 ≈ AOP/代理模式；`yield` ≈ 迭代器语法糖
5. **读完一个模块就做对应练习**：不要囤积
6. **记录 Python vs Java 差异清单**：每个 Phase 结束时整理 3-5 条
