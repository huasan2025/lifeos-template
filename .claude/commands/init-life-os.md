---
name: init-life-os
description: 4 步访谈引导新用户初始化 lifeos vault（生成 Identity.md + Soul.md + 占位符替换全 vault）
---

# /init-life-os

为新用户初始化 lifeos vault。4 步访谈：
1. **5 维度信息挖掘** → 生成 `90-System/Identity.md`
2. **AI 助理命名 + 人格定义** → 生成 `90-System/Soul.md` + 占位符替换全 vault
3. **命令保留选择** （MVP 默认全留，跳过）
4. **写作风格选择** （MVP 默认跳过）

整个过程预计 10-30 分钟（取决于用户首段输入信息密度）。

---

## 工作流

按以下顺序执行：

### State 检查

跑 onboarding 之前，检查 vault 根目录是否有 `.onboarding-state.json`：

**如果不存在：**
- 这是首次跑，正常进入 Step 1
- onboarding 进行中每完成一个里程碑（Step 1 草稿确认 / Step 2 助理选定），更新 state 文件

**如果存在：**
- 读取 state，提取已完成的 step 编号 + 已收集的回答
- 提示用户：
  ```
  你上次走到 Step [X]（[milestone 描述]），已经回答了 [N] 个问题。
  要继续吗？(y/n) 或 (重新开始)
  ```
- y → 续上（跳过已完成的 step，从断点继续）
- n / 重新开始 → 删除 state 文件，从 Step 1 开始
- 用户输入其他 → 默认 y

**state 文件 schema：**

```json
{
  "version": "0.1",
  "started_at": "2026-05-12T10:30:00",
  "current_step": 1,
  "step_1": {
    "completed": false,
    "dimension_status": {
      "1_identity": {"depth": 0, "summary": ""},
      "2_capability": {"depth": 0, "summary": ""},
      "3_blocker": {"depth": 0, "summary": ""},
      "4_goal": {"depth": 0, "summary": ""},
      "5_constraint": {"depth": 0, "summary": ""}
    },
    "draft_confirmed": false
  },
  "step_2": {
    "completed": false,
    "candidates_generated": [],
    "selected_candidate": null
  },
  "step_3_skipped": true,
  "step_4_skipped": true,
  "placeholder_replacement_done": false
}
```

**何时写 state（落点）：**

- Step 1 每个维度 confirm 后（更新 dimension_status）
- Step 1 草稿 confirm 后（draft_confirmed = true）
- Step 2 候选生成后（candidates_generated += [候选 1/2/3]）
- Step 2 用户选完后（selected_candidate = 1/2/3 或 'custom'）
- 占位符替换后（placeholder_replacement_done = true）
- onboarding 全部完成后，**删除** state 文件

**state 文件路径：** `<vault root>/.onboarding-state.json`（已在 .gitignore）

### Step 1：5 维度信息挖掘

**目标：** 通过自适应访谈，挖出 5 维度的信息：身份/角色 + 核心能力 + 当前瓶颈 + 6-12 月目标 + 约束。

**核心原则：** 5 维度是**信息目标**，不是固定步数。用户每段回答后，评估"已覆盖哪些维度、深度够不够"。已充分覆盖的维度跳过追问；未覆盖或浅薄的才主动问。终止条件：5 维度都达到"足以写一段 Identity.md"的深度。

**起始话术：**

```
嗨！我是你的 LifeOS onboarding 助手。

我们先了解你 5 件事，根据你给我的信息密度，可能 2-3 轮也可能 8-10 轮，
但目标都是同一个：让我充分理解你，写出准确的 Identity.md。

5 维度是：
1. 身份 / 角色
2. 核心能力
3. 当前瓶颈 / 主问题
4. 6-12 月目标
5. 约束（你不想做什么）

你可以一段话 dump 全部，或我们一个一个聊。从第 1 件开始：

**你目前在做什么？职业 / 状态 / 项目阶段，给我介绍一下。**
```

**用户回答后的处理：**

1. 解析这段话覆盖了 5 维度的哪几个，每个深度如何（1=没说 / 2=浅 / 3=中 / 4=深）
2. 对每个未达 3 的维度发追问（或合并几个相关的一起追问）
3. 每追问一组用户回答后，给一句 summary 让用户确认：
   ```
   第 N 维度（XX）我理解了：[一句话 summary]，对吗？
   ```
