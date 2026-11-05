"""通过 USB 读取超声波距离，并使用 ``lite.oled.show()`` 在 OLED 上显示结果。
运行前请设置设备 Token；没有有效测距时会显示 unavailable。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 读取一次超声波结果；max_age=0.5 表示最多接受旧 0.5 秒的数据。
        ultrasonic = lite.ultrasonic(max_age=0.5)

        # None 表示当前没有有效距离，不能把它当成真实的 0 mm。
        if ultrasonic.distance is None:
            distance_text = "unavailable"
        else:
            # SDK 的超声波距离单位是毫米。
            distance_text = f"{ultrasonic.distance:g} mm"

        # 终端和 OLED 使用同一个结果，避免两处显示不一致。
        print(f"Distance: {distance_text}")

        # 在 OLED 上临时显示三行文字，5 秒后结束本次临时显示。
        lite.oled.show(
            [
                "PyMotion Lite",
                "Ultrasonic",
                f"Dist: {distance_text}",
            ],
            duration_seconds=5.0,
        )

except pm.lite.LiteError as exc:
    # 连接、传感器或 OLED 操作失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
