"""通过 USB 持续接收直流电机、PWM 舵机和 TTL 舵机状态，不发送运动目标。
运行前请按实际接线设置 TTL 舵机 ID 和模式；PWM 状态不代表舵盘真实角度。
"""

import pymotion as pm


DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID
TRANSPORT = "usb"  # 连接方式："usb" 或 "wifi"
MAX_SAMPLES_PER_SOURCE = 100  # 每类执行器状态最多保留的条数
ACTUATOR_SOURCES = ["motors", "pwm_servos", "ttl_servos"]  # 状态订阅来源

# 根据板卡上实际连接的两种 PWM 舵机填写端口号。
# 在这里创建设备对象不会发送动作命令，也不会让舵机转动。
CONTINUOUS_PWM_SERVO_PORT = 1  # 连续旋转 PWM 舵机连接的端口，可选 1～6
POSITION_PWM_SERVO_PORT = 2  # 位置 PWM 舵机连接的端口，可选 1～6


def show_latest(source, data):
    """显示一组最新执行器状态。"""
    if source == "motors":
        for motor in data:
            if motor.control_mode == "closed_loop":
                command = f"target={motor.target_rpm} RPM"
            else:
                command = f"commanded={motor.commanded_pwm}%"
            print(f"  M{motor.port}: {command}, measured={motor.measured_rpm} RPM")
    elif source == "pwm_servos":
        for servo in data:
            if servo.mode == "position":
                command = (
                    "angle=unavailable"
                    if servo.commanded_angle is None
                    else f"angle={servo.commanded_angle} degrees"
                )
            elif servo.mode == "speed":
                command = (
                    "speed=unavailable"
                    if servo.commanded_speed is None
                    else f"speed={servo.commanded_speed}%"
                )
            else:
                command = "command=unavailable"
            print(
                f"  S{servo.port}: mode={servo.mode}, "
                f"{command}, enabled={servo.output_enabled}"
            )
    elif source == "ttl_servos":
        for servo in data:
            print(
                f"  ID{servo.id}: angle={servo.angle:.2f} degrees, "
                f"online={servo.online}"
            )


def main():
    """持续采集状态，直到用户按下 Ctrl+C。"""

    # 每个来源各自保存最近一段状态，避免不同类型的数据混在一起。
    actuator_data = {source: [] for source in ACTUATOR_SOURCES}

    # 本例只在初始化 TTL 模式时短暂写配置，实时循环本身只读状态。
    with pm.lite.connect(DEVICE_ID, transport=TRANSPORT, timeout=15.0) as lite:
        # 同一入口通过 mode 区分连续旋转舵机和 0～180°位置舵机。
        continuous_servo = lite.pwm_servo(
            CONTINUOUS_PWM_SERVO_PORT, mode="speed"
        )
        position_servo = lite.pwm_servo(
            POSITION_PWM_SERVO_PORT, mode="position"
        )
        print(
            f"PWM servo types: S{continuous_servo.port}=continuous, "
            f"S{position_servo.port}=position"
        )

        # 创建时立即配置声明模式，因此必须在控制上下文中完成一次。
        with lite.control():
            ttl_1 = lite.ttl_servo(1, mode="position")
            ttl_2 = lite.ttl_servo(2, mode="position")

        # 声明要订阅的来源和具体舵机对象，进入上下文后设备开始持续推送。
        with lite.realtime.open(
            data_sources=ACTUATOR_SOURCES,
            pwm_servos=[continuous_servo, position_servo],
            ttl_servos=[ttl_1, ttl_2],
            frequency="low",
            data_queue_size=32,
        ) as session:
            print("Collecting real-time actuator status data...")
            print("Press Ctrl+C to stop.")

            try:
                while True:
                    # 0.1 秒内没有新事件时返回 None，不代表连接失败。
                    event = session.data.read(timeout=0.1)
                    if event is None or event.source not in actuator_data:
                        continue

                    # 每类只保留最近 MAX_SAMPLES_PER_SOURCE 条，防止内存持续增长。
                    samples = actuator_data[event.source]
                    samples.append(event.data)
                    if len(samples) > MAX_SAMPLES_PER_SOURCE:
                        del samples[0]
            except KeyboardInterrupt:
                print("\nActuator data collection stopped by the user.")

            print("\nCollected actuator status data:")
            for source in ACTUATOR_SOURCES:
                samples = actuator_data[source]
                sample_word = "sample" if len(samples) == 1 else "samples"
                print(f"- {source}: {len(samples)} {sample_word}")
                if samples:
                    show_latest(source, samples[-1])
                else:
                    print("  Latest data: unavailable")

            # received 是进入队列的事件数，dropped 是队列满时丢弃的事件数。
            stats = session.data.stats()
            print("\nReal-time data statistics:")
            print(f"Received: {stats.received}")
            print(f"Dropped: {stats.dropped}")


try:
    main()
except pm.lite.LiteError as exc:
    # 连接、模式配置或实时数据会话失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
