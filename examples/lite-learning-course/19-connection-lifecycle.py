"""演示连接的关闭、重复关闭和重新连接；关闭后，旧连接创建的对象将失效。
本例不控制执行器，多设备环境应填写目标 ``DEVICE_ID``。
"""

import pymotion as pm


# 单设备 USB 入门场景保持 None；多设备时填入第 17 课发现到的设备 ID。
DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"  # 连接方式："usb" 或 "wifi"


def connect_target(device_id=None):
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID if device_id is None else device_id,
        transport=TRANSPORT,
        timeout=15.0,
    )


def close_and_check_old_child():
    """关闭连接，并确认旧对象已经失效。"""

    lite = None
    try:
        lite = connect_target()
        device_id = lite.connection.device_id
        old_motor = lite.motor(1)

        print("Initial connection")
        print(f"Device ID: {device_id}")
        print(f"Transport: {lite.connection.transport}")
        print(f"Closed: {lite.is_closed}")

        lite.close()

        print("\nAfter close()")
        print(f"Closed: {lite.is_closed}")

        # 重复关闭是安全的，不会重新打开连接。
        lite.close()
        print("Calling close() a second time completed safely.")

        print("\nOld motor object")
        try:
            old_motor.status(max_age=0.5)
        except pm.lite.ConnectionClosedError:
            print("The old motor object is no longer usable.")
        else:
            print("Unexpected: the old motor object remained usable.")

        return device_id
    finally:
        if lite is not None and not lite.is_closed:
            lite.close()


try:
    original_device_id = close_and_check_old_child()

    print("\nReconnect")
    with connect_target(original_device_id) as new_lite:
        new_motor = new_lite.motor(1)
        print(f"Requested device: {original_device_id}")
        print(f"Connected device: {new_lite.connection.device_id}")
        print(f"Fresh motor object: M{new_motor.port}")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
