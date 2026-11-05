"""通过 Wi-Fi 连接已完成配网的 PyMotion Lite，读取状态后再演示 USB 重连。
运行前请确保电脑与设备位于可互访的局域网，并在当前终端设置与设备一致的
``PYMOTION_AUTH_TOKEN``；首次配网步骤请参阅用户手册。
"""

import pymotion as pm


# 只有需要演示“关闭 Wi-Fi 后再改连 USB”时才改为 True。
SWITCH_TO_USB = False  # 是否在 Wi-Fi 演示结束后继续演示 USB 重连


def reconnect_by_usb() -> None:
    """在前一个 Wi-Fi 会话关闭后，使用默认 USB 链路重新连接。"""

    with pm.lite.connect(timeout=15.0) as lite:
        connection = lite.connection
        print("Reconnected using USB.")
        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")


try:
    # 读取 SDK 版本不需要先连接设备。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 运行前应已按上面的首次使用流程完成配网和 Token 设置。
    with pm.lite.connect(
        transport="wifi",
        timeout=60.0,
    ) as lite:
        connection = lite.connection
        status = lite.status(max_age=2.0)

        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")
        print(f"State: {status.state}")

    # Wi-Fi 的 with 已经退出后，才允许按需建立新的 USB 会话。
    if SWITCH_TO_USB:
        reconnect_by_usb()

except pm.lite.LiteError as exc:
    # 连接、身份认证和状态读取错误统一显示为 LiteError。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
