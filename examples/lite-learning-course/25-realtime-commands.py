"""通过 Wi-Fi 实时更新 M1、M2 的开环目标，使其平滑加速后停止。
``RUN_MOTORS`` 默认关闭；运行前请架空车轮、确认方向并了解 ``valid_for`` 超时停止机制。
"""

import time

import pymotion as pm


DEVICE_ID = None  # 单设备保持 None；多设备时填写目标设备 ID
TRANSPORT = "wifi"  # 连接方式："wifi" 或 "usb"
RUN_MOTORS = False  # 确认车轮已架空且环境安全后改为 True

M1_DIRECTION = 1  # M1 安装方向：正常为 1，反向时改为 -1
M2_DIRECTION = 1  # M2 安装方向：正常为 1，反向时改为 -1
PEAK_SPEED = 30  # 加减速过程达到的最高速度百分比
RAMP_DURATION = 5.0  # 从静止加速到最高速度所用时间（秒）

RAMP_STEPS = PEAK_SPEED  # 每提高 1% 速度算作一个加速步骤
# 每 1% 更新一次目标；本例由调用间隔决定为约 6 Hz，与传感器 frequency 档位无关。
# valid_for=0.5 秒可覆盖短暂 Wi-Fi 抖动。
COMMAND_INTERVAL = RAMP_DURATION / RAMP_STEPS  # 相邻两次实时命令的间隔（秒）


def get_motor_pwms(step):
    """计算当前步骤中 M1、M2 应使用的速度。"""
    if step <= RAMP_STEPS:
        speed = step
    else:
        speed = 2 * RAMP_STEPS - step

    return {
        1: M1_DIRECTION * speed,
        2: M2_DIRECTION * speed,
    }


def main():
    """发送一次加速、减速实时命令序列。"""

    if not RUN_MOTORS:
        print("Real-time motor commands are disabled.")
        print("Raise the wheels, clear the surroundings, then set RUN_MOTORS = True.")
        return

    with pm.lite.connect(DEVICE_ID, transport=TRANSPORT, timeout=15.0) as lite:
        with lite.control(timeout=5.0):
            with lite.realtime.open(
                command_targets={"motor_pwms": [1, 2]},
            ) as session:
                motor_commands = session.commands.motor_pwms

                print("Starting two-motor speed profile.")
                try:
                    for step in range(2 * RAMP_STEPS + 1):
                        pwms = get_motor_pwms(step)

                        # 命令采用“最新值优先”；链路来不及发送时旧的待发值会被替换。
                        # 0.5 秒内没有后续命令时，设备使目标失效并停止对应电机。
                        motor_commands.write(pwms, valid_for=0.5)
                        print(f"M1={pwms[1]}%, M2={pwms[2]}%")

                        if step < 2 * RAMP_STEPS:
                            time.sleep(COMMAND_INTERVAL)
                finally:
                    # 最后一次 0% write() 后不再等待一个提交间隔，因此它可能仍在
                    # SDK 的待发位置。stop() 会丢弃这条冗余的 0% 目标，改发专用停止命令，
                    # 所以统计中出现 replaced=1 是正常安全收尾，不表示 USB/Wi-Fi 丢包。
                    motor_commands.stop()
                    print("Motors stopped.")

                stats = motor_commands.stats()
                print(f"Commands sent: {stats.sent}")
                # replaced 还包含“待发普通目标被显式 stop() 替代”，不只表示写入过快。
                print(f"Commands replaced: {stats.replaced}")


try:
    main()
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
