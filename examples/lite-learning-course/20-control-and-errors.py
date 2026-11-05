"""演示使用 ``lite.control()`` 申请控制权，并处理常见连接和命令异常。
默认不驱动电机；启用 ``RUN_MOTOR_EXAMPLE`` 前请架空 M1 并清空运动范围。
"""

import pymotion as pm


# 单设备 USB 入门场景保持 None；多设备时填入目标设备 ID。
DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"  # 连接方式："usb" 或 "wifi"

# 为 True 时 M1 会低速运行 1 秒；运行前确认输出轴和负载可以安全转动。
RUN_MOTOR_EXAMPLE = False  # 改为 True 后才会运行 M1 电机示例


def connect_target():
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


try:
    with connect_target() as lite:
        print(f"Connected device: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")
        print("Requesting device control...")

        # 此控制块内的所有写命令共用同一份控制权。
        with lite.control(timeout=5.0):
            print("Device control acquired.")

            # 同一连接不能嵌套申请控制权；捕获这个错误后，外层控制块仍可继续使用。
            try:
                with lite.control(timeout=5.0):
                    pass
            except pm.lite.ControlUnavailableError:
                print("Nested control was rejected safely.")

            if RUN_MOTOR_EXAMPLE:
                print("Running M1 at low speed for one second.")
                lite.motor(1).set_pwm(20, duration=1.0)
            else:
                print("Motor example disabled; no motion command was sent.")

        print("Device control released automatically.")

    print("Connection closed.")
    print("Control and error-handling example completed.")

except pm.lite.MultipleDevicesFoundError as exc:
    print(f"Multiple Lite devices [{type(exc).__name__}]: {exc}")
    print("Set DEVICE_ID at the top of this file, then run it again.")

except (
    pm.lite.DeviceNotFoundError,
    pm.lite.AuthenticationError,
    pm.lite.ConnectionTimeoutError,
) as exc:
    print(f"Connection error [{type(exc).__name__}]: {exc}")

except (pm.lite.LeaseDeniedError, pm.lite.DeviceBusyError) as exc:
    print(f"Device control is unavailable [{type(exc).__name__}]: {exc}")

except pm.lite.CommandOutcomeUnknownError as exc:
    print(
        f"Command outcome is unknown [{type(exc).__name__}] "
        f"during {exc.operation} ({exc.stage}): {exc}"
    )
    print("Do not automatically repeat a motion command; inspect the device first.")

except pm.lite.EstopActiveError as exc:
    print(f"Emergency stop is active [{type(exc).__name__}]: {exc}")
    print("Inspect the device before recovery.")

except pm.lite.DeviceFaultError as exc:
    print(f"Device fault [{type(exc).__name__}]: {exc}")
    print("Resolve the physical cause before clearing the fault.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
