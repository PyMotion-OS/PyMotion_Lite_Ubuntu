"""通过 USB 演示 0～180°位置 PWM 舵机的单路和批量角度控制。
运行前请确认所选端口接入的是位置舵机并清空运动范围；PWM 舵机不提供角度反馈。
"""

import time

import pymotion as pm


SERVO_1_PORT = 1  # 第一只位置舵机连接的 PWM 端口，可选 1～6
SERVO_2_PORT = 2  # 第二只位置舵机连接的 PWM 端口，可选 1～6
MOVE_WAIT_SECONDS = 1.0  # 每次发送角度后等待舵机运动的时间（秒）


def main() -> None:
    try:
        with pm.lite.connect() as lite:
            # 同一入口通过 mode 明确物理舵机类型；错误模式不会发送动作命令。
            servo = lite.pwm_servo(SERVO_1_PORT, mode="position")

            with lite.control():
                try:
                    print(f"Moving position servo S{servo.port} to 45 degrees...")
                    servo.move_to(45)
                    time.sleep(MOVE_WAIT_SECONDS)

                    # 先把两路都归到 90°，建立每次运行都一致的动作起点。
                    print(
                        f"Centering servos S{SERVO_1_PORT} and S{SERVO_2_PORT}..."
                    )
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 90,
                            SERVO_2_PORT: 90,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)

                    # 两路向相反方向移动，确保第二路在每次运行中都有可见行程。
                    print(
                        f"Moving S{SERVO_1_PORT} to 45 degrees and "
                        f"S{SERVO_2_PORT} to 135 degrees..."
                    )
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 45,
                            SERVO_2_PORT: 135,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)

                    print("Returning both position servos to 90 degrees...")
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 90,
                            SERVO_2_PORT: 90,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)
                finally:
                    # 正常结束、异常或 Ctrl+C 都关闭全部 PWM 输出。
                    lite.pwm_servos.stop()

            print("PWM position-servo commands completed; outputs are disabled.")

    except pm.lite.LiteError as exc:
        print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")


if __name__ == "__main__":
    main()
