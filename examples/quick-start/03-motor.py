"""通过 USB 控制 M1，演示 ``set_pwm()`` 开环转动以及编码器位置移动。
运行前请设置设备 Token，并架空车轮、清空运动范围。
"""

import pymotion as pm


try:
    # 建立默认 USB 连接；离开 with 后 SDK 会自动关闭连接。
    with pm.lite.connect() as lite:
        # motor(1) 表示选择板卡 M1 端口。
        motor = lite.motor(1)

        # 所有电机动作都必须放在控制上下文中，退出时会执行安全收尾。
        with lite.control():
            # 30 是开环速度百分比，不是 RPM；duration 到时后自动停止。
            print("Running M1 at 30% for 2 seconds...")
            motor.set_pwm(30, duration=2.0)

            # 把电机当前静止位置定义为本次运行使用的临时 0°。
            print("Setting the current position to 0 degrees...")
            motor.zero_position()

            # move_to() 使用绝对角度：从临时零点移动到 90°。
            print("Rotating M1 to the absolute 90-degree position...")
            motor.move_to(90, speed=20, tolerance=2, timeout=8)

            # move_by() 使用相对角度：从当前位置反向移动 90°。
            print("Rotating M1 90 degrees in reverse from its current position...")
            motor.move_by(-90, speed=20, tolerance=2, timeout=8)

        print("M1 stopped.")

except pm.lite.LiteError as exc:
    # 连接、控制或运动失败时统一显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
