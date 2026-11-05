"""通过 USB 读取超声波、五路循迹、环境光和颜色传感器。
本例不会控制执行器，未安装或暂无有效数据的传感器会显示 unavailable。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 本例只读数据，不需要取得设备控制权。
        # 分别读取四类传感器的最新数据。
        ultrasonic = lite.ultrasonic(max_age=0.5)
        line_tracker = lite.line_tracker(max_age=0.5)
        ambient_light = lite.ambient_light(max_age=0.5)
        color = lite.color(max_age=0.5)

        print("\nUltrasonic")
        # 无回波通常表示目标超出量程；None 表示“没有可靠距离”，不能当作 0 mm。
        if ultrasonic.distance is not None:
            print(f"Distance: {ultrasonic.distance:g} mm")
        else:
            print("Distance: unavailable")

        print("\nLine tracker")
        # 五个元素依次对应板上的五路循迹输入，True 表示检测到黑线。
        if line_tracker.is_detected is not None:
            print(f"Detected: {line_tracker.is_detected}")
        else:
            print("Detected: unavailable")

        print("\nAmbient light")
        # illuminance 是环境光照度，单位为 lux。
        if ambient_light.illuminance is not None:
            print(f"Illuminance: {ambient_light.illuminance:g} lux")
        else:
            print("Illuminance: unavailable")

        print("\nColor")
        # RGB 和 Clear 是传感器原始计数，不是已经识别出的颜色名称。
        if (
            color.red is not None
            and color.green is not None
            and color.blue is not None
            and color.clear is not None
        ):
            print(f"Red: {color.red}")
            print(f"Green: {color.green}")
            print(f"Blue: {color.blue}")
            print(f"Clear: {color.clear}")
        else:
            print("Color values: unavailable")

except pm.lite.LiteError as exc:
    # 连接或任一传感器读取失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