4. 用户 confirm 后，进入下一个未达 3 的维度
5. 全部 5 维度达到 ≥3 时，进入"草稿 + 审查"环节

**草稿生成：**

```
好，我把 5 维度整理成 Identity.md 草稿。看一下：

[完整 Identity.md 内容，5 段，每段对应一个维度]

要改哪条？或者直接 confirm。
```

**用户审查：**
- "改第 X 维度" → 重新问该维度，AI 改对应段
- "全改" / "重新来" → 二次确认（"会丢已有回答，确定吗？"）→ 删除 state 重新走
- "OK" / "confirm" → 写入 `90-System/Identity.md`，进 Step 2

**默认不记录的内容（明确告知用户）：**
- 敏感个人信息（身份证、手机号、地址）
- 临时情绪
- 未验证的猜测
- 家庭隐私（除非用户明确要求记录）

### Step 2：AI 助理命名 + 人格定义

**目标：** 基于 Step 1 的 Identity 信息，AI 推荐 3 个候选助理（每个含名字 + 风格 + 示例对话），用户选 1 个或自定义。

**话术：**

```
基于你刚才告诉我的（[Identity summary，2-3 句]），
我为你推荐 3 个候选 AI 助理。每个我都演一段对话给你看，你选最舒服的。
```

**3 个候选生成原则：**

- **风格差异明显**：温度（暖/冷）+ 主动性（推/陪）2 维度上跨度 ≥ 2
- **名字本地化**：根据用户姓名 / 兴趣 / 文化背景定制（中文用户用中文名）
- **必须显式避开**：不推荐与 lifeos-template 创建者预设相关的名字 / 风格

**输出格式（示例）：**

```
候选 1：[名字]（[风格类型，如创业合伙人型]）
"[一段示例对话，~50 字，让用户直观感受这个助理日常说话方式]"

候选 2：[名字]（[风格类型]）
"[示例对话]"

候选 3：[名字]（[风格类型]）
"[示例对话]"

选 1 / 2 / 3，或告诉我你想自己来。
```

**用户选完后：**

- 选 1/2/3：把对应候选完整写入 `90-System/Soul.md`（含名字、风格描述、行为约定、示例对话）
- "我想自己来" → 转开放问 2 维度模式：
  ```
  好，自己来。回答两个问题：
  Q1: 你希望助理对你说话偏温暖（关心情绪）还是偏理性（直接给方案）？
  Q2: 你希望助理等你来问，还是主动反问、推你前进？
  ```
  根据回答合成自定义人格，再次写入 `90-System/Soul.md`

**写完后审查：**

```
你的 ${ASSISTANT_NAME} 是 [名字]，[风格描述一句]。
看一下 Soul.md 草稿，要改哪条行为？或者 confirm 进入下一步。
```

- "改 X" → 修对应段
- "confirm" → 进占位符替换
- "换一组" → 重新生成 3 个候选（避开上一组风格）

### Step 3：命令选择（默认全留）

直接告诉用户："默认保留所有命令（/save /go /today /capture）。如果你想删除某个，可以打开 `90-System/Commands.md` 手动改。"

### Step 4：写作风格（默认跳过）

直接告诉用户："写作风格预设暂未实装（v0.2 加），先跳过。如果需要让 AI 学习某种风格，可以在 90-System/ 下手工建一个 character.md 描述你想要的风格。"

### 占位符替换

Step 2 完成后，根据用户回答的几个关键变量，全 vault 字符串替换。

**变量映射：**

| 占位符 | 替换值来源 | 示例 |
|---|---|---|
| `${USER_NAME}` | Step 1 用户身份回答里提取的称呼 | "Alice" / "小王" / "李雷" |
| `${ASSISTANT_NAME}` | Step 2 用户选定 / 自定义的助理名 | "南瓜" / "Lex" / "小文" |
| `${USER_HANDLE}` | （可选）GitHub 用户名或社媒 handle | "alicedev" |
| `${VAULT_NAME}` | （可选）用户给自己 vault 取的名字 | "MyLifeOS" / "Alice 的人生 OS" |

**变量收集时机：**
- USER_NAME：Step 1 第一个维度回答时主动问"你怎么称呼自己？"（如果用户没说）
- ASSISTANT_NAME：Step 2 选完候选时已知
- USER_HANDLE：onboarding 结尾问一次（"你想用什么 handle 作为 GitHub username？可选，跳过用 \"my\""）
- VAULT_NAME：onboarding 结尾问一次（"给你的 LifeOS 起个名？默认 \"MyLifeOS\""）

