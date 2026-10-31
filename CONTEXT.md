# CONTEXT

本仓的术语表。只说这些词在这里指什么，不记录实现细节。

## skill

可移植的能力包：`skills/<name>/SKILL.md` 加该目录下的脚本、模板、参考。按需加载，**不**保证每次会话都生效。

## rule

机器级的 always-apply 约束，由用户级 agent 配置在每次会话注入。不是本仓的内容类型；本仓不存放 rule。

## pointer rule

只含四段的 rule：触发条件、`MUST` 先加载哪个 skill、skill 缺失时从哪里取、完成条件。它让「何时该用」常驻上下文，而正文只存在于 skill。

## skill 根

agent 扫描 skill 的目录，如 `~/.agents/skills`、`~/.claude/skills`。扫描只下探一层：`<根>/<name>/SKILL.md`；`<根>/<repo>/skills/<name>/SKILL.md` 不会被发现。

## bundle

按上游 commit 把多个 skill 展平、供产品仓库消费的构建产物。bundle 是产物，不是源；源是本仓和上游仓库。
