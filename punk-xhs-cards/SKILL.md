---
name: punk-xhs-cards
description: Punk XHS Cards：从用户照片或已有 IP 图建立并确认可复用个人 IP、作者名与主题色，再把带文字、截图、图表或流程图的 Markdown 长文制作成“主题色书封＋16:9 macOS 窗口 IP 插图＋从 01 开始编号的正文知识卡片”，保留理解文章不可缺少的关键图，同时生成小红书标题、正文和 tags。用户提到“上传照片生成个人 IP”“上传自己的 IP 形象”“把 Markdown 做成小红书图”“保留文章关键图”“先做封面再做内页”“个人 IP 知识卡片”或点名 $punk-xhs-cards 时使用。
---

# Punk XHS Cards

按三个确认门依次执行：人物确认、卡片样式确认、封面确认。未通过前一门时不得进入后一阶段，也不得提前拆分 Markdown。

## 每次开始

1. 读取 `references/character-package.md`，解析当前 `.punk-ip-assets/` 人物状态。
2. 读取 `references/profile-workflow.md`，解析当前 `.xhs-ip-cards/` card profile 状态。
3. 根据输入进入人物创建、人物修订、人物确认、样式创建、样式修订、样式确认、Markdown 解析、封面制作或内页生产。
4. 不把真人照片、生成角色、用户文章或本次封面插图写入 Skill 安装目录。

## 首次使用

没有已确认人物时，只发送以下引导，不读取文章：

```text
Hi，我是 Punk，欢迎使用「Punk XHS Cards」Skill。

我做这个 Skill，是想帮助多平台内容创作者更轻松地复用自己的优质内容。你可以把发布在 𝕏、微信公众号等平台的长文，转换成适合小红书阅读和发布的竖版知识卡片。

它会尽量保留原文的核心内容与关键图片，同时融入你的个人 IP 和专属视觉风格，让一篇好内容能够被更多平台看见。

开始前，请先准备并告诉我这 4 项：
1. 一张清晰的人物照片，或一张已经完成的个人 IP 形象；
2. 人物名称或昵称，它会直接作为封面作者名；
3. 一个主题色，最好给出 Hex 色值或颜色参考；没有的话，我会从人物服装或配件中提取 1 个候选色请你确认；
4. 希望人物在卡片里做什么动作。

动作可以是站立讲解、指向内容、拿着平板、在白板上书写，或坐着使用电脑。如果你还没想好动作或主题色，我会先给出候选方案，但会等你确认后才继续。

接下来，我会帮你：
1. 建立个人 IP 形象，并请你确认人物身份与卡片动作；
2. 使用你指定的主题色，或从人物形象提取候选主色，生成卡片排版样稿；
3. 在样式确认后，请你上传 Markdown 长文；
4. 根据文章内容和你的 IP 生成主题插图，再排成主题色书封与 16:9 macOS 窗口，之后将正文和关键截图排成竖版知识卡片；
5. 最后提供适合小红书发布的标题、正文和话题标签。
```

## 阶段路由

- 上传真人照片且没有确认人物：按“创建人物”生成个人 IP。
- 上传现成 IP 图且没有确认人物：按“登记现成 IP”建立人物资产。
- 当前人物为 `draft`：只修订或确认人物，同时询问并记录希望用于卡片的动作。
- 人物已确认但尚未明确卡片动作：给出 3 个适合知识卡片的动作建议并等待用户选择，不生成样稿。
- 人物和动作已确认但没有对应 card profile：创建动作图、配色和正文样稿。
- 已有匹配的 `confirmed` card profile：沿用其中的 `card_action`；只有用户要求修改时才重新生成动作图。
- card profile 为 `draft`：只修订或确认样式。
- card profile 已确认并收到 Markdown：解析标题与图片、拟定标题、调用 `$punk-ip-article-illustrations` 生成 IP 主题插图，渲染 16:9 macOS 窗口封面并停下等待封面确认。
- 用户确认封面：制作内页、发布文案、校验和 ZIP。

## 创建人物

完整读取：

- `references/ip-builder.md`
- `references/character-package.md`
- `references/tool-workflow.md`

### 从真人照片生成

1. 以用户照片为唯一身份来源，提炼可观察的脸、发型、体型、服装和配件。
2. 生成角色设定板和干净全身参考图；保持自然头身比例。
3. 写 `character-spec.md`，不得推断敏感属性。
4. 用 `scripts/character_registry.py register` 注册为 `draft`；用户提供的人物名称同时写入 `author_name`。用户指定主题色时用 `--theme-color '#RRGGBB'` 写入人物 manifest。
5. 展示设定板和干净参考图，询问人物是否确认，并确认卡片动作和主题色；用户已经指定时复述动作与色值。

