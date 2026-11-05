<div align="center">

<a href="README.md"><img src="https://img.shields.io/badge/English-24292f?style=for-the-badge" alt="English"></a>&nbsp;&nbsp;<a href="README_CN.md"><img src="https://img.shields.io/badge/中文-24292f?style=for-the-badge" alt="中文"></a>

<h1>PyMotion Lite</h1>

<p><strong>让 Python 不只停留在屏幕里。</strong></p>
<p>从代码到动作，从动作到反馈——一块面向机器人学习、原型验证与智能硬件项目的 Python 原生控制器。</p>

<p>
  <a href="https://pymotion.mintlify.site"><img src="https://img.shields.io/badge/在线使用手册-07C160?style=flat-square" alt="在线使用手册"></a>&nbsp;
  <img src="https://img.shields.io/badge/SDK-1.0.1-3B82F6?style=flat-square" alt="SDK 1.0.1">&nbsp;
  <img src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420?style=flat-square&logo=ubuntu&logoColor=white" alt="Ubuntu 24.04 LTS">&nbsp;
  <img src="https://img.shields.io/badge/Python-3.12-FFD43B?style=flat-square&logo=python&logoColor=1F2937" alt="Python 3.12">
</p>

</div>

PyMotion Lite 将直流电机、PWM 舵机、TTL 总线舵机、传感器、雷达、里程计、OLED 与设备状态统一到一套清晰的 `pm.lite` API 中。你可以先用 USB 完成稳定调试，再切换到 Wi-Fi 构建无线机器人；应用层代码保持同一种使用方式。

```mermaid
flowchart LR
    A[Python 程序] -->|USB / Wi-Fi| B[PyMotion Lite]
    B --> C[电机与舵机]
    B --> D[传感器与雷达]
    B --> E[里程计与 OLED]
    C --> F[真实动作]
    D --> G[实时数据]
    E --> G
    G --> A
```

## 为什么是 PyMotion Lite

| 特点 | 你可以获得什么 |
| --- | --- |
| Python 原生 | 公开 API 直接对应设备能力，不必先处理底层通信协议 |
| 控制与反馈一体 | 发出运动目标，同时读取编码器、实测转速、传感器、电源与设备状态 |
| USB / Wi-Fi 同一 API | 从桌面调试平滑切换到移动机器人和无线应用 |
| 实时能力 | 连续接收多源数据，并持续更新电机、舵机等执行器目标 |
| 安全进入正常流程 | Token 认证、控制权、命令有效期、主动停止与异常退出均有明确用法 |
| 离线安装 | SDK 与依赖从包内 wheel 安装到独立 Python 环境 |

## 运行环境

- Ubuntu 24.04 LTS，64 位 x86_64 / amd64。
- 使用系统 CPython 3.12 创建独立虚拟环境；安装 SDK 时不从网络下载 Python 包。
- 安装过程需要当前普通用户具备 `sudo` 权限，用于配置 USB 访问权限；不要直接以 root 用户运行安装脚本。
- 推荐安装 Visual Studio Code；没有 VS Code 时也可以使用 SDK 虚拟环境运行例程。
- USB 连接需要支持数据传输的 USB 线。

## 快速开始

先打开 [PyMotion Lite Ubuntu SDK 仓库](https://github.com/PyMotion-OS/PyMotion_Lite_Ubuntu)，点击 **Code → Download ZIP** 下载 SDK。

下载完成后，将 SDK 包完整解压到路径较短的目录，例如 `~/PyMotion_Lite_Ubuntu`。

### 1. 准备 SDK 目录

打开终端并进入 SDK 根目录：

```bash
cd ~/PyMotion_Lite_Ubuntu
```

目录中应至少包含：

```text
PyMotion_Lite_Ubuntu/
├── setup-ubuntu.sh
├── open-sdk-vscode.sh
├── run-sdk-python.sh
├── install-udev.sh
├── examples/
├── internal/
└── wheels/
```

请完整保留 SDK 目录结构，不要单独复制安装脚本，也不要移动、删除或修改 `internal`、`wheels` 和 `examples`。

### 2. 安装 SDK

以当前普通用户运行：

```bash
bash ./setup-ubuntu.sh
```

脚本会校验 SDK 完整性，创建独立环境，从本地 wheel 安装 SDK 与依赖，配置 udev 规则，并准备可编辑的示例工作区。默认 SDK 环境位于：

```text
~/.local/share/pymotion-lite/venv-ubuntu
```

安装结束后，请按终端提示重新插拔 PyMotion Lite 的 USB 线。如果脚本将当前用户加入了 `dialout` 组，还需要完整退出 Ubuntu 登录会话并重新登录一次。

### 3. 打开 SDK 工作区

回到 SDK 根目录后运行：

```bash
bash ./open-sdk-vscode.sh
```

启动器会检查已安装的 SDK 环境，把示例复制到当前用户的可编辑工作区，绑定正确的 Python 解释器，并使用新窗口打开 VS Code。

如果没有安装 VS Code，可以直接使用 SDK 环境中的 Python：

```bash
~/.local/share/pymotion-lite/venv-ubuntu/bin/python \
  ./examples/quick-start/01-pymotion-lite.py
```

### 4. 连接你的 PyMotion Lite 板卡

连接板卡前，请先接好支持数据传输的 USB 线并确认板卡已经正常供电。然后在打开的 VS Code 终端中设置板卡当前 Token：

```bash
export PYMOTION_AUTH_TOKEN="设备的 Token"
```

完成 USB 连接和 Token 设置后，运行只读连接例程：

```bash
python ./examples/quick-start/02-connection.py
```

该例程只会建立 USB 连接、读取板卡状态并关闭连接，不会驱动电机或舵机。运行成功后，终端会显示类似信息：

```text
PyMotion Lite SDK: 1.0.1
Device ID: ...
Transport: usb
State: ...
Status age: ... s
```

看到设备 ID、`Transport: usb` 和板卡状态后，说明 SDK 已经能够正常访问 PyMotion Lite。接下来可以继续运行 `examples/quick-start` 中的其他例程，或按照 `examples/lite-learning-course` 的编号顺序学习完整功能。

如果不使用 VS Code，请在 SDK 根目录中通过独立环境运行同一个例程：

```bash
export PYMOTION_AUTH_TOKEN="设备的 Token"
~/.local/share/pymotion-lite/venv-ubuntu/bin/python \
  ./examples/quick-start/02-connection.py
```

## 从这里继续

| 我想做什么 | 从这里开始 |
| --- | --- |
| 认识 SDK 并完成首次连接 | [Quick Start](examples/quick-start) |
| 学习电机、舵机、传感器与实时控制 | [Lite Learning Course](examples/lite-learning-course) |
| 检查 SDK 环境 | `~/.local/share/pymotion-lite/venv-ubuntu/bin/pymotion doctor` |
| 查询完整功能、API 与安全约束 | [在线使用手册](https://pymotion.mintlify.site) |

> [!CAUTION]
> 电机和舵机动作前，请在断电状态下完成接线，使用符合要求的外部供电，架空车轮并清空机构运动范围。软件停止与通信超时保护不能替代可立即操作的物理断电措施。

