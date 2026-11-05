"""通过 USB 使用 ``lite.power()`` 读取电池电压及电机、PWM 舵机的分组供电电流。
本例不会启动负载，暂时无效的数据会显示 unavailable。
"""

import pymotion as pm


def print_measurement(name, value, decimal_places):
    """按测量值的实际精度显示，缺少数据时显示 unavailable。"""

    if value is None:
        print(f"{name}: unavailable")
    else:
        print(f"{name}: {value:.{decimal_places}f}")


try:
    with pm.lite.connect() as lite:
        # 本例只读取电源测量值，不需要取得设备控制权。
        # max_age 同时限定样本年龄和本次读取的等待预算。
        power = lite.power(max_age=1.0)

        print("\nPower measurements")
        # 电流显示到 0.001 A，电压显示到 0.01 V，避免暗示不存在的测量精度。
        measurements = [
            ("M1/M2 supply current (A)", power.current(1), 3),
            ("M3/M4 supply current (A)", power.current(2), 3),
            ("PWM servo supply current (A)", power.current(3), 3),
            ("Battery voltage (V)", power.voltage, 2),
        ]
        # 使用同一个辅助函数统一处理有效数值和 unavailable。
        for name, value, decimal_places in measurements:
            print_measurement(name, value, decimal_places)

except pm.lite.LiteError as exc:
    # 连接或电源测量读取失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
