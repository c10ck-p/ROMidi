# ROMidi

[English](README.md) | **简体中文** | [繁體中文](README.zh_TW.md)

[HuMidi](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer) 的社区分支 — 一款用于 Roblox 钢琴游戏的 MIDI 自动演奏工具，具备人性化播放、自动踏板时序和 88 键支持。

ROMidi 专注于 UI 打磨、国际化和主题定制，同时保留所有原有功能。

---

## ROMidi 相较 HuMidi 的改进

| 功能 | 说明 |
|------|------|
| **多语言支持** | 内置简体中文和繁体中文翻译 |
| **跟随系统语言** | 首次启动时自动检测操作系统语言 |
| **主题改进** | 基于 QSS 的主题引擎增强，颜色同步更出色 |
| **试听修复** | 修复了停止试听后无法重新启动的问题 |
| **Bug 修复** | 翻译查找规范化及其他细节改进 |

---

## 截图

<img width="326" height="396" alt="ROMidi 播放页" src="https://github.com/user-attachments/assets/c9d39ad9-0517-4ea6-acb3-da312868aaed" />
<img width="326" height="396" alt="ROMidi 可视化页" src="https://github.com/user-attachments/assets/dfe54071-70ba-4c80-b2a8-3c866f3f7cb1" />
<img width="326" height="396" alt="ROMidi 设置页" src="https://github.com/user-attachments/assets/17b5eac5-b194-4d77-af0e-f1d1c17e463a" />

## 快速开始

### 从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

### 构建可执行文件

```bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." main.py
```

仅支持 `.mid` 文件。钢琴独奏 MIDI 效果最佳，也支持混合乐器。

## 依赖

| 包 | 用途 |
|----|------|
| [PyQt6](https://riverbankcomputing.com/software/pyqt/) | GUI 框架 |
| [mido](https://github.com/mido/mido) | MIDI 文件解析 |
| [numpy](https://numpy.org/) | 音频/数值处理 |
| [onnxruntime](https://github.com/microsoft/onnxruntime) | AI 踏板时序推理 |
| [pynput](https://github.com/moses-palmer/pynput) | 键盘/鼠标模拟 |

具体版本约束见 `requirements.txt`。

## 许可证

本项目基于 MIT 许可证开源 —— 有关原始软件的完整许可证文本，请参阅 [HuMidi](./ui/LicenseTab.py) 许可证条目。

原作者版权所有 (c) 2026 smyGitt — [HuMidi GitHub 仓库](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer)