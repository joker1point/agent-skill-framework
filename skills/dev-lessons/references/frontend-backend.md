# 前后端异步与状态同步踩坑

场景标签：`#前端` `#后端` `#异步` `#状态管理`

## 条目索引（按编号或关键词检索：**先用 search_content 搜编号 / 关键词，勿整读本文件**）

| 编号 | 标题 | 场景标签 |
|---|---|---|
| F-01 | 占位状态显式建模：绝不把占位文本当结果 | #异步 #前端 |
| F-02 | 用户 override 必须写回 DB | #异步 #后端 #DB |
| F-03 | 决策点阻塞条件要与"用户主动"解耦 | #后端 #业务逻辑 |
| F-04 | 乐观更新 + 新鲜度标记 | #前端 #UX |
| F-05 | 跨源刷新与 stale 保护 | #前端 |
| F-06 | 序列化完整性：API 字段与前端契约 | #后端 #API设计 |
| F-07 | rAF 循环双重调度 → 后继帧指数多开 | #前端 #动画 #rAF |
| F-08 | smoothDamp 的位移钳制必须外置，放 damp 内部会破坏阻尼动力学 | #前端 #动画 #数值方法 |
| F-09 | 收敛自停的 rAF 响应不了非输入事件的状态变化 | #前端 #动画 #rAF |
| F-10 | CSS 3D 残留（preserve-3d + translateZ）使 DOM 顺序层级失效 | #前端 #CSS #视觉bug |
| F-11 | React 18 批处理吃掉“成功提示”：异步子 setState 与父 setState 同批 | #React #状态 #UX |
| F-12 | Tailwind 变体类不在 classList：写「没有的那个类」的选择器是死代码 | #前端 #CSS #Tailwind #深色模式 |
| F-13 | 内联元素负 margin 会减少内联前进量：给标题图标加负 margin 把文字带偏 | #前端 #CSS #布局 |
| F-14 | 已发布内容加自动编号：别改写标题文本（锚点会断），用 CSS 计数器 | #前端 #内容站 #SEO |
| F-15 | 动效先算「浏览器覆盖 × 交互频率」，再想 reduced-motion 的兜底 | #前端 #动效 #可访问性 |
| F-16 | 中文内容站的阅读时长口径：构建期与渲染期两套算法，数字必然对不上 | #前端 #内容站 #i18n |
| F-17 | 静态导出站（basePath + .html）里别用 usePathname() 推导链接 | #前端 #Next.js #静态导出 #hydration #链接 |

### F-01 占位状态显式建模：绝不把占位文本当结果
- 场景：#异步 #前端
- 问题：推进事件后 5 秒看到 `pending_enrich` 占位文本，18-30 秒后才被真实结果替换，期间占位文本被当成了"结果"渲染。
- 根因：后端 O(1) 推进先写占位、异步 enrich 后补真实内容；前端乐观更新没识别占位状态，也无轮询。
- 方案：三件套——
  1. 前端检测 `parsed.status === 'pending_enrich'` 走"生成中"fallback 分支（显示进行中，**不是**"生成失败"）；
  2. refresh 合并数据时跳过 server 端 placeholder，防止把真实结果覆盖回占位；
  3. 推进后启动轮询（`5s × 6 = 30s`）拉取真实 enrich 结果。
- 反模式：把占位字符串直接渲染给用户；轮询无上限。
- 溯源：2026-07-06_pending_enrich_optimistic_bug.md、2026-07-06_stage_summary.md

### F-02 用户 override 必须写回 DB
- 场景：#异步 #后端 #DB
- 问题：用户点"复杂推进"，后端内存里 `complexity` 改了，但 enrich 后台任务读 DB 拿到的还是 `simple`，产出仍是简单档。
- 根因：内存变量与持久化状态分离；异步任务只信 DB。
- 方案：`update_event_result` 增加 `complexity` 参数写回 DB；调用时 `complexity=complexity if mode in ("simple","complex") else None`。
- 通用规律：用户的模式/偏好选择是**持久状态**，不是函数内临时变量。
- 溯源：2026-07-06_mode_override_complexity_persistence.md

### F-03 决策点阻塞条件要与"用户主动"解耦
- 场景：#后端 #业务逻辑
- 问题：用户主动选择"复杂推进"时，决策点被跳过，直接出结果。
- 根因：阻塞条件写成 `mode is None`（即只有自动推进才停决策点），用户主动选择反而绕过了决策。
- 方案：改为 `not user_decision`——是否阻塞只看"用户是否已做过决策"，与触发方式无关。
- 溯源：2026-07-06_complex_event_progression.md

