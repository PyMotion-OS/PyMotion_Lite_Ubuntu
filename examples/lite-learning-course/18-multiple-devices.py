"""使用 ``pm.lite.list_devices()`` 发现 USB 和 Wi-Fi 设备，并按设备 ID 选择目标。
本例只执行发现，不建立认证或控制连接；存在多台设备时请填写 ``DEVICE_ID``。
"""

import pymotion as pm


DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID


def select_device(devices):
    """选择唯一设备；无法明确选择时返回 None。"""

    # 没有发现设备时直接结束选择流程。
    if not devices:
        print("No PyMotion Lite devices were found.")
        return None

    device_word = "device" if len(devices) == 1 else "devices"
    print(f"Found {len(devices)} PyMotion Lite {device_word}:")
    for device in devices:
        links = ", ".join(device.transports)
        print(f"- {device.device_id}, available connections: {links}")

    # 用户填写了设备 ID 时，只接受完全匹配的设备。
    if DEVICE_ID is not None:
        for device in devices:
            if device.device_id == DEVICE_ID:
                return device
        print(f"Configured device was not found: {DEVICE_ID}")
        return None

    # 仅发现一台设备时，可以安全地自动选择。
    if len(devices) == 1:
        print("One PyMotion Lite device was found; selecting it automatically.")
        return devices[0]

    print("More than one Lite device was found.")
    print("Copy one listed ID into DEVICE_ID, then run this example again.")
    return None


try:
    # list_devices() 只做发现，不会连接或取得设备控制权。
    devices = pm.lite.list_devices()
    selected = select_device(devices)

    if selected is not None:
        print("Selected device")
        print(f"Device ID: {selected.device_id}")
        print(f"Available connections: {', '.join(selected.transports)}")
        print("Call connect() to verify authentication and establish a connection.")
        print("No connection was opened, so no authentication Token was required.")

except pm.lite.LiteError as exc:
    # USB/Wi-Fi 发现过程失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
