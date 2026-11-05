"""通过 USB 使用 ``lite.imu()`` 读取 MPU6050 的加速度、角速度和横滚/俯仰角。
本例只读取数据，不会控制执行器；MPU6050 不提供航向角。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 本例只读数据，不需要取得设备控制权。
        imu = lite.imu(max_age=0.5)

        # 数据无效或过旧时，数值字段为 None，不会用 0 冒充真实测量值。
        acceleration = imu.acceleration
        if acceleration is not None:
            print("Acceleration (mm/s^2):")
            print(f"  x: {acceleration.x:.2f}")
            print(f"  y: {acceleration.y:.2f}")
            print(f"  z: {acceleration.z:.2f}")
        else:
            print("Acceleration: unavailable")

        # 角速度是绕 X、Y、Z 三个轴的旋转速度。
        angular_velocity = imu.angular_velocity
        if angular_velocity is not None:
            print("Angular velocity (rad/s):")
            print(f"  x: {angular_velocity.x:.4f}")
            print(f"  y: {angular_velocity.y:.4f}")
            print(f"  z: {angular_velocity.z:.4f}")
        else:
            print("Angular velocity: unavailable")

        # orientation 提供 roll 和 pitch，单位都是度。
        orientation = imu.orientation
        if orientation is not None:
            print("Orientation (degrees):")
            print(f"  roll: {orientation.roll:.2f}")
            print(f"  pitch: {orientation.pitch:.2f}")
        else:
            print("Orientation: unavailable")

except pm.lite.LiteError as exc:
    # 连接或 IMU 读取失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