### 登记现成 IP

1. 把用户上传的 IP 图视为身份参考，不重新设计人物。
2. 若不是干净全身图，生成一张同身份、同服装、同配件的干净全身参考图。
3. 生成四视图设定板并写 `character-spec.md`。
4. 注册为 `draft`，展示后等待人物确认，同时确认希望人物在卡片里做什么动作和是否指定主题色。

人物草稿不得用于封面或卡片。只有用户明确说“确认”“定稿”“就用这个”时运行确认命令。人物确认后仍须取得明确的卡片动作；用户把动作交给你决定时，先给出 3 个简短候选并标出推荐项。

## 创建卡片样式

完整读取：

- `references/profile-workflow.md`
- `references/theme-system.md`
- `references/tool-workflow.md`
- 当前确认人物的 `character-spec.md`

1. 按用户确认的 `card_action` 生成卡片专用透明人物图，例如站立讲解、指向内容、拿着平板、在白板上书写或坐着使用电脑。默认让人物的身体、视线或手势朝向左上内容区，但不得改变用户指定动作的核心含义。
2. 不自动套用“盘腿使用电脑”。只有用户明确选择该动作，或当前已确认 profile 原本就使用该动作时才沿用。
3. 保持身份、服装、配件和自然比例；禁止拉伸、压扁和裁头。
4. 用户指定主题色时把它作为最高优先级；否则从人物服装或配件提取稳定强调色。运行 `scripts/derive_palette.py` 生成 `theme.json`，并展示色值让用户随样稿一起确认。
5. 该 profile 强调色必须同时驱动整张封面背景、标题区、Mac 窗口视觉细节、内页编号、分区线和重点框。不得把 Punk 的红色写成所有用户的默认值。
6. 使用 `--author-name` 写入当前人物的 `author_name`，使用 `--action` 写入用户确认的动作，注册 `draft` card profile，并渲染一张正文样稿。
7. 展示动作图、主题色和正文样稿，只询问确认还是修改。
8. 用户明确确认后再激活 profile。

## 读取 Markdown

封面阶段完整读取：

- `references/cover-workflow.md`
- `references/card-data-schema.md`
- `references/markdown-images.md`
- `references/platform-rendering.md`
- 当前 profile 的 `theme.json`、`profile.json` 和 `character-spec.md`

先运行：

```bash
python3 scripts/parse_markdown.py <source.md>
```

规则：

1. 原始标题取 YAML `title:`；没有则取第一个一级标题。
2. 作者名只读取当前已确认 profile 的 `author_name`。不得扫描、提取或采用 Markdown 中的 `author:`、`作者：` 或“关于作者”内容作为封面作者。
3. 检查解析结果的 `images` 清单，并结合全文和图片内容标记关键图；解析器的 `selection_hint` 只是提示，不能代替语义判断。
4. 若文章包含连续操作步骤、命令和界面截图，启用教程模式：先建立“步骤—截图—完成标志”映射，必备步骤图不得省略。
5. 完整理解文章后，拟定一个准确、有搜索性的封面标题；不得改变核心含义或制造原文没有的承诺。
6. 向用户说明原始标题、建议封面标题、当前人物作者名和关键图数量；未被要求时直接采用建议标题继续封面草稿。

## 生成主题色 16:9 macOS 窗口 IP 封面

必须使用已安装的 `$punk-ip-article-illustrations` Skill 生成封面中间的主题插图。它负责根据 Markdown 提炼一个认知锚点、保持 IP 身份和生成插图；`render_cards.py` 负责主题色背景、准确短标题、16:9 macOS 窗口和粗体衬线作者名。若该 Skill 不可用，明确说明缺少依赖并停止在封面阶段。

