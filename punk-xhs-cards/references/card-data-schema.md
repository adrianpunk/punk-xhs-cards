# 卡片数据格式

渲染器接收 UTF-8 JSON。封面与内页分开；`cards` 中不得再放 `kind: cover`。

```json
{
  "seriesTitle": "文章短标题",
  "handle": "@用户账号",
  "cover": {
    "title": "完整封面书名",
    "illustration": "cover-illustration.png"
  },
  "cards": []
}
```

`illustration` 是由 `$punk-ip-article-illustrations` 根据 Markdown 内容和当前 IP 生成的 16:9 主题插图。相对路径以 `cards.json` 所在目录为基准，也可使用绝对路径。渲染器把它嵌入 16:9 macOS 窗口；作者不写入 `cards.json`，从 profile 的 `author_name` 读取。

为已有输出保持兼容，渲染器仍可读取旧 `hero`、`artwork` 和旧 `cover.author`；新文章禁止继续生成旧格式。

## 内页卡

```json
{
  "kind": "content",
  "eyebrow": "01 · 核心定义",
  "title": "提示词解决一次，Skill 固化一类任务",
  "blocks": [
    {"kind": "paragraph", "text": "普通正文。"},
    {"kind": "highlight", "text": "重点结论。"},
    {"kind": "section", "text": "小节标题"},
    {"kind": "item", "number": "01", "title": "条目标题", "body": "条目说明。"},
    {"kind": "bullet", "text": "项目符号内容。"},
    {"kind": "code", "text": "命令或目录结构"},
    {"kind": "image", "path": "assets/article-images/image-03.png", "caption": "原文图注或准确的上下文说明", "height": 360},
    {"kind": "note", "text": "提醒、边界或行动建议。"},
    {"kind": "spacer", "height": 20}
  ]
}
```

## 块类型

- `paragraph`：连续解释，建议 1–3 句。
- `highlight`：核心结论，每页最多一个。
- `section`：小节标题。
- `item`：步骤、维度、坑点。
- `bullet`：并列短句。
- `code`：命令、YAML、目录或固定模板。
- `image`：Markdown 中的关键图。`path` 相对 `cards.json` 所在目录或使用绝对路径；`caption` 可省略；`height` 是图片面板高度，默认 360，范围 220–520。
- `note`：异常、风险、总结或下一步。
- `spacer`：必要时调整节奏，建议 8–28。

## 密度

- 每页建议 4–8 个 blocks。
- 同页 item 最多 5 个；解释较长时最多 4 个。
- 不把 Markdown 符号写进普通文本。
- 溢出时重新分配内容，不盲目缩小正文。
- 默认每页最多一个 `image` block；细节密集的截图或图表优先单独成页。
