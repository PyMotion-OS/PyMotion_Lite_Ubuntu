"""通过 USB 读取 LD14P 雷达的最新 12 点局部帧和一圈完整扫描。
本例只读取数据，并输出转速、角度和距离摘要。
"""

import pymotion as pm


try:
    # 雷达数据量较大，本课程显式选择 USB 链路。
    with pm.lite.connect(transport="usb") as lite:
        # frame 适合低延迟观察局部数据；每帧固定包含一小段角度范围。
        frame = lite.lidar.frame(max_age=0.5)

        print("\nLiDAR frame")
        print(f"Sequence: {frame.sequence}")
        print(f"Point count: {len(frame.points)}")

        # 没有有效点时 points 为空列表，因此读取第一个点前先判断。
        if frame.points:
            point = frame.points[0]
            print("First point in the frame:")
            print(f"  angle: {point.angle:.2f} degrees")
            print(f"  distance: {point.distance} mm")
            print(f"  confidence: {point.confidence}")

        # scan 会把连续帧拼成一圈，适合绘图、避障地图和点云处理。
        scan = lite.lidar.scan()

        print("\nLiDAR scan")
        print(f"Sequence: {scan.sequence}")
        print(f"Point count: {len(scan.points)}")
        print(f"Frame count: {scan.frame_count}")

        # 这里只打印前五个点，避免完整一圈数据刷满终端。
        if scan.points:
            print("First five points in the scan:")
            for point in scan.points[:5]:
                print(
                    f"  angle={point.angle:.2f} degrees, "
                    f"distance={point.distance} mm, "
                    f"confidence={point.confidence}"
                )

except pm.lite.LiteError as exc:
    # 连接、雷达帧或完整扫描读取失败时显示 SDK 错误。
    print(f"PyMotion Lite [{type(exc).__name__}]: {exc}")
