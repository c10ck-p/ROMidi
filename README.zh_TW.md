# ROMidi

[English](README.md) | [简体中文](README.zh_CN.md) | **繁體中文**

[HuMidi](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer) 的社群分支 — 一款用於 Roblox 鋼琴遊戲的 MIDI 自動演奏工具，具備人性化播放、自動踏板時序和 88 鍵支援。

ROMidi 專注於 UI 打磨、國際化和主題客製化，同時保留所有原有功能。

---

## ROMidi 相較 HuMidi 的改進

| 功能 | 說明 |
|------|------|
| **多語言支援** | 內建簡體中文和繁體中文翻譯 |
| **跟隨系統語言** | 首次啟動時自動偵測作業系統語言 |
| **主題改進** | 基於 QSS 的主題引擎增強，顏色同步更出色 |
| **試聽修復** | 修復了停止試聽後無法重新啟動的問題 |
| **Bug 修復** | 翻譯查找正規化及其他細節改進 |

---

## 截圖

<img width="326" height="396" alt="ROMidi 播放頁" src="https://github.com/user-attachments/assets/c9d39ad9-0517-4ea6-acb3-da312868aaed" />
<img width="326" height="396" alt="ROMidi 視覺化頁" src="https://github.com/user-attachments/assets/dfe54071-70ba-4c80-b2a8-3c866f3f7cb1" />
<img width="326" height="396" alt="ROMidi 設定頁" src="https://github.com/user-attachments/17b5eac5-b194-4d77-af0e-f1d1c17e463a" />

## 快速開始

### 從原始碼執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動
python main.py
```

### 建立可執行檔

```bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." main.py
```

僅支援 `.mid` 檔案。鋼琴獨奏 MIDI 效果最佳，也支援混合樂器。

## 依賴

| 套件 | 用途 |
|------|------|
| [PyQt6](https://riverbankcomputing.com/software/pyqt/) | GUI 框架 |
| [mido](https://github.com/mido/mido) | MIDI 檔案解析 |
| [numpy](https://numpy.org/) | 音訊/數值處理 |
| [onnxruntime](https://github.com/microsoft/onnxruntime) | AI 踏板時序推論 |
| [pynput](https://github.com/moses-palmer/pynput) | 鍵盤/滑鼠模擬 |

具體版本約束見 `requirements.txt`。

## 授權

本專案基於 MIT 授權條款開源 —— 有關原始軟體的完整授權條款文字，請參閱 [HuMidi](./ui/LicenseTab.py) 授權條款項目。

原作者版權所有 (c) 2026 smyGitt — [HuMidi GitHub 倉庫](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer)