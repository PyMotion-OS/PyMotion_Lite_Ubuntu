"""通过 USB 连接一台 PyMotion Lite，并使用 ``lite.status()`` 显示基本状态。
运行前请连接设备，并在当前终端设置 ``PYMOTION_AUTH_TOKEN``；全新设备的出厂 Token
为 ``123456``，已经修改过 Token 的设备应使用当前值。
使用 USB 时不需要先完成 Wi-Fi。用户 Token 保存在设备中并优先于出厂 Token，
因此修改 Token 后，USB 与 Wi-Fi 连接都必须提供当前用户 Token。

Windows PowerShell：
    $env:PYMOTION_AUTH_TOKEN = "123456"

Windows 命令提示符（CMD）：
    set PYMOTION_AUTH_TOKEN=123456

Ubuntu Bash：
    export PYMOTION_AUTH_TOKEN="123456"
"""

import pymotion as pm


try:
    # 显示当前 Python 实际导入的 PyMotion Lite SDK 版本。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 连接一台 Lite。离开 with 代码块时，连接会自动关闭。
    with pm.lite.connect() as lite:
        # max_age=1.0 表示不接受超过 1 秒的旧状态。
        status = lite.status(max_age=1.0)

        # 输出设备标识和当前状态摘要，便于确认连接是否正确。
        print(f"Device ID: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")
        print(f"State: {status.state}")
        # age 表示这份状态数据已经存在多久，不是 USB/Wi-Fi 通信耗时。
        print(f"Status age: {status.age:.3f} s")

except pm.lite.LiteError as exc:
    # SDK 连接或状态读取失败时，显示便于排查的错误信息。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
