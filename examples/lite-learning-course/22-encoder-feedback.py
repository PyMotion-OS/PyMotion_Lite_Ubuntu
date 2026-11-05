"""通过 USB 读取 M1～M4 的编码器能力、实测转速和累计计数。
本例只读取状态，不会驱动电机；累计计数不会因重新运行程序而自动归零。
"""

import pymotion as pm


# 单设备 USB 场景可保持 None；多设备时填写第 17 课发现到的目标 ID。
DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID

# 可选值："usb" 或 "wifi"。使用 Wi-Fi 时需配置目标设备的 Token。
TRANSPORT = "usb"  # 连接方式："usb" 或 "wifi"


def connect_target():
    """连接本例指定的设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


try:
    with connect_target() as lite:
        print(f"Connected device: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")

        # 一次读取 M1～M4 的最新状态。
        motor_states = lite.motors.status(max_age=0.5)

        print("\nMotor encoder feedback")
        for port in sorted(motor_states):
            state = motor_states[port]
            print(f"\nM{state.port}")
            print(f"Encoder available: {state.has_encoder}")

            if not state.has_encoder:
                print("Measured RPM: not supported")
                print("Encoder count: not supported")
            else:
                if state.measured_rpm is None:
                    print("Measured RPM: unavailable")
                else:
                    print(f"Measured RPM: {state.measured_rpm}")

                # 这是带方向的净累计计数，不是忽略方向后累加的“总转动量”。
                if state.encoder_count is None:
                    print("Encoder count: unavailable")
                else:
                    print(f"Encoder count: {state.encoder_count}")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
