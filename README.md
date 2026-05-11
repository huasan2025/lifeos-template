# lifeos-template

> Personal life & project OS template — fork to start your own AI-assisted vault.

基于 Obsidian + Claude Code 的个人操作系统模板。从复盘 → 战略问题 → 项目执行 → 经验沉淀，闭环管理。

## 目标用户

- 想用 AI 提效的独立创业者 / 自由职业者 / 知识工作者
- 愿意装 Claude Code（一次性，看教程视频跟着做就行）
- 不要求会编程，但需要基本终端命令熟悉度（`cd` `ls` 这种）

## 它是什么

一个**结构化的 Obsidian vault** + **AI 助理人格 + 命令系统**。包括：

- **Problems**（≤3 个长期赌注）→ **Projects**（执行容器）→ **Library**（跨项目沉淀）三层模型
- **AI 助理**（你给它取名、定义人格）通过 4 个命令陪伴你：
  - `/init-life-os` — onboarding，4 步访谈生成你的定制化配置
  - `/go` — 恢复上下文，告诉你今天最该做什么
  - `/save` — 保存进度 + AI 自我进化检查
  - `/today` — 基于上下文给出今日聚焦
- **过程即内容**：项目过程产物（笔记/文章/视频稿）跟项目走，自然变成可发布内容

## 快速开始

### 1. Fork 并 clone

```bash
# 在 GitHub 上点 Fork（或下载 zip）
git clone https://github.com/<你的用户名>/lifeos-template.git my-vault
cd my-vault
```

### 2. 装 Claude Code

看 [装 CC 教程视频](https://...)（5-10 分钟，有付费用户群链接）

### 3. 跑 onboarding

```bash
claude
```

进入 Claude Code 后，输入：

```
/init-life-os
```

跟着 AI 助理走 4 步访谈：
1. 5 维度信息挖掘（让 AI 了解你）
2. AI 助理命名 + 人格选择（AI 给你 3 个候选）
3. 命令保留 / 删除选择（默认全留）
4. 写作风格选择（默认跳过）

约 10-30 分钟（取决于第一段你 dump 多少信息）。

### 4. 开始用

```
/go
```

AI 助理会读你的 Identity / Soul / PROGRESS，告诉你今天最该做什么。

## 非 Claude Code 用户

你也可以在其他 AI 工具（ChatGPT / Claude.ai / Codex / Cursor）里跑 onboarding。把 `.claude/commands/init-life-os.md` 文件内容复制粘贴到 AI 对话框，告诉 AI："请按这个 prompt 引导我完成 onboarding"。AI 会输出 markdown 让你手动复制到 vault 内对应文件。

日常使用同理：把 `.claude/commands/save.md` `go.md` `today.md` 内容复制粘贴到 AI 对话框，AI 按内容跑。

## 系统设计原则

- **Problems ≤ 3**：战略问题硬性上限，超出说明还没收敛到真正赌注
- **过程即内容**：项目产出物留项目里
- **Git 是回收站**：删除直接删
- **AI 默认不读 99-Archive**：冷库不污染上下文
- 详见 `CLAUDE.md` 内的核心规则

## 路线图

- v0.1 (current): onboarding skill + 模板 vault
- v0.2: 命令选择交互、写作风格预设包
- v1.0: Web 表单 onboarding（无需装 CC）

## 反馈 / 提问

入群（付费用户）或在 [issues](https://github.com/huasan2025/lifeos-template/issues) 反馈。

## License

MIT
