---
name: xhs-ip-cards
description: 从用户照片或已有 IP 图建立并确认可复用个人 IP，再把带文字、截图、图表或流程图的 Markdown 长文制作成“无页码书封面 Hero 图＋从 01 开始编号的正文知识卡片”，保留理解文章不可缺少的关键图，同时生成小红书标题、正文和 tags。用户提到“上传照片生成个人 IP”“上传自己的 IP 形象”“把 Markdown 做成小红书图”“保留文章关键图”“先做封面再做内页”“个人 IP 知识卡片”或点名 $xhs-ip-cards 时使用。
---

# 小红书个人 IP 书封知识卡片

按三个确认门依次执行：人物确认、卡片样式确认、封面确认。未通过前一门时不得进入后一阶段，也不得提前拆分 Markdown。

## 每次开始

1. 读取 `references/character-package.md`，解析当前 `.punk-ip-assets/` 人物状态。
2. 读取 `references/profile-workflow.md`，解析当前 `.xhs-ip-cards/` card profile 状态。
3. 根据输入进入人物创建、人物修订、人物确认、样式创建、样式修订、样式确认、Markdown 解析、封面制作或内页生产。
4. 不把真人照片、生成角色、用户文章或本次 Hero 图写入 Skill 安装目录。

## 首次使用

没有已确认人物时，只发送以下引导，不读取文章：

```text
请先上传一张清晰的人物照片，或一张已经完成的个人 IP 形象，并告诉我角色名称或昵称。

我会先建立人物资产并请你确认；确认后再创建小红书专用坐姿、配色和正文样稿。最后你再上传 Markdown，我会先做无页码封面，再从 01 开始制作内页。
```

## 阶段路由

- 上传真人照片且没有确认人物：按“创建人物”生成个人 IP。
- 上传现成 IP 图且没有确认人物：按“登记现成 IP”建立人物资产。
- 当前人物为 `draft`：只修订或确认人物。
- 人物已确认但没有对应 card profile：创建坐姿、配色和正文样稿。
- card profile 为 `draft`：只修订或确认样式。
- card profile 已确认并收到 Markdown：解析元数据、拟定标题、生成 Hero、渲染封面并停下等待封面确认。
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
4. 用 `scripts/character_registry.py register` 注册为 `draft`。
5. 展示设定板和干净参考图，只询问确认还是修改。

### 登记现成 IP

1. 把用户上传的 IP 图视为身份参考，不重新设计人物。
2. 若不是干净全身图，生成一张同身份、同服装、同配件的干净全身参考图。
3. 生成四视图设定板并写 `character-spec.md`。
4. 注册为 `draft`，展示后等待确认。

人物草稿不得用于封面或卡片。只有用户明确说“确认”“定稿”“就用这个”时运行确认命令。

## 创建卡片样式

完整读取：

- `references/profile-workflow.md`
- `references/theme-system.md`
- `references/tool-workflow.md`
- 当前确认人物的 `character-spec.md`

1. 生成卡片专用透明坐姿：人物盘腿使用电脑，身体和视线朝左上内容区。
2. 保持身份、服装、配件和自然比例；禁止拉伸、压扁和裁头。
3. 从人物服装或配件提取稳定强调色，运行 `scripts/derive_palette.py` 生成 `theme.json`。
4. 该 profile 强调色必须同时驱动封面书脊与下部色块、分区线、内页编号与重点框，以及 Hero 中唯一的彩色玻璃/材质。不得把 Punk 的红色写成所有用户的默认值。
5. 注册 `draft` card profile，并渲染一张正文样稿。
6. 展示坐姿、主题色和正文样稿，只询问确认还是修改。
7. 用户明确确认后再激活 profile。

## 读取 Markdown

封面阶段完整读取：

- `references/cover-workflow.md`
- `references/hero-image-prompt.md`
- `references/card-data-schema.md`
- `references/markdown-images.md`
- 当前 profile 的 `theme.json`、`profile.json` 和 `character-spec.md`

先运行：

```bash
python3 scripts/parse_markdown.py <source.md>
```

规则：

1. 原始标题取 YAML `title:`；没有则取第一个一级标题。
2. 作者优先取 Markdown 靠近文末的独立标注 `author:`、`Author:` 或 `作者：`；兼容文末“关于作者/作者简介”小节的首个名字。
3. 找不到作者时询问用户，不从人物名、账号或文件名推断。
4. 作者标注只用于封面，不进入内页正文。
5. 检查解析结果的 `images` 清单，并结合全文和图片内容标记关键图；解析器的 `selection_hint` 只是提示，不能代替语义判断。
6. 若文章包含连续操作步骤、命令和界面截图，启用教程模式：先建立“步骤—截图—完成标志”映射，必备步骤图不得省略。
7. 完整理解文章后，拟定一个准确、有搜索性的封面标题；不得改变核心含义或制造原文没有的承诺。
8. 向用户说明原始标题、建议封面标题、识别到的作者和关键图数量；未被要求时直接采用建议标题继续封面草稿。