### F-04 乐观更新 + 新鲜度标记
- 场景：#前端 #UX
- 问题：推进后等待 refresh 期间用户重复点击、状态错位。
- 方案：前端立即乐观更新 pending→completed，保留 `_isNew` 高亮标记（chip 样式），新事件 chip 点击可跳转到详情页并自动滚动；等待后端 refresh 校准。
- 溯源：2026-07-05_chat_event_optimistic_chip.md

### F-05 跨源刷新与 stale 保护
- 场景：#前端
- 问题：从其他页面/标签页回来后事件时间线不刷新；刷新失败时把已有数据清空。
- 方案：
  1. 抽取统一 `refreshActiveEvents`，监听 `visibilitychange` / `pageshow` 做跨源刷新；
  2. 展示型数据刷新失败时**保留旧数据**（stale 好过空白）；
  3. 后端 CRUD 过滤参数（如 `day_number`）改可选，宽松调用语义避免上层调用分叉。
- 反模式：刷新失败 catch 里 setState([])。
- 溯源：2026-07-03_chat_event_progression.md

### F-06 序列化完整性：API 字段与前端契约
- 场景：#后端 #API设计
- 问题：`_serialize_event` 漏字段，前端拿不到关键属性静默出错。
- 方案：新增字段时同步排查所有序列化出口；跨天查询统一语义（`day_number` 可选）。
- 溯源：2026-07-03_chat_event_progression.md

### F-07 rAF 循环双重调度 → 后继帧指数多开
- 场景：#前端 #动画 #rAF
- 问题：待机巡视动画的位置更新速度指数增长，画面抽搐。
- 根因：loop 开头 `raf = 0` 后，循环体内的分支（如巡视推进）又调用 `schedule()` 排下一帧——每 tick 产生 2 个后继，指数多开。
- 方案：`ticking` 标志位——`schedule()` 在 tick 执行期间拒排；循环末尾由 loop 自己续帧。凡"rAF 循环 + 任意路径可触发 schedule"的结构都要有这个闸。
- 反模式：只用 `raf` 一个变量防重排，忽略 tick 进行中的窗口期。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md

### F-08 smoothDamp 的位移钳制必须外置，放 damp 内部会破坏阻尼动力学
- 场景：#前端 #动画 #数值方法
- 问题：限速后平衡状态爬行（高刷屏下 ~10fps 级移动），与 maxSpeed 取值无关。
- 根因：`maxChange = mSpeed * dt` 钳制放进 damp 内部后，dt 越小钳得越死，阻尼动力学被破坏——平衡速度与 maxSpeed 脱钩且随 dt 减小变慢。
- 方案：damp 内部保持纯阻尼；限速外置为位移钳制：`maxStep = mSpeed * dt; step = clamp(out[0] - pos, ±maxStep)`。
- 反模式：把限速逻辑塞进阻尼函数"一步到位"。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md

### F-09 收敛自停的 rAF 响应不了非输入事件的状态变化
- 场景：#前端 #动画 #rAF
- 问题：面板打开后动画不回正，动一下鼠标才恢复。
- 根因：动画收敛后 rAF 自停省电（正确设计），但 class 切换等非 pointer 事件没人唤醒循环。
- 方案：MutationObserver 监听目标元素 `class` 属性变化 → `schedule()` 唤醒；同理 visibilitychange 唤醒/暂停。
- 反模式：给所有状态变化都挂 pointermove 监听兜底；或干脆不收敛、让 rAF 空转。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md

### F-10 CSS 3D 残留（preserve-3d + translateZ）使 DOM 顺序层级失效
- 场景：#前端 #CSS #视觉bug
- 问题：新覆盖层（DOM 更后、z=0）被旧元素盖住——图标"透"到上层图像中间；删掉新层旧元素又正常。
- 根因：父级残留旧方案的 `transform-style: preserve-3d`，子级残留 `translateZ(14px)`——3D 空间中按 z 轴距离排序，**DOM 顺序失效**，z=14px 的旧元素永远在新层之上。
- 方案：替换视觉方案时全局搜索旧方案的专属属性（preserve-3d/translateZ/rotateY 等）一并清理；被覆盖的底元素在顶层就绪后 `visibility:hidden`（保留解码前降级）。
- 反模式：只加新层不改旧样式，靠 DOM 顺序想当然；用更高 z-index 硬顶（在 preserve-3d 下无效）。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md


