"""通过 USB 连接 PyMotion Lite，并读取设备 ID、连接方式和状态。
运行前请在当前终端设置 ``PYMOTION_AUTH_TOKEN``；全新设备的出厂 Token 为
``123456``，已经修改过 Token 的设备应使用当前值。
"""

import pymotion as pm


try:
    # 打开设备前也可以读取当前安装的 SDK 版本。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 省略 transport 时使用默认 USB 连接。
    # Ubuntu 虚拟机在 USB 设备重新打开时可能需要更长的枚举时间。
    with pm.lite.connect(timeout=15.0) as lite:
        connection = lite.connection
        status = lite.status(max_age=1.0)

        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")
        print(f"State: {status.state}")

except pm.lite.LiteError as exc:
    # 连接或读取失败时统一显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
