"""通过 USB 演示 TTL 舵机的位置或速度模式，可通过 ``DEMO_MODE`` 选择。
运行前请确认舵机 ID 和实际模式，接好外部电源并清空运动范围。
"""

import time

import pymotion as pm


DEMO_MODE = "position"  # 演示模式："position" 位置模式或 "speed" 速度模式
MOVE_DURATION_SECONDS = 2.0  # 位置模式下每段动作的计划用时（秒）
# duration 是舵机计划运动时间；额外等待用于机械到位和状态反馈更新。
MOVE_SETTLE_MARGIN_SECONDS = 0.5  # 动作结束后额外等待反馈更新的时间（秒）
MOVE_WAIT_SECONDS = MOVE_DURATION_SECONDS + MOVE_SETTLE_MARGIN_SECONDS  # 总等待时间
SPEED_PERCENT = 20.0  # 速度模式的目标速度百分比
SPEED_DURATION_SECONDS = 3.0  # 速度模式每段连续转动时间（秒）
MOVE_OFFSET_DEG = 60.0  # 位置模式相对中心移动的角度（度）
RETURN_TOLERANCE_DEG = 5.0  # 判断是否回到中心附近的允许误差（度）


def run_position_demo(lite: pm.lite.Lite) -> None:
    """让两只 TTL 舵机完成位置动作，并检查最终位置反馈。"""

    # 创建对象时立即将对应舵机配置为位置模式。
    servo_1 = lite.ttl_servo(1, mode="position")
    servo_2 = lite.ttl_servo(2, mode="position")

    # 不公开具体舵机型号，直接根据每只舵机报告的最大角度计算中心位置。
    center_1 = servo_1.max_angle / 2.0
    center_2 = servo_2.max_angle / 2.0
    target_1 = center_1 + MOVE_OFFSET_DEG
    target_2 = center_2 + MOVE_OFFSET_DEG

    # 批量命令让两只舵机同时回到各自角度范围的中心。
    print("Centering TTL servos with IDs 1 and 2...")
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: center_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    print(f"Moving TTL servo with ID 1: {center_1:.1f} -> {target_1:.1f} degrees...")
    servo_1.move_to(target_1, duration=MOVE_DURATION_SECONDS)
    time.sleep(MOVE_WAIT_SECONDS)

    print(
        "Returning servo 1 to center while servo 2 moves "
        f"about {MOVE_OFFSET_DEG:g} degrees..."
    )
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: target_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    print("Returning both TTL servos to their center positions...")
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: center_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    # 读取真实反馈，确认最终位置位于允许误差范围内。
    final_1 = servo_1.status().angle
    final_2 = servo_2.status().angle
    error_1 = abs(final_1 - center_1)
    error_2 = abs(final_2 - center_2)
    print(
        "Final position feedback: "
        f"ID1={final_1:.2f}° (error {error_1:.2f}°), "
        f"ID2={final_2:.2f}° (error {error_2:.2f}°)"
    )
    if error_1 > RETURN_TOLERANCE_DEG or error_2 > RETURN_TOLERANCE_DEG:
        raise RuntimeError("TTL servo did not return to its center position")

    # 位置演示完成后停止两只 TTL 舵机的输出。
    lite.ttl_servos.stop()


def run_speed_demo(lite: pm.lite.Lite) -> None:
    """让两只 TTL 舵机演示连续旋转，并在结束时停止输出。"""

    # 创建对象时立即将对应舵机配置为速度模式。
    servo_1 = lite.ttl_servo(1, mode="speed")
    servo_2 = lite.ttl_servo(2, mode="speed")

    print("Running TTL servo with ID 1 at 20% speed for 3 seconds...")
    servo_1.set_speed(SPEED_PERCENT, duration=SPEED_DURATION_SECONDS)

    print("Running TTL servos with IDs 1 and 2 in opposite directions for 3 seconds...")
    # 批量速度中的正负号表示两只舵机向相反方向转动。
    lite.ttl_servos.set_speeds(
        {servo_1: SPEED_PERCENT, servo_2: -SPEED_PERCENT},
        duration=SPEED_DURATION_SECONDS,
    )
    lite.ttl_servos.stop()
    print("Speed outputs stopped; both servos remain configured in speed mode.")


try:
    # 两种演示共用默认 USB 连接和同一个控制会话。
    with pm.lite.connect() as lite:
        with lite.control():
            # 根据开头的 DEMO_MODE 只运行一种模式，避免意外切换。
            if DEMO_MODE == "position":
                run_position_demo(lite)
            elif DEMO_MODE == "speed":
                run_speed_demo(lite)
            else:
                raise ValueError("DEMO_MODE must be 'position' or 'speed'")

        print("TTL servo demonstration completed.")

except pm.lite.LiteError as exc:
    # 设备通信或舵机命令失败。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
except (RuntimeError, ValueError) as exc:
    # 参数填写错误或最终位置验证未通过。
    print(f"TTL servo demonstration failed [{type(exc).__name__}]: {exc}")
