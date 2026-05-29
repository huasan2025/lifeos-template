# Commands

这里记录 AI 助理可用的命令。
这些命令不是为了炫技，而是为了在高频决策场景中，稳定调用系统级上下文。

> 命令文件实体在 `.claude/commands/`。把 vault 维护想成三类动作：
> **写入**（`/save` `/capture`）· **读取/判断**（`/go`）· **自检**（`/lint`）。
> `/init-life-os` 是一次性的 onboarding，不属于日常循环。

## `/init-life-os` — 首次 onboarding（一辈子一次）

4 步访谈生成 Identity.md + Soul.md + 全 vault 占位符替换。约 10-30 分钟。拿到 fresh fork 后跑一次，详见 `.claude/commands/init-life-os.md`。

## `/go` — 恢复 + 判断（每天的单一入口）

读 `PROGRESS.md` + `Identity.md` + `Soul.md` 和任务下 📄 关联文档，先恢复"你在哪、还剩什么"，再判断今天最该做的 1-3 件（含"今天不要做"和"最小保底动作"）。

### 使用原则
- 不复述已完成事项；不自作主张开始工作，等${USER_NAME}确认方向
- 关联文档**必须读**，不要跳过
- 优先真实问题 / 资产积累 / 接近现金流；${USER_NAME}被新灵感带偏时直接指出
- 可以挑战判断，但不替${USER_NAME}做最终决定

> 早期有独立的 `/today`（深一层的今日判断），实践中和 `/go` 重叠、很少单独用，v0.2 合并进 `/go`。

## `/save` — 保存进度（写入）

保存当前会话进度到 `PROGRESS.md`，归档旧的"本轮完成的事"到 `90-System/PROGRESS-ARCHIVE.md`。/clear 前用。
- 末尾跑 lint 轻量版（死链 / 命令路径）做结构兜底
- 触发 ${ASSISTANT_NAME} 的自我进化检查（详见 `91-Assistant/Evolution Rules.md`）

## `/capture` — 提取写作素材（写入）

从当前对话中提取洞察/转折/框架，存为 Process Note（落到当前项目的 `process/` 子目录）。不是每次对话都需要 capture，只在"聊出了东西"时用。

## `/lint` — 结构自检（自检）

扫描 vault，把硬约束自动查一遍：死 wikilink、命令死引用、Problem ≤3、Project 锚定、孤儿笔记、缺入口笔记。只报告不自动改。
- 全量 6 项体检，结构大改后或定期手动跑
- 每次扫描往 `90-System/lint-log.md` 追加带时间戳的结果，报告头显示"上次扫描"时间
- 轻量版（死链 / 命令路径）已折叠进 `/save`，日常兜底
- 只做结构自检，不做经验蒸馏（那是 `91-Assistant/Evolution Rules.md` 的事）

## 设计原则

- 命令引用的文件路径必须真实存在——结构重构后**同步更新命令引用**，否则产生死引用（`/lint` 专门查这个）
- 一个命令只干一件事，不混淆职责
- 新命令只在现有命令稳定有用、且痛点高频出现后才加（如无必要勿增实体）
