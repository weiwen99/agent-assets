# 0001 — 公开仓只放 skill，rule 退化为指针

- 状态：已采纳，2026-10-31

## 背景

自写的 agent 资产原先散在三处：`tikz-diagramming`、`inkscape-diagramming`、`de-ai-flavor` 直接维护在公司私有仓 `xai/prefill-skills`（作为产品仓的 submodule），`scala-best-practices` 有自己的公开仓，两条行为约束以 rule 形式躺在私有机器配置仓。同一个 skill 存在 2–3 份副本，`scala-best-practices` 已经分叉。

目标是一个公开仓，作为自写 skill 的唯一来源。

## 决策

1. 本仓只有 `skills/`，不设 `rules/` 层。rule 的实质内容迁成 skill。
2. 机器上的 rule 保留，但退化为 pointer rule：触发条件 + `MUST` 加载某 skill + 缺失时如何获取 + 完成条件。触发常驻，正文不在 rule 里。
3. `scala-best-practices` 并入本仓，旧仓归档。
4. 机器侧安装由机器配置仓声明活链接（指向本仓工作树），本仓不提供 Nix/home-manager module。
5. 第三方 skill 不 vendored；需要展平与上游 pin 的消费方继续用各自的 bundle。

## 否决的替代方案

- **rule 镜像到本仓**：多了单向同步与漂移检查，收益只是"内容公开"。
- **公开仓作为 rule 的 flake input**：给多台主机的配置构建引入对公开仓的依赖与输入分组登记，为「公开」这一件事付构建期成本；且本仓内容变动要重新 lock。
- **rule 槽位直接指向 `SKILL.md`**（一份文件两用，全文常驻）：省掉一次 skill 读取，但让 always-apply 的 rule 依赖本仓是否已克隆到该主机——没 clone 的主机连触发都不存在；还让约 7.4KB 正文常驻 prompt。

## 后果

- always-apply 从「正文常驻」变成「指针常驻 + 一次 skill 读取」。漏读即静默不合规；验收方式是开新会话实测触发。
- rule 必须保留 `alwaysApply: true`。只写 `description` 的 rule 会掉进 rulebook 桶，只列名字、不注入。
- skill 根只扫一层，安装只能用单 skill 链接，不能把整个仓库克隆进 skill 根。
- 已知约束：主机没克隆本仓时 skill 不可见；本仓不 pin 任何上游 commit。
