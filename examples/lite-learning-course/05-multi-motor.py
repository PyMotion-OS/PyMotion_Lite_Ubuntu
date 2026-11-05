"""通过 USB 批量控制同一台 Lite 上的多路直流电机，并统一停止。
运行前请架空车轮；字典中未列出的端口不会被改变。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 本例程的全部电机命令共用一个控制会话。
        with lite.control():
            # 字典中的键是电机端口，值是 -100～100 的速度百分比。
            # duration=2.0 表示这些电机运行 2 秒后自动停止。
            print("Running M1, M2, M3 and M4 for 2 seconds...")
            lite.motors.set_pwms(
                {
                    1: 20,
                    2: 30,
                    3: 40,
                    4: 50,
                },
                duration=2.0,
            )

            # 上一段结束后四路都已停止；这一段只运行列出的 M1 和 M2。
            print("Running M1 and M2 for 2 seconds...")
            lite.motors.set_pwms(
                {
                    1: -20,
                    2: -30,
                },
                duration=2.0,
            )

            # 批量示例结束时显式停止全部四路直流电机。
            lite.motors.stop()

        print("Batch motor examples completed; all motors are stopped.")

except pm.lite.LiteError as exc:
    # 连接、控制和电机命令错误统一显示为 LiteError。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
