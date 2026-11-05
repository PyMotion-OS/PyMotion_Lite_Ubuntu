"""通过 Wi-Fi 持续接收传感器和设备状态，并显示接收及丢弃统计。
本例不会控制执行器；``frequency`` 是目标更新档位，实际频率仍受各数据源采样能力限制。
"""

import pymotion as pm


DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID
TRANSPORT = "wifi"  # 连接方式："wifi" 或 "usb"
MAX_SAMPLES_PER_SOURCE = 100  # 每类数据在本例中最多保留的条数

# 每个名称对应一种可以独立接收的数据来源。
SENSOR_SOURCES = [  # 需要订阅的实时传感器和设备状态来源
    "status",
    "imu",
    "ultrasonic",
    "line_tracker",
    "ambient_light",
    "color",
    "lidar",
    "power",
]


def show_latest(source, data):
    """按适合终端阅读的格式显示一条最新数据。"""
    if source == "status":
        print(f"  State: {data.state}")
    elif source == "imu":
        acceleration = data.acceleration
        orientation = data.orientation
        if acceleration is None or orientation is None:
            print("  IMU data: unavailable")
        else:
            print(
                "  Acceleration: "
                f"x={acceleration.x:.1f}, y={acceleration.y:.1f}, "
                f"z={acceleration.z:.1f} mm/s^2"
            )
            print(
                f"  Orientation: roll={orientation.roll:.2f}, "
                f"pitch={orientation.pitch:.2f} degrees"
            )
    elif source == "ultrasonic":
        if data.distance is None:
            print("  Distance: unavailable")
        else:
            print(f"  Distance: {data.distance:.1f} mm")
    elif source == "line_tracker":
        if data.is_detected is None:
            print("  Detected: unavailable")
        else:
            detected = ", ".join("1" if value else "0" for value in data.is_detected)
            print(f"  Detected: {detected}")
    elif source == "ambient_light":
        if data.illuminance is None:
            print("  Illuminance: unavailable")
        else:
            print(f"  Illuminance: {data.illuminance:.1f} lux")
    elif source == "color":
        if data.red is None:
            print("  Color values: unavailable")
        else:
            print(f"  RGB: {data.red}, {data.green}, {data.blue}")
    elif source == "lidar":
        print(f"  Point count: {len(data.points)}")
    elif source == "power":
        values = (
            ("M1/M2 supply current", data.current(1), "A"),
            ("M3/M4 supply current", data.current(2), "A"),
            ("S1-S6 PWM servo supply current", data.current(3), "A"),
            ("Battery voltage", data.voltage, "V"),
        )
        for name, value, unit in values:
            if value is None:
                print(f"  {name}: unavailable")
            else:
                print(f"  {name}: {value:.3f} {unit}")


def main():
    """持续收集数据，直到用户按下 Ctrl+C。"""

    # 为每种数据来源准备一个列表，列表中保存已经收到的数据对象。
    sensor_data = {source: [] for source in SENSOR_SOURCES}

    # DEVICE_ID=None 表示仅发现一台设备时自动选择；多设备时应填写目标设备 ID。
    with pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    ) as lite:
        # 进入上下文时启动数据流，退出时 SDK 会自动停止数据流并释放资源。
        with lite.realtime.open(
            data_sources=SENSOR_SOURCES,
            frequency="low",
            data_queue_size=32,
        ) as session:
            print("Collecting real-time sensor data...")
            print("Press Ctrl+C to stop.")

            try:
                while True:
                    # event.source 是来源名称，event.data 是对应的类型化数据对象。
                    # 0.1 秒内没有新数据时返回 None，程序可以继续等待。
                    event = session.data.read(timeout=0.1)
                    if event is None:
                        continue

                    # 只汇总本课程明确订阅的来源，避免把未知数据误当成课程结果。
                    if event.source not in sensor_data:
                        continue

                    samples = sensor_data[event.source]
                    samples.append(event.data)

                    # 只保留最近 100 条，避免程序长时间运行后列表无限增长。
                    if len(samples) > MAX_SAMPLES_PER_SOURCE:
                        del samples[0]

            except KeyboardInterrupt:
                print("\nSensor collection stopped by the user.")

            print("\nCollected sensor data:")
            for source in SENSOR_SOURCES:
                samples = sensor_data[source]
                sample_word = "sample" if len(samples) == 1 else "samples"
                print(f"- {source}: {len(samples)} {sample_word}")
                if samples:
                    show_latest(source, samples[-1])
                else:
                    print("  Latest data: unavailable")

            # received 是 SDK 放入队列的事件总数；dropped 是队列满时丢弃的数量。
            stats = session.data.stats()
            print("\nReal-time data statistics:")
            print(f"Received: {stats.received}")
            print(f"Dropped: {stats.dropped}")


try:
    main()
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
