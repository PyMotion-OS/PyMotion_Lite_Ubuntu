"""通过 USB 演示连续旋转 PWM 舵机的单路和批量速度控制。
运行前请确认 S1、S2 接入连续旋转舵机并清空运动范围；速度值为百分比而非 RPM。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # pwm_servo(1, mode="speed") 对应板卡丝印 S1 的连续旋转舵机。
        servo = lite.pwm_servo(1, mode="speed")

        with lite.control():
            try:
                # S1 以 25% 速度运行 2 秒，到时自动关闭 S1 输出。
                print("Running servo S1 for 2 seconds...")
                servo.set_speed(25, duration=2.0)

                # 字典同时设置 S1、S2；负速度表示相反方向。
                print("Running servos S1 and S2 in opposite directions...")
                lite.pwm_servos.set_speeds(
                    {
                        1: 25,
                        2: -25,
                    },
                    duration=2.0,
                )
            finally:
                # 正常结束、通信异常或 Ctrl+C 时都明确关闭全部六路 PWM 输出。
                lite.pwm_servos.stop()

        print("Continuous-rotation servos have stopped.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
