# 跨平台渲染

正式渲染器为 `scripts/render_cards.py`，使用 Pillow，在 macOS、Windows 和 Linux 上读取同一份 `cards.json`、`profile.json` 与 `theme.json`，输出一致的 1080×1440 PNG。

## 首次检查

在渲染前运行：

```bash
python3 scripts/render_cards.py --check
```

Windows 可使用：

```powershell
py -3 scripts\render_cards.py --check
```

如果缺少 Pillow，在 Skill 目录执行：

```bash
python3 -m pip install -r requirements.txt
```

Windows 对应命令：

```powershell
py -3 -m pip install -r requirements.txt
```

只把依赖安装到当前用户环境或项目虚拟环境；不要修改系统 Python。

## 中文字体

渲染器会自动查找：

- macOS：PingFang SC；
- Windows：Microsoft YaHei；
- Linux：Noto Sans CJK、Noto Sans SC、Source Han Sans SC 或文泉驿正黑。

Linux 没有中文字体时，先使用系统包管理器安装 Noto Sans CJK。需要 `sudo` 时先取得用户同意。例如：

```bash
sudo apt install fonts-noto-cjk
```

无法安装系统字体时，下载一份合法授权的中文字体，并传入：

```bash
python3 scripts/render_cards.py --check --font /path/to/chinese-font.otf
```

正式渲染时同样追加 `--font`。也可设置环境变量 `XHS_IP_CARDS_FONT`；等宽字体可通过 `--mono-font` 或 `XHS_IP_CARDS_MONO_FONT` 指定。

## 正式渲染

通用 Python 命令：

```bash
python3 scripts/render_cards.py <cards.json> <output-dir> <profile.json>
```

macOS 与 Linux 可使用包装脚本：

```bash
scripts/render_cards.sh <cards.json> <output-dir> <profile.json>
```

Windows PowerShell 可使用：

```powershell
.\scripts\render_cards.ps1 <cards.json> <output-dir> <profile.json>
```

渲染待确认样稿时，Python 与 Bash 命令追加 `--allow-draft`；PowerShell 使用 `-AllowDraft`。

## 失败处理

- 报告 `Pillow is required`：安装 `requirements.txt`。
- 报告 `No Chinese font found`：安装中文字体或传入 `--font`。
- 报告内容溢出：重新拆分该页 blocks，不缩小正文逃避检查。
- 报告图片缺失：把 Markdown 图片收集到文章目录，并修正 `cards.json` 的相对路径。
- 不因当前系统缺依赖而改回只支持 macOS 的 Swift 流程；先完成依赖或字体设置。

`render_cards.swift` 只作为旧版 macOS 实现保留，不是默认渲染路径。