**替换执行（Bash 工具）：**

```bash
cd <vault root>

# 仅替换 .md / .json / .yaml / .yml / .txt / .sh 文件
# 注意：排除 .claude/commands/init-life-os.md 自身（保留原样以便用户重新跑或将来分享 / fork）
find . -type f \( \
    -name '*.md' -o -name '*.json' -o -name '*.yaml' -o \
    -name '*.yml' -o -name '*.txt' -o -name '*.sh' \
\) \
    -not -path './.git/*' \
    -not -path './.obsidian/*' \
    -not -path './node_modules/*' \
    -not -path './.claude/commands/init-life-os.md' \
    -exec sed -i '' \
        -e "s|\${USER_NAME}|${USER_NAME_VALUE}|g" \
        -e "s|\${ASSISTANT_NAME}|${ASSISTANT_NAME_VALUE}|g" \
        -e "s|\${USER_HANDLE}|${USER_HANDLE_VALUE}|g" \
        -e "s|\${VAULT_NAME}|${VAULT_NAME_VALUE}|g" \
        {} +
```

**替换后验证：**

```bash
# 检查残留占位符（应忽略 init-life-os.md 自身）
grep -rn '\${USER_NAME}\|${ASSISTANT_NAME}\|${USER_HANDLE}\|${VAULT_NAME}' \
    --include='*.md' \
    --exclude-dir=.git \
    --exclude-dir=.obsidian \
    . 2>/dev/null | grep -v '.claude/commands/init-life-os.md'
```

预期：空输出（没有残留）

如果有残留：报告给用户哪些文件，让用户确认是否手动改。

### 重命名 91-Assistant 目录

占位符替换完成后，把通用代号 `91-Assistant` 目录重命名为 `91-<助理名>`，让目录名也反映用户的助理。

**变量来源：** `${ASSISTANT_NAME_VALUE}`（Step 2 用户选定/自定义的助理名）

**执行：**

```bash
cd <vault root>

# 如果助理名含空格 / 特殊字符，按用户偏好规范化（建议保留中文，删空格）
SAFE_NAME=$(echo "${ASSISTANT_NAME_VALUE}" | tr -d ' /\\:')

# 重命名目录
if [ -d "91-Assistant" ]; then
    mv "91-Assistant" "91-${SAFE_NAME}"
fi
```

**同步更新引用：** 文档里所有 `91-Assistant/` 字面引用要替换为 `91-${SAFE_NAME}/`（前一步占位符替换已经处理了 `${ASSISTANT_NAME}` 但没处理硬编码的 `91-Assistant` 字面字符串）：

```bash
find . -type f \( -name '*.md' -o -name '*.json' \) \
    -not -path './.git/*' \
    -not -path './.obsidian/*' \
    -not -path './.claude/commands/init-life-os.md' \
    -exec sed -i '' "s|91-Assistant|91-${SAFE_NAME}|g" {} +
```

**特殊文件：** `.obsidian/graph.json` 里的关系图谱配置 path 也含 `91-Assistant`，上面的 find 已覆盖（含 .json）。

### 收尾

占位符替换完成后：

1. **删除 state 文件**
   ```bash
   rm <vault root>/.onboarding-state.json
   ```

2. **告诉用户下一步**

   ```
   ✅ Onboarding 完成！

   你现在的 vault 是定制版本：
   - Identity.md：${USER_NAME} 的画像
   - Soul.md：${ASSISTANT_NAME} 的人格定义
   - CLAUDE.md / AGENTS.md / 91-Assistant/Evolution Rules.md：所有占位符已替换

   接下来推荐：

   1. 在 02-Problems/ 下写 1-2 个真实的战略问题（参考 EXAMPLE-Problem.md，写完删除示范文件）
   2. 在 PROGRESS.md 顶部"还没做的事"里写 1-3 件你最想做的事
   3. 跑 /go 开始第一天

   ${ASSISTANT_NAME} 已经准备好了。
   ```

3. **首次 commit 提示**

   ```
   建议你做第一次 commit 把当前定制化版本固化：

   git add -A
   git commit -m "init: my lifeos config (onboarding done)"

   想 push 到远程？建议把 fork 改成 private（包含个人信息），再 push。
   ```
