#!/usr/bin/env python3
"""vnpy 启动脚本"""
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

qapp = create_qapp()

event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 逐个尝试加载，失败不中断
modules: list[tuple[str, str, str]] = [
    ("gateway", "vnpy_ctp", "CtpGateway"),
    ("app", "vnpy_ctastrategy", "CtaStrategyApp"),
    ("app", "vnpy_ctabacktester", "CtaBacktesterApp"),
    ("app", "vnpy_datamanager", "DataManagerApp"),
]

for mod_type, mod_name, cls_name in modules:
    try:
        mod = __import__(mod_name, fromlist=[cls_name])
        cls = getattr(mod, cls_name)
        if mod_type == "gateway":
            main_engine.add_gateway(cls)
        else:
            main_engine.add_app(cls)
        print(f"  [OK] {cls_name}")
    except Exception as e:
        print(f"  [跳过] {cls_name} — {e}")

main_window = MainWindow(main_engine, event_engine)
main_window.showMaximized()
print(f"vnpy 启动成功！")
qapp.exec()
