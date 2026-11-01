# SVG 网页约定

此约定适用于已经审阅、可编辑的技术图。固定底色继续使用绘图技能原管线；以下适配过程作用于另一份网页衍生文件，不能据此破坏原编辑稿或印刷输出。

## 主题信号

外部 `<img src="diagram.svg">` 内的 SVG 是独立文档。宿主提供颜色方案，不传递整套 CSS 变量或任意 `currentColor`。图内用 `prefers-color-scheme` 选调色板，路径的 `fill`/`stroke` 仍由作者定义。

下面假设主题属性位于 `html`，图片用显式类；实际项目若使用其他属性或 URL 选择器，应先核对其匹配范围。声明仅限制在 SVG 图片上，避免顺带改变表单和滚动条。

```css
img.theme-aware { color-scheme: light dark; }
html[data-theme="light"] img.theme-aware { color-scheme: light; }
html[data-theme="dark"] img.theme-aware { color-scheme: dark; }

/* 放在手动主题规则之后；第二条选择器与它们优先级相同。 */
@media print {
  img.theme-aware,
  html[data-theme] img.theme-aware { color-scheme: light; }
}
```

图内也声明根方案，解决单独打开原图时浅色字配白色画布的问题；不画整页背景。打印规则在深色规则之后显式恢复所有角色，不能只改 `color-scheme` 却保留浅色墨迹。

```css
:root { color-scheme: light dark; --ink: #202020; }
.ink-fill { fill: var(--ink); }
.ink-stroke { stroke: var(--ink); }
@media (prefers-color-scheme: dark) { :root { --ink: #e8e5e0; } }
@media print { :root { color-scheme: light; --ink: #202020; } }
```

这里的变量定义在 SVG 自己内部。每个实际角色都要覆盖：正文、辅助线、填色、marker 箭头、点和边框。不要用整图 `filter: invert()` 代替角色配色。固定底色图无需拥有主题媒体查询。

## 透明与遮挡

先区分四种白色：整页纸面、遮线标签底、空心点内部、物体或区域本身。只删除已识别的整页矩形。单纯将标签或空心点填色改成 `none` 会露出背后的线。

在原白片轮廓内用亮度遮罩清除之前的绘制，再在遮罩外画文字或边框。遮罩中不透明白色保留，不透明黑色清除；显式写 `mask-type="luminance"`（默认亦为此）。不要将它改成 alpha mask，否则不透明黑色仍保留内容。

```xml
<mask id="gap" mask-type="luminance"
      maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse"
      x="0" y="0" width="320" height="120">
  <rect width="320" height="120" fill="white"/>
  <rect x="140" y="40" width="40" height="40" fill="black"/>
</mask>
<g mask="url(#gap)"><!-- 原来在白片之前的线与填充 --></g>
<text x="160" y="67" text-anchor="middle">L</text>
```

完整图的遮罩必须覆盖所有需要清除的早期绘制；只遮线却留下下面的填色并不透明。后画文字不在这个遮罩内。可以平铺绘制组并给每组应用后续遮挡集合，但应检查大图的遮罩成本，不要求所有图沿用某一种生成算法。

mask 内的白矩形不参与页面绘制。原 `fill="white"` 属性也可能被 CSS 类覆盖，判断依据是最终绘制、透明度和实际合成，不是搜索白色字面量。

## 淡色区域与渐隐

区域填充有语义，不能与标签底一起删除。若输入是已在白底合成的、不透明 RGB，可以在已知合成口径下选一组前景色与 alpha。归一化通道的可选分解为：

```text
C = αF + (1 − α) × 1
α = 1 − min(Cr, Cg, Cb)
α > 0: F = [C − (1 − α)] / α
α = 0: 纯白，是否透明仍由对象语义决定
```

这是数学上选定的一组分解，不是恢复唯一原始透明度，也不是任意颜色空间的通式。改变背景后前景/alpha 需要重新选择并检查对比度。区域重画前应按原语义清掉下层绘制，避免 alpha 变化让以前不可见的线露出。渐隐应朝透明页面过渡，而不是朝写死的白色过渡；带数、颜色数和导出后不同 alpha 数是不同指标。

默认将实际文字/背景配对按 4.5:1、需辨认的线和符号按 3:1 检查，覆盖页面与图内填色上的真实组合；不要对不存在的叠色组合凑门禁，也不把抗锯齿边缘最低像素当角色色值。字形转路径后的文字仍按文字检查。既有品牌色、不可改原稿等限制若与目标冲突，报告并请用户取舍。