1. 完整读取 Markdown，选择一个能代表全文的认知锚点，并按 `$punk-ip-article-illustrations` 的“核心动作”或“流程拆解”规则生成一张 16:9 IP 主题插图。插图不生成封面大标题、作者、Logo 或页码。
2. 只使用当前已确认人物的身份参考和用户确认动作；人物必须等比例，保持脸、服装、配件和自然比例。封面插图可按文章主题改变场景职责，但不得改变人物身份。
3. 从 profile 读取 `author_name`、`accent` 和 `deepAccent`。整张 1080×1440 封面背景使用 `accent`；顶部不放标题框，只用暖白或与背景有充分对比的圆润字体居中排一个简短封面标题；红色只属于 Punk profile。
4. 中间固定放一个 960×620 的精细 macOS 窗口：上方为 62 px 工具栏、三个系统圆点、细边线和柔和投影；工具栏下方是完整 16:9 图片区，不再使用 4:3 网页画布。插图按 aspect-fill 裁切，不拉伸人物。
5. 作者位于窗口下方，只显示 profile 的 `author_name`。使用粗体衬线字体居中排版；不显示 `AUTHOR`、“作者”、横线、签名笔触或倾斜变形。作者只来自 profile，不从 Markdown 复制。
6. 建立 `cards.json`：顶层 `cover` 只保存 `title` 和 `illustration` 路径；`cards` 只保存内页。不得写 `cover.author`。
7. 运行 `scripts/render_cards.py` 合成最终封面。封面不显示页码、总页数、栏目名、品牌名或账号。
8. 展示主题插图、最终封面、书名、profile 作者名和主题色值，只询问确认还是修改。封面未确认时不得拆分内页。

## 制作内页

封面确认后完整读取 `references/content-workflow.md`、`references/markdown-images.md`、`references/card-data-schema.md` 和 `references/platform-rendering.md`。

1. 默认交付 10 张：1 张无页码封面＋9 张内页；文章需要时可调整内页数量，不重复内容凑页。
2. 内页从 `01` 开始，页码总数只计算内页，例如 `01 / 09`；封面不参与页码。
3. 以文字准确还原为主，允许压缩重复表达，不新增数据、经历、结论或承诺。
4. 对已选关键图运行 `scripts/collect_markdown_images.py`，复制或下载到 `assets/article-images/`。每张图只使用一次，默认每页最多一张；细节密集的图可单独成页。
5. 在 `cards.json` 使用 `image` block 放入关键图，并只使用原文 alt、相邻图注或正文语境撰写图注，不虚构图片含义。
6. 教程模式按原文顺序编排步骤图。凡用于确认“点哪里、输入什么、选择什么、完成后看到什么”的截图必须出现；为保持可读性可以增加内页，不能为了固定 10 张删图或压缩到看不清。
7. 首次渲染先按 `references/platform-rendering.md` 运行 `scripts/render_cards.py --check`，确认 Pillow 和中文字体可用。不得因为当前系统不是 macOS 而跳过渲染。
8. 生成 `cards.json` 后使用跨平台 Python 渲染器：

   ```bash
   python3 scripts/render_cards.py <cards.json绝对路径> <output目录绝对路径> <profile.json绝对路径>
   ```

   Windows 使用 `py -3 scripts\render_cards.py ...` 或 `scripts\render_cards.ps1`；macOS 与 Linux 也可使用 `scripts/render_cards.sh`。样稿追加 `--allow-draft`。

9. 逐张检查截断、重叠、步骤顺序、关键图可读性、主题配色和人物比例。
10. 生成 `publish-copy.md`：一个推荐标题、三个备选标题、一段正文和 6–10 个 tags。
11. 运行 `scripts/validate_output.py`；它会检查已收集的关键图是否都进入卡片。通过后再把 `cover.png` 与 `card-01.png ...` 一起打 ZIP。

## 输出结构

```text
<article-slug>-小红书/
├── source.md
├── cover-illustration.png
├── assets/
│   └── article-images/
│       ├── image-01.png ...
│       └── manifest.json
├── cards.json
├── publish-copy.md
├── output/
│   ├── cover.png
│   ├── card-01.png ... card-09.png
└── <article-slug>-小红书.zip
```

## 固定质量要求

- 所有图片 1080×1440；封面主题插图源图为 16:9，嵌入精细的 16:9 macOS 窗口。
- 在 macOS、Windows 和 Linux 上优先使用同一个 `render_cards.py`，不得维护三套不同版式。
- 人物每张只出现一次，必须等比例、不裁头、不改变脸。
- 封面背景、标题、macOS 窗口细节和内页必须使用当前人物 profile 的同一主色系统；Punk 使用红色只是 Punk profile 的结果，不是通用模板色。
- 封面不计页码；内页从 01 开始。
- 封面不显示账号；内页账号来自 profile，没有则省略。
- 标题来自 Markdown 内容；作者只来自人物创建阶段保存的 `author_name`。
- Markdown 中影响理解、步骤、证据或结果的关键图必须展示；装饰图、头像、重复封面和无关 Logo 不进入内页。
- 教程中的操作截图与检查点截图是内容，不是装饰；缺少任意必备步骤图时不得宣布完成。
- 原始照片默认不复制进文章输出、不提交 GitHub、不公开上传。
- 没有 `$punk-ip-article-illustrations` 或图像生成能力时，输出缺少的依赖或已编译提示词与保存计划，明确说明封面尚未完成。
