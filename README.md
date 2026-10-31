# agent-assets

weiwen99 自用的 AI agent skill 集合。每个 skill 是一个独立目录 `skills/<name>/SKILL.md`，被 omp、Claude Code、Codex、pi 等按目录发现的 agent 直接读取。

## 内容

| skill | 用途 |
|---|---|
| `tikz-diagramming` | TikZ/LaTeX 技术图：red/rose core-dataflow 配色，输出矢量 PDF、自包含 SVG、清晰 PNG（可选 lossless WebP） |
| `inkscape-diagramming` | 单色 Inkscape/SVG 架构图、业务流程图，输出可编辑 SVG + PNG |
| `de-ai-flavor` | 按仓库自己的手写基线测量并削掉 AI 文风，不丢事实 |
| `scala-best-practices` | Scala 3 项目创建与日常编码规范（Mill 优先） |
| `org-inline-code-spacing` | Emacs org-mode 行内标记的空格边界与验收步骤 |
| `design-scope-discipline` | 设计文档与 code review 的规模纪律（先量规模、gate 可证伪、代价量化） |

## 安装

```bash
git clone git@github.com:weiwen99/agent-assets.git ~/projects/agent-assets
```

agent 只扫 `<skills 根>/<name>/SKILL.md` 一层，所以**不要**把整个仓库克隆进 skills 根；按需把单个 skill 链进去：

```bash
ln -s ~/projects/agent-assets/skills/<name> ~/.agents/skills/<name>
ln -s ~/projects/agent-assets/skills/<name> ~/.claude/skills/<name>   # Claude Code
```

本仓不提供 Nix/home-manager module。机器侧的槽位由私有机器配置仓声明为指向本仓工作树的活链接，见 `docs/adr/0001`。

## 与「规则」的分工

本仓只有 skill（按需加载的内容）。会被 agent 每次会话无条件注入的约束不放在这里，而是留在机器配置仓，正文退化成一条**指针**：写清触发条件、`MUST` 先加载哪个 skill、skill 缺失时从哪里取、完成条件。这样同一份内容只有一个来源，也不需要在两处维护。

## 校验

```bash
python3 scripts/validate.py
```

检查每个 `SKILL.md` 的 `name`/`description` 非空、`name` 与目录同名、正文非空，并禁止本机绝对路径与内部主机名。CI（`.github/workflows/validate.yml`）在每次 push 与 PR 上跑同一个脚本。

## 许可

- 除另注外：MIT，见 [LICENSE](LICENSE)。
- `skills/scala-best-practices/` 沿用 Apache-2.0，见该目录的 [LICENSE](skills/scala-best-practices/LICENSE)。它的原仓 `weiwen99/scala-best-practices-skill` 已归档，历史与 issue 保留在那里。
