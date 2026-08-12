# Profile 状态与目录

card profile 是已确认人物角色的小红书视觉扩展，不负责从照片创建人物。人物角色沿用 `references/character-package.md` 和 `.punk-ip-assets/`；只有 `confirmed` 人物才能注册 card profile。

## 运行目录

默认使用当前项目：

```text
<project-root>/.xhs-ip-cards/
```

用户明确指定位置时遵循用户选择。不要把运行数据、真人照片或生成角色写进 Skill 安装目录。

## 目录结构

```text
.xhs-ip-cards/
├── current-profile.json
└── profiles/
    └── <profile-slug>/
        ├── profile.json
        ├── character-sheet.png
        ├── character-clean.png
        ├── character-card-pose.png
        ├── character-spec.md
        ├── theme.json
        └── layout-sample.png
```

slug 只使用小写字母、数字和连字符。

## 状态

- `draft`：卡片专用动作、配色或样稿待确认；不得批量生产文章卡片。
- `confirmed`：用户明确确认后可用于文章生产并可设为当前 profile。

每次修订增加 revision，旧文件使用 `-v2`、`-v3` 保留。

## 注册

先运行 `character_registry.py resolve` 得到已确认人物的 `sheet`、`clean_reference` 和 `spec` 绝对路径，再与用户确认的动作描述、新生成的 `card_pose`、`theme` 一起注册。`card_action` 是 profile 的正式字段；不同用户可以使用站立讲解、指向内容、拿着平板、白板书写或坐着使用电脑等不同动作。card profile 保存人物资产快照，确保后续渲染不会因当前角色切换而漂移。

```bash
python3 scripts/profile_registry.py register \
  --root <runtime-root> \
  --slug <slug> \
  --name "<显示名称>" \
  --author-name "<人物创建阶段确认的名称>" \
  --action "<用户确认的卡片动作>" \
  --sheet <character-sheet.png> \
  --clean-reference <character-clean.png> \
  --card-pose <character-card-pose.png> \
  --spec <character-spec.md> \
  --theme <theme.json>
```

不得在用户未确认动作时注册新 profile。旧版 profile 如果没有 `card_action`，解析器会只为兼容目的补上原有的“盘腿使用电脑，身体和视线朝向内容区”；下一次修订时必须重新询问并写入用户明确选择的动作。

`author_name` 必须从已确认 character manifest 复制，封面只读取这个字段。旧 profile 没有该字段时，解析器会优先读取 `theme.json` 的 `profileName`，最后才回退到 profile 显示名称；下一次修订必须写入明确的 `author_name`。

## 确认与解析

```bash
python3 scripts/profile_registry.py confirm --root <runtime-root> --slug <slug>
python3 scripts/profile_registry.py resolve --root <runtime-root>
python3 scripts/profile_registry.py resolve --root <runtime-root> --slug <slug> --allow-draft
python3 scripts/profile_registry.py activate --root <runtime-root> --slug <slug>
python3 scripts/profile_registry.py list --root <runtime-root>
```

渲染正式文章时直接把 `profile.json` 绝对路径传给跨平台 `render_cards.py`。生成确认前样稿时追加 `--allow-draft`。按操作系统选择 Python 命令和包装脚本，完整规则见 `references/platform-rendering.md`。
