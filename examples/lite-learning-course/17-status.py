"""通过 USB 使用 ``lite.status()`` 读取设备、控制及安全状态。
本例不会申请控制权；``status.age`` 表示状态数据年龄，不是通信延迟。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 该操作只读取状态；数据超过 max_age 时 SDK 会报告过期，而不是返回旧值。
        status = lite.status(max_age=1.0)

        print("Device status")
        print(f"Device ID: {status.device_id}")
        print(f"State: {status.state}")
        print(f"Status age: {status.age:.3f} s")

        # lease_active 表示当前是否存在有效控制会话。
        print("\nControl")
        print(f"Active: {status.lease_active}")

        # 急停锁存和故障锁存是两个相互独立的安全状态。
        print("\nSafety")
        print(f"Emergency stop: {status.estop_latched}")
        print(f"Fault: {status.fault_latched}")

        if status.estop_latched:
            print(f"Emergency stop reason: {status.estop_reason}")

        if status.fault_latched:
            print(f"Fault reason: {status.fault_reason}")

except pm.lite.LiteError as exc:
    # 连接失败或状态超过允许年龄时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