## 生成 Hero 与书封面

不要调用 `punk-cover`。直接把 `references/hero-image-prompt.md` 填成完整图像生成提示词并调用可用的图像生成工具。

1. 用文章主题填写视觉关系、动作和结果。
2. 用 profile 强调色填写唯一彩色玻璃/材质；不要固定使用 Skill 作者的红色。Punk 示例使用低饱和砖红和酒红。
3. 生成一张 16:9 横版纯图 Hero：无文字、无数字、无 Logo、无水印、无人物。
4. 检查 Hero 是否只讲一个视觉故事，并保存到文章输出目录。
5. 建立新格式 `cards.json`：顶层 `cover` 保存标题、作者和 Hero 路径；`cards` 只保存内页。
6. 渲染封面。封面固定要求：
   - 1080×1440；
   - 不显示左上栏目、右上页码或任何封面页码；
   - 顶部为 16:9 Hero；
   - 中部为完整书名和作者，标题默认横排，过长时最多自然换成两行；
   - 白色书名区与下部强调色之间使用明显的不规则切角：白色左侧向下延伸，右侧提前进入强调色，以单一大斜面连接；禁止退化成整齐的水平矩形分区；
   - 下部为深强调色书封区域，账号位于左下并使用强调字形；
   - 不显示品牌名；
   - 人物固定整页右下角，aspect-fit 等比例显示。
7. 展示 Hero 和完整封面，只询问确认还是修改。封面未确认时不得拆分内页。

## 制作内页

封面确认后完整读取 `references/content-workflow.md`、`references/markdown-images.md` 和 `references/card-data-schema.md`。

1. 默认交付 10 张：1 张无页码封面＋9 张内页；文章需要时可调整内页数量，不重复内容凑页。
2. 内页从 `01` 开始，页码总数只计算内页，例如 `01 / 09`；封面不参与页码。
3. 以文字准确还原为主，允许压缩重复表达，不新增数据、经历、结论或承诺。
4. 对已选关键图运行 `scripts/collect_markdown_images.py`，复制或下载到 `assets/article-images/`。每张图只使用一次，默认每页最多一张；细节密集的图可单独成页。
5. 在 `cards.json` 使用 `image` block 放入关键图，并只使用原文 alt、相邻图注或正文语境撰写图注，不虚构图片含义。
6. 教程模式按原文顺序编排步骤图。凡用于确认“点哪里、输入什么、选择什么、完成后看到什么”的截图必须出现；为保持可读性可以增加内页，不能为了固定 10 张删图或压缩到看不清。
7. 生成 `cards.json` 后运行：

   ```bash
   scripts/render_cards.sh <cards.json绝对路径> <output目录绝对路径> <profile.json绝对路径>
   ```

8. 逐张检查截断、重叠、步骤顺序、关键图可读性、主题配色和人物比例。
9. 生成 `publish-copy.md`：一个推荐标题、三个备选标题、一段正文和 6–10 个 tags。
10. 运行 `scripts/validate_output.py`；它会检查已收集的关键图是否都进入卡片。通过后再把 `cover.png` 与 `card-01.png ...` 一起打 ZIP。

## 输出结构

```text
<article-slug>-小红书/
├── source.md
├── hero.png
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

- 所有图片 1080×1440；Hero 源图为 16:9。
- 人物每张只出现一次，必须等比例、不裁头、不改变脸。
- 封面、Hero 和内页必须使用当前人物 profile 的同一主色系统；Punk 使用红色只是 Punk profile 的结果，不是通用模板色。
- 封面不计页码；内页从 01 开始。
- 封面账号来自 profile；没有账号则省略，不用品牌名替代。
- 标题和作者来自 Markdown 解析结果；作者缺失时必须询问。
- Markdown 中影响理解、步骤、证据或结果的关键图必须展示；装饰图、头像、重复封面和无关 Logo 不进入内页。
- 教程中的操作截图与检查点截图是内容，不是装饰；缺少任意必备步骤图时不得宣布完成。
- 原始照片默认不复制进文章输出、不提交 GitHub、不公开上传。
- 没有图像生成能力时，输出完整 Hero 提示词和保存计划，明确说明 Hero 与封面尚未完成。
