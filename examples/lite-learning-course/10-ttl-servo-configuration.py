"""通过 USB 使用 ``set_id()`` 修改 TTL 舵机 ID，并读回验证结果。
该操作会修改舵机配置；请断电接线，并确保总线上只连接一只待配置舵机。
"""

import pymotion as pm


TARGET_ID = 1  # 要写入这只 TTL 舵机的新 ID
CONFIRMATION = f"CONFIGURE-TTL-{TARGET_ID}"  # 防止误改舵机 ID 的确认文字


try:
    # 修改持久配置前要求输入完整确认文字，避免误运行程序。
    confirmation = input(
        "请确认设备已完全断电换线、总线上只接一只 TTL 舵机并已重新上电。\n"
        f"输入 {CONFIRMATION} 将它配置为 ID {TARGET_ID}："
    ).strip()
    if confirmation != CONFIRMATION:
        print("确认文本不匹配，未修改舵机配置。")
    else:
        # 设置 ID 是写操作，因此需要连接设备并取得控制权。
        with pm.lite.connect() as lite:
            with lite.control():
                # 总线上只能连接一只待配置舵机，否则无法确定要修改哪一只。
                result = lite.ttl_servo.set_id(new_id=TARGET_ID)

        # 成功返回表示 SDK 已经写入并重新读取确认新 ID。
        print(f"TTL servo ID: {result.old_id} -> {result.id}")
        print(f"Maximum angle: {result.max_angle} degrees")
        print("Configuration verified. Power off and label this servo before continuing.")

except pm.lite.LiteError as exc:
    # 自动识别、写入或读回验证失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