### F-11 React 18 批处理会吃掉"成功提示"：异步后的子 setState 与父 setState 同批渲染
- 场景：#React #状态 #UX
- 问题：点按钮 → 请求成功 → `setResult('成功了…')` 并通知父组件刷新数据；结果承载提示的引导块**整体卸载**，"成功"这行字从未上过屏。端到端测试卡在等待该文案、超时（表现为"疑似功能坏了"）。
- 根因：await 之后的两次 setState（子组件 `setResult` 与父组件 `setHealth`）被 React 18 **自动批处理进同一次渲染**；父级状态一变，条件渲染的子组件当场卸载，提示来不及渲染。
- 方案：成功提示要"**先让用户看见，再刷新会卸载它的那个状态**" —— `setResult(...)` 之后用 `setTimeout(onRefresh, 900)` 延后刷新；或把提示上提到不会被卸载的父级/全局（toast）。
- 反模式：在会被卸载的组件里显示成功态、并立刻触发那个会卸载它的刷新；用"反正界面变了就算成功"糊过去（用户和自动化都看不到反馈）。
- 溯源：flowwatch 首启引导的「重新检测」按钮（2026-09-23/24，`web/src/components/CaptureGuide.tsx`）。

### F-12 Tailwind 变体类不在 classList 里：写"没有的那个类"的选择器是死代码
- 场景：#前端 #CSS #Tailwind #深色模式
- 问题：模板 CSS 里 `.prose-invert { … }` 一整套深色覆写**从未命中** —— 深色模式下引用块、`strong`、行内代码的配色一直是错的，而且**没有任何报错**（纯静默失效，只能靠肉眼比对发现）。
- 根因：DOM 上的字面类名是 Tailwind 变体 `dark:prose-invert`，`classList` 里**根本没有 `prose-invert` 这个类**；按"类名"字面写选择器就永远匹配不上（源顺序/优先级再调也没用）。
- 方案：覆写改用 `.dark .prose`（`<html>` 上有 `.dark`）—— 稳定命中，且特异性（0,2,1）高于 `.prose`，不依赖源顺序。
- 反模式：把"样式没生效"先归因于加载顺序/缓存，去加 `!important` 或调整文件顺序；正确第一步是**去 DOM 里核对实际类名**（变体类、`data-*`、哈希类名都会骗过你）。
- 溯源：TechLog 文章页改版（2026-09-28，`css/tailwind.css`）

### F-13 内联元素的负 margin 会减少"内联前进量"：给标题前置图标加负 margin，把标题文字整体带偏
- 场景：#前端 #CSS #布局
- 问题：用 CSS 计数器给标题加编号后，想顺带把悬停才出现的锚点图标挪到编号左侧，于是加大图标的负 `margin-left`；结果**标题文字整体左移 68.8px**，正好压住编号 —— 现象看起来像"CSS 计数器没生效"。
- 根因：图标包在一个内联 `<a>` 里，负 margin 直接**减少内联前进量**（inline advance），后续文字跟着左移；而 `::before` 生成的计数器框还在原位，于是文字盖住了数字。
- 方案：保持 `margin-left ≈ 图标自身宽度`（advance = 0），图标自然落进编号框右侧的空白里；验收这类"看不见的伪元素"要测 `getComputedStyle(el, '::before').width` —— **别只看 `content`**（Chrome 返回未解析的 `counter(h2counter) "."`，看着像没生效）。
- 反模式：肉眼看到"编号/图标没出来"就直接去改计数器或内容规则；用"再加大负 margin"调位置（图标的 advance 会继续吃掉文字宽度）。
- 溯源：TechLog 自动章节编号（2026-09-29）

### F-14 给已发布内容加自动编号：别改写标题文本（锚点会断），用 CSS 计数器
- 场景：#前端 #内容站 #SEO #兼容性
- 问题：要给站内 27 篇文章自动加章节编号，但这些文章已有对外深链（`#<slug>`）与运行期生成的目录。
- 根因：编号一旦写进标题文本，会同时牵动**两处权威源** —— 锚点 id（`rehype-slug` 基于标题文本）与目录（pliny 从 **raw markdown** 提取 `toc`）；插件顺序稍错就会让 id 变化、外部深链全断，而目录侧仍旧拿不到编号、与正文不一致。
- 方案：正文编号用 **CSS 计数器**（`::before` + `counter()`，不改 HTML）；目录侧用**同一套规则在运行时算**（`numberToc()`）保证两边一致；是否启用由构建期判定（正文已有人工编号「一、/ 1.」的文章整体关闭，避免双重编号）。
- 反模式：为了"编号能进正文文本"去动 AST 插节点，用已发布的深链换一个无关紧要的好处；正文与目录各写一套编号逻辑（必然错位）。
- 溯源：TechLog（2026-09-29，`lib/headingNumbering.ts` + `css/tailwind.css` 的 `.auto-numbered`）

