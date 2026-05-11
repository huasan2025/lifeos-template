# Commands

这里记录 AI 助理可用的命令。
这些命令不是为了炫技，而是为了在高频决策场景中，稳定调用系统级上下文。

## `/init-life-os`

### 作用
首次 onboarding，4 步访谈生成 Identity.md + Soul.md + 全 vault 占位符替换。约 10-30 分钟。

### 触发
拿到 fresh fork 之后跑一次。详见 `.claude/commands/init-life-os.md`。

## `/go`

### 作用
恢复上下文。读 `PROGRESS.md` 的"还没做的事"和关联文档，告诉${USER_NAME}今天能继续做什么。

### 读取内容
- `PROGRESS.md`
- 任务下 📄 标记的关联文档

### 使用原则
- 不复述已完成事项
- 不自作主张开始工作，等${USER_NAME}确认方向
- 关联文档**必须读**，不要跳过

## `/today`

### 作用
基于${USER_NAME}的身份、原则、当前状态、当前问题和当前项目，判断今天最值得推进的 1-3 件事。

### 读取内容
- `90-System/Identity.md`
- `90-System/Soul.md`
- `PROGRESS.md`
- 从 PROGRESS 的"还没做的事"识别当前活跃的 Problem 和 Project

### 输出内容
- 今日判断
- 今天只做这 1-3 件事
- 为什么是这几件
- 今天不要做
- 最小保底动作

### 使用原则
- 优先真实问题，而不是自我感动
- 优先资产积累，而不是临时忙碌
- 优先接近现金流的动作
- 如果${USER_NAME}在逃避关键问题或被新灵感带偏，要直接指出
- 最终决策以${USER_NAME}的意志为准

## `/save`

### 作用
保存当前会话进度到 `PROGRESS.md`，归档旧的"本轮完成的事"到 `90-System/PROGRESS-ARCHIVE.md`。/clear 前用。

### 副作用
- 触发${ASSISTANT_NAME}的自我进化检查（详见 `91-Assistant/Evolution Rules.md`）

## `/capture`

### 作用
从当前对话中提取写作素材，保存为 Process Note（落到当前项目的 `process/` 子目录）。

### 触发
对话中产生了值得写成内容的洞察、转折、框架时。不是每次对话都需要 capture。

## 后续可增加的命令

只有在以上 5 个命令稳定有用之后，才继续扩展。
