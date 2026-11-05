"""通过 USB 使用 ``lite.output()`` 控制一路 3.3 V 数字输出，高电平保持约 2 秒后关闭。
该接口只适合 LED 或逻辑输入等小负载，不能直接驱动电机或舵机。
"""

import time

import pymotion as pm


OUTPUT = 3  # 可改为 1～6，对应板卡丝印 OUTPUT1～OUTPUT6


try:
    # 数字输出使用默认 USB 连接。
    with pm.lite.connect() as lite:
        # 将用户端口号转换为对应的 OUTPUT 端口对象。
        output = lite.output(OUTPUT)

        # 改变输出电平属于写操作，必须先取得设备控制权。
        with lite.control():
            print(f"OUTPUT{output.port} is HIGH for 2 seconds...")
            try:
                output.on()
                time.sleep(2.0)
            finally:
                # 即使等待期间发生异常或按下 Ctrl+C，也尽量恢复低电平。
                output.off()

        print(f"OUTPUT{output.port} is LOW.")
except pm.lite.LiteError as exc:
    # 连接、控制或输出设置失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