### F-15 动效的两笔账：先算「浏览器覆盖 × 交互频率」，再想 reduced-motion 的兜底
- 场景：#前端 #动效 #可访问性 #决策
- 问题：想给主题切换加"从点击位置圆形扩散"（View Transitions）动效；同时发现全站**没有任何 `prefers-reduced-motion` 处理**，而 `<html>` 上全局开着 `scroll-smooth`。
- 根因/判据：① **覆盖** —— View Transitions 只有 Chrome/Edge 支持，Firefox 与 Safari 稳定版都没有，"读者多用 Safari"的站点等于白做；② **频率** —— 主题默认跟随系统，多数访问根本不会点开关，低频交互的设计回报天然低；③ **定位** —— 编辑级克制的站点里，全页色块擦除更接近装饰而非交互逻辑。
- 方案：**不做**这个动效并记录理由（避免以后重复论证一遍）；把力气转去补真问题 —— 在 `@media (prefers-reduced-motion: reduce)` 里关掉 `scroll-behavior: smooth` 与抽屉/菜单过渡（浏览器**不会**因为你声明了 reduced-motion 就自动停掉平滑滚动，必须自己关）。
- 反模式：因为"好看 / 能展示技术"就上动效，不看浏览器覆盖与交互频率；只做一半的 reduced-motion（禁掉了逐个动画，却留着全局平滑滚动）。
- 溯源：TechLog 站内改版（2026-09-29）

### F-16 中文内容站的阅读时长口径：构建期与渲染期两套算法，数字必然对不上
- 场景：#前端 #内容站 #i18n #构建期
- 问题：首页/列表卡片显示「5,210 字 · 27 min read」，文章页显示「阅读约 N 分钟」——同一篇内容的时长在站内以**两种语言、两个数字**并存；全站 27 篇文章都如此。
- 根因：两套口径。首页/列表吃 contentlayer **构建期** computed field（用的是 `reading-time` 这个英文模型库，中文被按"英文单词 / 200 每分钟"估算）；文章页用仓库里自写的 `lib/wordCount`（渲染期，CJK 300 字/分钟 + 英文 200 词/分钟）。同一个事实被两个算法各算一遍，还各配一种语言的文案。
- 方案：**构建期与渲染期共用同一份实现**——`contentlayer.config.ts` 的 `readingTime` computed field 改为 `import { countWords, readingTime } from './lib/wordCount'`，产出 `{ text: '阅读约 N 分钟', minutes, words, time }`；首页、列表、文章页全部渲染这同一份数据。
- 反模式：给中文站直接套英文阅读时长库（`reading-time` 等）就当口径可用；同一展示事实在构建期与渲染期各写一版（必然漂移）；发现两处数字不一致时只改一处文案，不统一源头。
- 溯源：TechLog 文章页改版（2026-09-28，`lib/wordCount.ts` + `contentlayer.config.ts`）

### F-17 静态导出站（basePath + .html）里别用 usePathname() 推导链接：SSR/CSR 值不一致，客户端点击必 404
- 场景：#前端 #Next.js #静态导出 #hydration #链接 #basePath
- 问题：列表页底部点「下一页」跳到 `blog.html/page/2.html`（把 `.html` 当成了目录段）→ 404；SSR 输出的 href 与 DOM 属性看起来都对，console 也没有 hydration 报错，只有**点击**才炸。
- 根因：`usePathname()` 在**客户端**返回带 basePath 前缀与 `.html` 后缀的真实 URL（`/techlog/blog.html`），在**服务端**返回路由路径（`/blog`）。用 `replace(/\/page\/\d+$/,'')` 剥分页段时 `.html` 剥不掉 → 拼出 `<list>.html/page/N.html`。两处不一致时 React 19 会保留服务端 DOM（attribute 仍是旧值），但点击走 hydration 后客户端树的值 → 必 404。判据：点击瞬间的 RSC 请求 URL 里能看到 `/blog.html/page/2.html.txt?_rsc=...`。
- 方案：链接根路径**显式 prop 传入**（服务端已知，如 `basePath="/blog"`、`/tags/<slug>`），组件不依赖 usePathname；侧栏激活态同理（`activeTag` prop）。验证必须在「静态导出 + BASE_PATH + 前缀目录托管」形态下点一遍：`EXPORT=1 BASE_PATH=/techlog` 构建后把 `out/` 挂到 `<root>/techlog/` 用静态服务器复刻线上 URL 形态。
- 反模式：用 usePathname() 推导站内链接；用 dev server 验证线上 URL 形态问题（dev 下不加 .html、也没有 basePath 后缀，复现不了）；只看 SSR 输出正常就认为没事。
- 溯源：2026-10-03 TechLog 分页 404 修复（同批修 tag 页分页与侧栏高亮；见 usercontext/2026-10-03.md）
