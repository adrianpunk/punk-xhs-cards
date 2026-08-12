# Punk XHS Cards

把人物照片或已有 IP 形象，和一篇带截图的 Markdown 长文，制作成一套可直接发布到小红书的竖版知识卡片。

这个 Codex Skill 不使用固定模板色。建立人物时可以直接指定主题色；没有指定时，它会从人物的服装或配件中提取一个候选色请你确认。同一套色彩会同时影响封面背景、标题、Mac 网页框和正文卡片。Punk 使用红色，只是 Punk 这个人物 profile 的结果。

## 它能做什么

- 从真人照片创建可复用的个人 IP，或登记用户已有的 IP 形象
- 生成并确认角色设定板、干净全身参考图和用户指定动作的卡片人物图
- 从人物形象提取主色，建立独立的卡片 profile
- 在建立人物时记录人物名称、封面作者名和可选主题色
- 解析 Markdown 的标题、正文结构、图片和教程步骤，不从文章提取作者
- 保留理解文章不可缺少的截图、图表、流程图与完成状态图
- 调用 Punk IP Article Illustrations，根据 Markdown 与人物 IP 生成一张 16:9 主题插图
- 用主题色背景、准确标题、4:3 Mac 网页框和签名体作者名合成 1080×1440 无页码封面
- 从 `01` 开始生成正文卡片，并自动检查图片遗漏、文字截断和人物比例
- 使用同一套 Python/Pillow 渲染器支持 macOS、Windows 和 Linux
- 生成一个推荐标题、三个备选标题、小红书正文和 6–10 个 tags

## 工作流

```text
上传人物照片或 IP 图
        ↓
确认人物名称、人物设定、卡片动作与主题色
        ↓
确认动作图、主题色和正文样稿
        ↓
上传 Markdown
        ↓
解析标题、正文结构与关键图
        ↓
确认 IP 主题插图与 Mac 网页框封面
        ↓
生成从 01 开始的内页、发布文案和 ZIP
```

整个流程有三个确认门：人物确认、卡片样式确认、封面确认。前一阶段没有确认时，Skill 不会提前拆文章或批量生成内页。

## 安装

### 方式一：克隆到 Codex Skills 目录

```bash
git clone https://github.com/adrianpunk/punk-xhs-cards.git
cp -R punk-xhs-cards/punk-xhs-cards ~/.codex/skills/
```

Windows PowerShell：

```powershell
git clone https://github.com/adrianpunk/punk-xhs-cards.git
Copy-Item -Recurse punk-xhs-cards\punk-xhs-cards "$HOME\.codex\skills\punk-xhs-cards"
```

安装后重新打开一个 Codex 任务，或重启 Codex，使新 Skill 出现在可用 Skills 列表中。

封面插图阶段依赖 `$punk-ip-article-illustrations`。请确认它也出现在当前 Codex 的可用 Skills 列表；如果尚未安装，需要先安装或复制 Punk IP Article Illustrations，再运行本工作流。

安装跨平台渲染依赖：

```bash
python3 -m pip install -r ~/.codex/skills/punk-xhs-cards/requirements.txt
```

Windows 使用：

```powershell
py -3 -m pip install -r "$HOME\.codex\skills\punk-xhs-cards\requirements.txt"
```

### 方式二：手动安装

下载仓库 ZIP，解压后把其中的 `punk-xhs-cards/` 目录复制到：

```text
~/.codex/skills/punk-xhs-cards/
```

## 使用

第一次使用时，可以直接对 Codex 说：

```text
请使用 $punk-xhs-cards。先根据我上传的照片建立个人 IP，
确认人物、卡片动作和视觉风格后，再把我提供的 Markdown 做成小红书知识卡片。
```

首次启动且还没有确认人物时，Skill 会显示：

```text
Hi，我是 Punk，欢迎使用「Punk XHS Cards」Skill。

我做这个 Skill，是想帮助多平台内容创作者更轻松地复用自己的优质内容。你可以把发布在 𝕏、微信公众号等平台的长文，转换成适合小红书阅读和发布的竖版知识卡片。

它会尽量保留原文的核心内容与关键图片，同时融入你的个人 IP 和专属视觉风格，让一篇好内容能够被更多平台看见。

请先上传一张清晰的人物照片，或一张已经完成的个人 IP 形象，并告诉我人物名称、希望人物在卡片里做什么动作，以及是否有指定主题色。这个人物名称会作为封面作者名；没有指定主题色时，我会从人物服装或配件中识别一个候选色请你确认。

动作可以是站立讲解、指向内容、拿着平板、在白板上书写，或坐着使用电脑。如果你还没想好，我会先给你 3 个适合知识卡片的动作建议。

接下来，我会帮你：
1. 建立个人 IP 形象，并请你确认人物身份与卡片动作；
2. 使用你指定的主题色，或从人物形象提取候选主色，生成卡片排版样稿；
3. 在样式确认后，请你上传 Markdown 长文；
4. 根据文章内容和你的 IP 生成主题插图，再排成主题色书封与 4:3 Mac 网页窗口，之后将正文和关键截图排成竖版知识卡片；
5. 最后提供适合小红书发布的标题、正文和话题标签。
```

