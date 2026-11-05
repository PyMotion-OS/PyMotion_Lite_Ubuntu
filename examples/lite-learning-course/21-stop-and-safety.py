"""通过 USB 演示普通停止，以及需要人工确认的急停操作。
默认只执行 ``lite.stop()``；切换 ``SAFETY_EXAMPLE`` 前请确认现场安全。
"""

import pymotion as pm


# 单设备 USB 入门场景可保持 None；多设备时填写第 17 课发现到的目标 ID。
DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"  # 连接方式："usb" 或 "wifi"

# 可选值：None 或 "emergency_stop"。
SAFETY_EXAMPLE = None  # 选择普通停止或急停演示


def connect_target():
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


def show_safety_status(lite, heading):
    """显示设备状态，以及相互独立的急停和故障状态。"""

    status = lite.status(max_age=1.0)
    print(f"\n{heading}")
    print(f"State: {status.state}")
    print(f"Emergency stop: {status.estop_latched}")
    print(f"Fault: {status.fault_latched}")
    if status.estop_latched:
        print(f"Emergency stop reason: {status.estop_reason}")
    if status.fault_latched:
        print(f"Fault reason: {status.fault_reason}")
    return status


latched_safety_may_be_active = False


try:
    if SAFETY_EXAMPLE not in {None, "emergency_stop"}:
        print(f"Unknown SAFETY_EXAMPLE value: {SAFETY_EXAMPLE!r}")
    else:
        with connect_target() as lite:
            print(f"Connected device: {lite.connection.device_id}")
            print(f"Transport: {lite.connection.transport}")
            status = show_safety_status(lite, "Status before stop")

            stop = lite.stop(timeout=2.0)
            if not stop.succeeded:
                raise pm.lite.DeviceFaultError(
                    "ordinary stop was not fully acknowledged"
                )
            print("\nOrdinary stop completed.")

            status = show_safety_status(lite, "Status after ordinary stop")

            if SAFETY_EXAMPLE == "emergency_stop":
                confirmation = input(
                    "After clearing the area, type TRIGGER ESTOP to continue: "
                )
                if confirmation == "TRIGGER ESTOP":
                    latched_safety_may_be_active = True
                    report = lite.emergency_stop(timeout=3.0)
                    if not report.succeeded:
                        raise pm.lite.DeviceFaultError(
                            "emergency stop was not acknowledged"
                        )
                    print("Emergency stop activated.")
                    show_safety_status(lite, "Status after emergency stop")

                    confirmation = input(
                        "After a physical safety check, type RESET ESTOP: "
                    )
                    if confirmation == "RESET ESTOP":
                        report = lite.reset_estop(timeout=3.0)
                        if not report.succeeded:
                            raise pm.lite.DeviceFaultError(
                                "emergency stop reset was not acknowledged"
                            )
                        reset_status = show_safety_status(
                            lite, "Status after emergency stop reset"
                        )
                        latched_safety_may_be_active = reset_status.estop_latched
                        print("Emergency stop reset.")
                        print("Previous motion was not resumed.")
                    else:
                        print("Emergency stop remains active.")
                else:
                    print("Emergency stop example skipped.")

            else:
                print("\nOrdinary stop example completed.")

except pm.lite.CommandOutcomeUnknownError as exc:
    latched_safety_may_be_active = True
    print(
        f"The safety operation result [{type(exc).__name__}] "
        f"could not be confirmed: {exc}"
    )
    print("Reconnect and inspect the device; do not repeat it automatically.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")

finally:
    if latched_safety_may_be_active:
        print("A safety latch may still be active; inspect the device before recovery.")
