"""通过 USB 创建 OLED 动态页面，并演示固定显示、自动轮播和恢复欢迎页。
页面由设备本地持续刷新，按 Enter 可继续执行下一项显示操作。
"""

import pymotion as pm


OLED_PAGES = {  # OLED 页面名称、文字和动态数据字段
    "device": [
        "UPTIME / s",
        "{system.uptime}",
        "WIFI IP",
        "{wifi.ip}",
    ],
    "motors_1_2": [
        "M1 SPEED / RPM",
        "{motors.1.measured_rpm}",
        "M2 SPEED / RPM",
        "{motors.2.measured_rpm}",
    ],
    "motors_3_4": [
        "M3 SPEED / RPM",
        "{motors.3.measured_rpm}",
        "M4 SPEED / RPM",
        "{motors.4.measured_rpm}",
    ],
    "power_voltage": [
        "BATTERY / V",
        "{power.voltage}",
        "SERVO BUS / A",
        "{power.current.3}",
    ],
    "power_motors": [
        "M1-M2 / A",
        "{power.current.1}",
        "M3-M4 / A",
        "{power.current.2}",
    ],
    "sensors": [
        "DISTANCE / mm",
        "{ultrasonic.distance}",
        "LIGHT / lux",
        "{ambient_light.illuminance}",
    ],
    "imu": [
        "ROLL PITCH / deg",
        "{imu.orientation}",
        "LINE DETECTION",
        "SEE HOST LOG",
    ],
    "color": [
        "RGB RAW",
        "{color.rgb_raw}",
        "CLEAR RAW",
        "{color.clear_raw}",
    ],
}


try:
    with pm.lite.connect() as lite:
        # 设置页面、数据刷新间隔和自动换页间隔。
        lite.oled.show_pages(
            OLED_PAGES,
            refresh_interval_seconds=0.5,
            page_interval_seconds=3.0,
        )

        print(f"OLED dashboard started with {len(OLED_PAGES)} pages.")
        input("Observe the automatic page rotation, then press Enter to continue...")

        # 暂停自动轮播，并按名称固定显示 sensors 页面。
        lite.oled.show(page="sensors")
        # 也可以按页码选择第六页：lite.oled.show(page=5)
        input("The Sensors page is selected. Press Enter to resume automatic rotation...")

        # 从 device 页面恢复自动轮播。
        lite.oled.show(page="device", slide=True)
        input("Observe the page rotation, then press Enter to restore the welcome page...")

        lite.oled.show()
        print("Default welcome page restored.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