如果已有个人 IP：

```text
请使用 $punk-xhs-cards，把这张现成 IP 图登记为我的人物形象。
卡片里希望人物站立讲解，并用右手指向左上方内容区。
确认样稿后，我会继续上传 Markdown。
```

人物和样式确认后，再上传 Markdown。封面作者已经在人物创建阶段确定；Markdown 不需要额外写作者标注，即使存在作者字段也不会覆盖人物 profile 中的作者名。

如果 Markdown 中有教程截图，请保留原始图片链接、相对路径和准确的 alt 文本。Skill 会先建立“步骤—截图—完成标志”映射；为保证可读性，它可以增加卡片数量，而不会为了凑固定页数删掉必要步骤图。

## 默认输出

```text
<article-slug>-小红书/
├── source.md
├── cover-illustration.png
├── assets/
│   └── article-images/
├── cards.json
├── publish-copy.md
├── output/
│   ├── cover.png
│   ├── card-01.png
│   └── ...
└── <article-slug>-小红书.zip
```

默认交付 1 张无页码封面和 9 张正文卡片。实际内页数量会根据文章内容和必要截图调整，避免重复内容凑页。

## 设计约束

- 输出尺寸为 1080×1440，封面主题插图源图为 16:9
- 封面不显示页码；正文从 `01` 开始编号
- 书名默认横排，长标题最多自然换成两行
- 顶部为暖白标题区，中间为 4:3 Mac 网页框，下方为签名体作者名
- 卡片人物动作由用户在确认 IP 时指定，并写入个人 profile；不会统一套用坐姿或电脑
- 人物始终等比例显示，不拉伸、不压扁、不裁头
- 封面背景、标题、Mac 网页框和内页使用同一个人物 profile 的色彩系统
- 每张关键图只使用一次，教程必备截图不得省略
- 原始照片、人物资产、文章和生成结果不写入 Skill 安装目录

## 运行要求

- Codex，且当前环境能够调用图像生成工具
- 已安装 `$punk-ip-article-illustrations` Skill；封面插图阶段不回退到无人物抽象 Hero 流程
- Python 3.10 或更新版本
- Pillow 10–12，可通过 Skill 内的 `requirements.txt` 安装
- 中文字体：macOS 使用苹方，Windows 使用微软雅黑，Linux 推荐 Noto Sans CJK

检查当前系统能否渲染：

```bash
python3 ~/.codex/skills/punk-xhs-cards/scripts/render_cards.py --check
```

Windows 使用：

```powershell
py -3 "$HOME\.codex\skills\punk-xhs-cards\scripts\render_cards.py" --check
```

没有 Punk IP Article Illustrations 或图像生成能力时，Skill 会明确指出缺少的依赖，或输出已经编译的封面插图提示词与保存计划，但不会假装图片已经生成。

## 仓库结构

```text
.
├── README.md
└── punk-xhs-cards/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```

`punk-xhs-cards/` 是可直接安装的 Skill 包；仓库根目录只放面向使用者的说明和项目级文件。

## 隐私说明

Skill 会把用户照片、人物 profile、文章和卡片输出保存在运行时目录，而不是 Skill 目录。提交或分享项目时，请继续排除 `.punk-ip-assets/`、`.xhs-ip-cards/` 和文章输出目录。

为兼容改名前已经确认的人物与卡片 Profile，Punk XHS Cards 继续读取 `.xhs-ip-cards/` 运行数据目录；升级后不需要重新建立人物。

图片生成过程仍会把用户提供的参考图交给当前宿主的图像生成服务处理；请根据你使用的平台和账号设置判断是否适合上传相应照片。

## 当前边界

- macOS、Windows 和 Linux 共用 Python/Pillow 渲染器；旧版 Swift/AppKit 文件只为兼容保留
- 精简 Linux 系统通常没有中文字体，需要先安装 Noto Sans CJK 或通过 `--font` 指定字体
- 中文标题、正文与教程型 Markdown 是当前主要优化方向
- 最终效果仍取决于输入照片质量、Markdown 结构和截图清晰度
