"""通过 USB 演示 OLED 临时文字、动态页面和页面轮播。
``show()`` 控制当前显示，``show_pages()`` 配置页面并开始轮播。
"""

import time

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 先临时显示一条固定文字；持续时间到后设备自动结束临时显示。
        lite.oled.show("Connected", duration_seconds=2.0)
        time.sleep(2.0)

        # 动态字段只提供数值；标签和单位由普通文本行按页面用途自由添加。
        # show_pages() 一次提交全部页面，随后由设备本地更新字段和自动换页。
        lite.oled.show_pages(
            [
                [
                    "DISTANCE / mm",
                    "{ultrasonic.distance}",
                    "LINE DETECTION",
                    "SEE HOST LOG",
                ],
                [
                    "BATTERY / V",
                    "{power.voltage}",
                    "M1-M2 / A",
                    "{power.current.1}",
                ],
                [
                    "UPTIME / s",
                    "{system.uptime}",
                    "RSSI / dBm",
                    "{wifi.rssi}",
                ],
            ],
            refresh_interval_seconds=0.5,
            page_interval_seconds=3.0,
        )
        time.sleep(10.0)

        # 手动选页会暂停自动轮播，索引 1 表示第二页。
        lite.oled.show(page=1)
        time.sleep(2.0)
        # 恢复设备默认欢迎页，避免示例页面一直保留。
        lite.oled.show()

        print("OLED page example completed; the default page has been restored.")

except pm.lite.LiteError as exc:
    # 连接或 OLED 命令失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