## 两种图源

- TikZ：审核后按原 XeLaTeX → PDF → dvisvgm 管线产出固定纸面制品，保留 `.tex`。需要自包含时可将字形转路径；这会增加体积、失去普通文字的选择能力，不等于已解决无障碍。衍生器只允许已识别结构，保留路径、变换、线宽、点径与字形定义，其他差异逐项说明。
- Inkscape：保留编辑稿的活文字、语义 ID 与命名图层。角色 CSS 在设计阶段引入，包含共享 marker 的填色；必要遮罩可包裹新组。若网页另需轮廓化副本，须明确授权、保留活文字主稿并重新验字形与排版。

主源、固定底色 SVG 与网页 SVG 用不同用途/名称标记，例如 `diagram.svg` 与 `diagram.web.svg`，不把一个 PNG 假装成矢量图。网页图片的固有尺寸和 `viewBox` 比例也要核对，避免换格式后在 `max-width` 下意外缩小字号。

## 最小回归与真实浏览器

先运行本技能自带的结构检查，再以 HTTP 打开夹具。命令在本技能目录执行；服务只监听本机，用完停止。

```sh
python3 scripts/check-fixture.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory fixtures
```

打开 `http://127.0.0.1:8765/`。三个面板同时呈现跟随系统、固定浅色、固定深色；切换系统偏好或浏览器开发工具仿真后再检查。也分别打开 `theme-aware.svg` 和浏览器打印预览。静态脚本只验证这份夹具的结构，不检测任意图，更不能证明 CSS 已实际渲染。

每次交付记录以下矩阵；完整复测应至少使用两种独立浏览器引擎。工具不可用时说明已覆盖和未覆盖，不能把未测项当通过。

| 对象 | 验收 |
| --- | --- |
| 系统浅/深 × 页面 auto/light/dark（或实际主题集合） | 含两种反向组合，文字、线与箭头颜色正确 |
| 桌面与窄屏 | 图与代码/正文不制造整体横向溢出，细节可辨或有原图入口 |
| 标签与空心点 | 露出页面底色，旧线不穿过，后画文字和边框保留 |
| 淡色区域与渐隐 | 保持语义边界，无突兀白块；在实际背景上计算角色对比度 |
| 原图直接打开 | 明暗均可读；UA 画布 RGB 不固定，不继承来源页主题 cookie |
| 暗色页面打印 | 真实预览或 PDF 回读为浅色墨迹，无裁切或缺字 |

墨色和透明角落可从真实浏览器视口截图取样；角落 RGB 与明确页面背景相等只是一个探针，须结合整图和遮罩检查。`canvas.drawImage` 可能在不同上下文重渲染 SVG，`getComputedStyle(img)` 只证明外层声明；二者不能单独代替显示验收。headless Chrome/Firefox 仍是真实浏览器，普通栅格转换器通过不代表浏览器媒体查询通过。

## 真实宿主与发布边界

本地预览通过只证明候选。调用方获准发布后，在返回的真实 URL 上再次检查实际嵌入方式、MIME、字节、主题切换和原图链接；`.svg?v=2` 不会匹配简单的后缀选择器。普通 Markdown 链接和图片可能走不同路径改写规则，不手拼服务端 revision 地址。没有真实 URL 或发布权限时标记宿主待验，不因此发布新文或改网站。

SVG 作为图片和作为顶层文档的执行环境不同。交付文件仅含所需图形、内部引用、内置样式和已授权的内容；不添加脚本、事件属性、远程字体/图片或 `foreignObject` 来绕过宿主限制。来自外部的 TeX/SVG 先审阅，结构白名单不应被宣传为通用安全清洗器。

## 记录与来源

交接记录至少含源/衍生文件、版本或 hash、背景分支、宿主假设、浏览器版本和日期、矩阵结果、已验/待验、重建方式。源码推送、机器安装、运行时加载、文章发布是不同动作，分别报告。

机制资料（2026-11-01 核对）：

- [MDN：prefers-color-scheme 的嵌入文档规则](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme)
- [CSS Color Adjustment：根画布与颜色方案](https://www.w3.org/TR/css-color-adjust-1/#color-scheme-effect)
- [MDN：亮度遮罩](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/mask)
- [案例与已验证范围](https://draft.weiwen.org/p/svg-theme-adaptation-eit2nh2466fzhanz)

案例是来源，不是所有未来浏览器的保证；通用规则与本次夹具的运行证据分开记录。
