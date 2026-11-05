"""通过 USB 短暂运行 M1，并读取运行中和停止后的四路电机状态。
``commanded_pwm`` 表示开环百分比，``measured_rpm`` 表示编码器实测转速。
"""

import time

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        motor = lite.motor(1)

        # 让 M1 以 20% 的开环速度运行 0.5 秒，然后读取最新状态。
        # 无论读取是否成功，finally 都会先停止电机。
        with lite.control():
            try:
                motor.set_pwm(20)
                time.sleep(0.5)

                all_status = lite.motors.status(max_age=0.0)
                status = motor.status(max_age=0.0)
            finally:
                motor.stop()

        print("\nM1 status while running")
        print(f"Port: M{status.port}")
        print(f"Control mode: {status.control_mode}")
        print(f"Commanded PWM: {status.commanded_pwm}%")
        print(f"Measured speed: {status.measured_rpm} RPM")
        print(f"Fault: {status.fault}")

        if status.has_encoder and status.feedback_valid:
            # 多圈累计角度，不会自动限制在 0~360°。
            print(f"Measured angle (multi-turn): {status.measured_angle} degrees")
        else:
            print("Encoder feedback: unavailable")

        # 依次显示 M1～M4，便于比较每路的指令速度和实测速度。
        print("\nStatus of all motors")
        for port, motor_status in all_status.items():
            print(
                f"M{port}: commanded={motor_status.commanded_pwm}%, "
                f"measured={motor_status.measured_rpm} RPM"
            )

        # stop() 会立即清除驱动命令；机械惯性和采样周期可能让 RPM 稍后才归零。
        # 最多等待 3 秒，避免例程无限等待。
        stopped = motor.status(max_age=0.0)
        for _ in range(60):
            rpm_stopped = (
                stopped.measured_rpm is None
                or abs(stopped.measured_rpm) <= 2.0
            )
            if stopped.commanded_pwm == 0.0 and rpm_stopped:
                break
            time.sleep(0.05)
            stopped = motor.status(max_age=0.0)

        print("\nM1 status after stopping")
        print(f"Commanded PWM: {stopped.commanded_pwm}%")
        print(f"Measured speed: {stopped.measured_rpm} RPM")

        if stopped.measured_rpm is None:
            print("Physical state: encoder speed is unavailable.")
        elif abs(stopped.measured_rpm) <= 2.0:
            print("Physical state: M1 encoder speed is stationary.")
        else:
            print("Physical state: M1 is still coasting after 3 seconds.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
