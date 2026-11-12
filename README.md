# agent-assets

weiwen99 自用的 AI agent skill 集合。每个 skill 是一个独立目录 `skills/<name>/SKILL.md`，被 omp、Claude Code、Codex、pi 等按目录发现的 agent 直接读取。

## 内容

| skill | 用途 |
|---|---|
| `tikz-diagramming` | TikZ/LaTeX 技术图：red/rose core-dataflow 配色，输出矢量 PDF、自包含 SVG、清晰 PNG（可选 lossless WebP） |
| `inkscape-diagramming` | 单色 Inkscape/SVG 架构图、业务流程图，输出可编辑 SVG + PNG |
| `svg-web-delivery` | 网页 SVG 的主题自适应交付：主题信号、图内配色角色、透明遮挡、打印回退、真实宿主验收；两个绘图 skill 按需加载它 |
| `de-ai-flavor` | 按仓库自己的手写基线测量并削掉 AI 文风，不丢事实；只读的论证审读模式查自设靶子与无依据的防误解提醒 |
| `scala-best-practices` | Scala 3 项目创建与日常编码规范（Mill 优先） |
| `org-inline-code-spacing` | Emacs org-mode 行内标记的空格边界与验收步骤 |
| `design-scope-discipline` | 设计文档与 code review 的规模纪律（先量规模、gate 可证伪、代价量化）；评审含分析性文字时按同根链接加载 `de-ai-flavor` 的论证审读模式 |

## 安装

```bash
git clone git@github.com:weiwen99/agent-assets.git ~/projects/agent-assets
```

agent 只扫 `<skills 根>/<name>/SKILL.md` 一层，所以**不要**把整个仓库克隆进 skills 根；按需把单个 skill 链进去：

```bash
ln -s ~/projects/agent-assets/skills/<name> ~/.agents/skills/<name>
ln -s ~/projects/agent-assets/skills/<name> ~/.claude/skills/<name>   # Claude Code
```

`tikz-diagramming` 与 `inkscape-diagramming` 的网页自适应分支用相对链接 `../svg-web-delivery/SKILL.md` 加载共用规则，安装任一调用方时，应把它与 `svg-web-delivery` 放在**同一个 skills 根**。下面演示安装两种绘图入口及其共用技能；不需要的绘图入口可以省去：

```bash
for name in svg-web-delivery tikz-diagramming inkscape-diagramming; do
  ln -s ~/projects/agent-assets/skills/$name ~/.agents/skills/$name
  ln -s ~/projects/agent-assets/skills/$name ~/.claude/skills/$name   # Claude Code
done
```

只装调用方、或把调用方单独拍平到别处而没有兄弟 `svg-web-delivery`，自适应分支在加载处失败；固定底色分支不依赖它，照旧可用。`design-scope-discipline` 只在评审含分析性文字时按相对链接 `../de-ai-flavor/SKILL.md` 加载论证审读模式，装它时把 `de-ai-flavor` 放进同一个 skills 根；纯代码评审不需要它。目标机器没有本仓时，从 [github.com/weiwen99/agent-assets](https://github.com/weiwen99/agent-assets) 克隆**整个**仓库到可写工作区（同根引用与样例跟着一起来），记录解析到的 commit，再加载 `skills/svg-web-delivery/SKILL.md` 及其指向的 references、fixtures。

槽位上已有手工拷贝时，要先跑一次迁移：它把要替换的条目移进带时间戳的备份目录（`agents/`、`claude/` 分开放），已经指向本仓的链接原样保留，遇到既不是目录也不是链接的东西立即停下。

```bash
scripts/adopt-local-slots.sh ~/projects/agent-assets
```

**迁移本身不装替代链接**，所以它必须和「机器激活」（home-manager / `ee` / `nix-rebuild`）放在同一个窗口里连续做完；在激活完成前，被移走的那几个 skill 在这台机上不可见。clone 本身随时可做，没有这个窗口问题。

本仓不提供 Nix/home-manager module。机器侧的槽位由私有机器配置仓声明为指向本仓工作树的活链接，见 `docs/adr/0001`。

## 与「规则」的分工

本仓只有 skill（按需加载的内容）。会被 agent 每次会话无条件注入的约束不放在这里，而是留在机器配置仓，正文退化成一条**指针**：写清触发条件、`MUST` 先加载哪个 skill、skill 缺失时从哪里取、完成条件。这样同一份内容只有一个来源，也不需要在两处维护。

## 校验

```bash
python3 scripts/validate.py                 # 校验本仓 skills/
python3 scripts/validate.py /path/to/skills # 校验扁平安装目录（同根依赖检查）
python3 scripts/test_validate.py            # validator 单测，纯标准库，不联网
python3 scripts/test_argument_review.py     # 论证审读的结构检查：模式指针、文件可达、零汉字脚本、fixtures
python3 skills/svg-web-delivery/scripts/check-fixture.py --self-test
```

检查每个 `SKILL.md` 的 `name`/`description` 非空、`name` 与目录同名、正文非空，并禁止本机绝对路径与内部主机名。此外检查每个 skill 目录内 Markdown 的相对链接：必须按安装槽位的逻辑路径解析到 skills 根内的文件或目录（skill 目录可以是符号链接），`#anchor` 只取路径、不核对锚点；代码块、行内代码、HTML 注释里的示例链接和外链不检查。缺兄弟依赖就是一条链接失败，这正是「单装调用方不可用」的检查方式。

`test_argument_review.py` 只查结构：两个技能的论证审读模式指针、引用文件可达、`de-ai-flavor` 第 1 步脚本在零汉字文本上不除零并标出语言口径、fixtures 的 ID 对齐与冻结 hash。它不判断任何一例的语义对错；语义只能靠跑模型并对照原始输出评分。

CI（`.github/workflows/validate.yml`）运行上述校验、单测、论证审读结构检查及SVG夹具结构检查。真实浏览器的主题、原图和打印矩阵另按 `svg-web-delivery` 执行，结构检查不能代替渲染验收。

## 许可

- 除另注外：MIT，见 [LICENSE](LICENSE)。
- `skills/scala-best-practices/` 沿用 Apache-2.0，见该目录的 [LICENSE](skills/scala-best-practices/LICENSE)。它的原仓 `weiwen99/scala-best-practices-skill` 已归档，历史与 issue 保留在那里。
