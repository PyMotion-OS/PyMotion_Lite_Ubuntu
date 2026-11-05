"""通过 USB 使用编码器反馈控制 M1，演示设置零点、绝对位置和相对位置移动。
运行前请架空车轮并确保电机已经静止。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 先确认 M1 端口支持编码器；feedback_valid=False 只表示本次启动后
        # 还没有观察到有效运动，不影响在静止状态下设置零点。
        motor = lite.motor(1)
        status = motor.status(max_age=0.5)

        if status.has_encoder:
            with lite.control():
                try:
                    # 等待电机静止，并把当前位置定义为本次程序使用的 0°。
                    motor.zero_position()

                    # 移动到以新零点为参考的绝对 90° 位置，便于观察位置变化。
                    print("Moving M1 to 90 degrees...")
                    motor.move_to(
                        90,
                        speed=20,
                        tolerance=2,
                        timeout=8,
                    )
                    print("M1 reached 90 degrees.")

                    # 从当前角度相对移动 -90°，回到零点附近。
                    print("Moving M1 back by 90 degrees...")
                    motor.move_by(
                        -90,
                        speed=20,
                        tolerance=2,
                        timeout=8,
                    )
                    print("M1 returned near the zero position.")
                finally:
                    # 零点在本次设备运行期间保留；再次调用 zero_position() 可以
                    # 将另一个静止位置重新定义为零点。
                    motor.stop()
                    print("M1 stopped; the current zero position remains active.")

        else:
            # 当前端口没有编码器时，不能使用角度位置控制。
            print("Position control skipped: M1 has no encoder capability.")

except pm.lite.LiteError as exc:
    # 位置、反馈和设备错误统一显示为 LiteError。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
