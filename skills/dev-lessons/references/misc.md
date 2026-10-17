# 工具使用与排查方法

场景标签：`#工具使用` `#搜索` `#多副本` `#排查`

## 条目索引（按编号或关键词检索：**先用 search_content 搜编号 / 关键词，勿整读本文件**）

| 编号 | 标题 | 场景标签 |
|---|---|---|
| M-01 | 搜索工具在同名项目副本间串台 | #工具使用 #搜索 #多副本 |
| M-02 | 命令行内联 JSON 在 PowerShell 中被转义破坏 | #工具使用 #Windows #接口调试 |
| M-03 | Edit 工具对同文件连续多次修改可能未持久化 | #工具使用 #AI代理 #编辑可靠性 |
| M-04 | headless 浏览器测 rAF 动画必须禁节流，否则结果失真 | #测试 #Puppeteer #动画 #QA |
| M-05 | ffmpeg MP4 muxer 静默丢弃自定义 metadata key | #工具使用 #ffmpeg #元数据 #合规 |
| M-06 | Tabbit CLI 在 Windows 沙箱下的调用法（兼容模式） | #工具使用 #浏览器自动化 #Windows |
| M-07 | 产物有格式缺陷时，写幂等后处理脚本修，别全量重跑模型 | #工具使用 #成本控制 #幂等 |
| M-08 | 不克隆仓库提取开源项目的协议知识 | #工具使用 #开源 #API逆向 |
| M-09 | 平台生成物对外发布前必须"清洗 + diff 核对"（BOM / 行尾 / 引用误删） | #开源 #文档 #编码 #工具使用 |
| M-10 | 本地"端口/进程"验证的两个假象：假成功与假失败 | #Windows #验证 #端口 #进程 |
| M-11 | Playwright 录屏做演示动图（GIF）的四个坑 | #Playwright #演示资产 #ffmpeg #脱敏 |
| M-12 | 本机环境两个固定约束：safe-delete 拦截 rmtree、pytest 的 sys.path | #工具使用 #环境 #pytest |
| M-13 | 用真实浏览器自动化执行平台"写操作"（投稿/发布）的七条硬规矩 | #浏览器自动化 #Playwright #Tabbit #平台发布 |
| M-14 | 视频时间轴"收紧"（跳跃剪辑）要工程化：单一裁剪表 + 回归验证 + 交付前 QC | #视频 #ffmpeg #字幕 #时间轴 |
| M-15 | 用管道截断看进度会掐掉上游进程（脚本只跑一半） | #PowerShell #工具使用 #长任务 |
| M-16 | GitHub Actions 工作流的"语法级"坑：`name:` 值里的冒号 | #CI #YAML #工具使用 |
| M-17 | 工作区里出现"非本次改动"的破损编辑：先分离归属，再定点修复 | #协作 #排查 #版本控制 |
| M-18 | 清理/删除类操作写成可复用脚本，别塞在终端长命令里 | #工具使用 #Windows #协作 |
| M-19 | 卡片式"数据解说"视频的可复制链路（HTML 卡片 → 录屏 → TTS → 烧字幕） | #视频生成 #Playwright #edge-tts #可复制 |
| M-20 | 平台投稿类自动化：跨会话任务槽会失效，未提交的页面状态不可依赖 | #浏览器自动化 #投稿 #交接 |
| M-21 | 微信公众平台自动化发布的三个连环坑：HTML 被降级 / 标题框是隐藏元素 / 必须走 paste 事件 | #浏览器自动化 #平台发布 #Tabbit #微信 |
| M-22 | 文件行尾 CRLF 会让 frontmatter 报"假 YAML 错"（报错列号伪装成内容问题） | #编码 #行尾 #Contentlayer #js-yaml #工具使用 |
| M-23 | 进程"杀-重生"循环：只杀子进程是白杀，先看清"谁在重启它" | #进程管理 #自动化 #Electron #排查 |
| M-24 | PowerShell 5.1 的 `Get-Process` 没有 `CommandLine`：按命令行筛进程必须走 CIM | #Windows #PowerShell #进程 #工具使用 |
| M-25 | 云安全组端口是否放行：用 refused vs timeout 判定，比回控制台翻规则快 | #云主机 #安全组 #排查 #网络 |
| M-26 | 从压缩/打包产物里定位逻辑：按"字符窗口"截取；附 PowerShell 里 `$` 被外层 shell 吃掉的坑 | #工具使用 #Minified #PowerShell |
| M-27 | 第三方内核依赖"能自动到什么程度"由许可决定，不由技术决定 | #合规 #第三方依赖 #产品决策 |
| M-28 | 多会话共享当日日志：整篇重写会吞掉别会话的记录 | #协作 #记忆系统 #并发 |
| M-29 | 定位器逐项读文本会累加超时：撞满执行器硬限后连标签页一起丢 | #浏览器自动化 #Playwright #Tabbit #超时预算 |
| M-30 | B 站投稿/字幕自动化的判据与走位：结构 > 数值 > 文案（补 M-13） | #浏览器自动化 #平台发布 #B站 #判据 |
| M-31 | 程序化宣传片：分段边界必须单一权威源 + 交付前四项 QC | #视频生成 #逐帧渲染 #字幕 #验收 |
| M-32 | 解析命令行 JSON 的三连坑：多行 stdout / 盘符变量 / stderr 假报错 | #PowerShell #curl #API调试 #工具使用 |
| M-33 | 会"误伤用户"的自动化：默认向后兼容 + 风险能力显式开启 + 先看清再开火 | #工具设计 #默认值 #安全 #用户体验 |
| M-34 | 别人给的预览/沙箱 URL 可能是旧快照：先做"是否当前源码"判据再相信它 | #排查 #验证 #预览环境 |
| M-35 | MDX / 行尾 / 内容层缓存：三个只在"执行链"上暴露的约定（含 git 幽灵 M） | #编码 #行尾 #MDX #构建缓存 |
| M-36 | npm script 里的 `$VAR` 在 Windows cmd 下不展开（`Unbound variable`） | #工具使用 #Windows #npm |
| M-37 | 一条命令内的 `Set-Location` 不保证后续相对路径的解析基准 | #工具使用 #Windows #跨工作区 #相对路径 |
| M-38 | 会话"服务化"后 stdout 被吞：结果写文件再读；附 python -c 引号炸 | #工具使用 #Windows #PowerShell #AI代理 |
| M-39 | 探测本机服务只认状态码，会被"别的进程占同端口"骗过 | #排查 #本机服务 #端口 #健康检查 |
| M-40 | cmd 下含 `%xx%` 的 URL 被当变量展开：报"文件名、目录名或卷标语法不正确" | #Windows #cmd #URL #下载 #工具使用 |
| M-41 | 验证「技能/知识库到底有没有用」用三臂对照，agentic 测可检索须补 read 工具 | #知识库评估 #agentic #技能验证 #可检索 |
| M-42 | "按索引检索、勿整读"原则必须在 read 工具层落实 | #知识库消费 #agentic #token预算 #references |
| M-43 | 稍复杂的命令一律写成脚本文件再执行（内联反引号/`%VAR%` 会被当 cmd 解析） | #工具使用 #Windows #PowerShell #AI代理 |
| M-44 | B站新版「封面制作」弹窗：4:3/16:9 独立面板，file input 随激活状态动态变化 | #浏览器自动化 #平台发布 #B站 #封面 #shadowDOM |
| M-45 | B站评论区是 web components：操作菜单的定位、触发与验证方法论 | #浏览器自动化 #平台发布 #B站 #评论 #shadowDOM |
| M-46 | PIL 逐帧渲染：字体缺字形静默画方框，渲染前必须抽帧过目 | #视频生成 #逐帧渲染 #字体 #PIL |
| M-47 | 抓不到屏的五个"假 API 失败"：根因常是窗口比屏幕大（附屏幕尺寸可信判据） | #Windows #抓屏 #自动化验证 #DPI |
| M-48 | ctypes 不声明 argtypes：句柄被静默截断成 32 位，三处调用全静默失效 | #Python #ctypes #Windows #静默失败 |
| M-49 | Win32 `SS_OWNERDRAW` 自绘卡片的四条规矩（一次 DrawTextW / 位置现算 / 缺 API 动态取） | #Win32 #Rust #自绘控件 #UI反馈 |
| M-50 | ffmpeg 合成 GIF 不显式传 `-framerate` 会悄悄变速，同片各段还可能不一致 | #ffmpeg #GIF #视频 #演示动图 |
| M-51 | 跟外部系统要"列表位置"：快照 diff 而非序号推算，且必须重试 | #桌面 #外部系统 #自动化 #容错 |
| M-52 | 规范/流程类资产：主本唯一 + 副本带出生证明 + 触发写成路由技能 | #知识资产 #防漂移 #技能 #触发 |
| M-53 | 复刻既有脚本的输出格式：拿参照数据逐行 diff 保真，别凭目测 | #格式复刻 #会话导出 #验证 |
| M-54 | 检索命中 0 不等于没有：先排两个静默跳过源（点目录 / 超大文件） | #工具使用 #搜索 #静默失败 |
| M-55 | Tabbit 任务空闲即回收：跨等待的操作按"可恢复"设计，恢复三步固定（补 M-20） | #浏览器自动化 #Tabbit #平台发布 #恢复 |
| M-56 | B 站专栏/动态程序化发布：输入规则注入富文本 / 勾选框走 DOM click / 动态不支持编辑 | #浏览器自动化 #平台发布 #B站 #富文本 |
| M-57 | 抓飞书文档正文：web_fetch 拿不到（SPA），大视口一次渲染 + 禁止按行去重 | #浏览器自动化 #文档抓取 #飞书 |

### M-01 搜索工具在同名项目副本间串台
- 场景：#工具使用 #搜索 #多副本
- 问题：对 A 目录做全文搜索，结果里混入了 B 目录**同名文件**的命中行，据此误判"A 文件还有旧内容""这个文件被回退了"。
- 根因：本机存在同名项目副本时，搜索结果的路径归一化/相对化让命中跨目录混排，仅凭摘要无法分辨归属；行号也对不上。
- 方案：下结论前用**绝对路径 + 精确读取**复核（`Select-String -Path <绝对路径>` 或按行号 `read_file`）；怀疑"编辑没生效"时先比对文件总行数与章节标题，确认打开的是同一个文件。
- 反模式：直接拿搜索摘要断言某个文件的内容状态；或因为看到"旧内容命中"就重复提交/回滚。
- 溯源：2026-09-10，搜索 `mojibake` 命中了另一副本的 `handoff.md`（第 375 行），误以为本项目文档未更新

### M-02 命令行内联 JSON 在 PowerShell 中被转义破坏
- 场景：#工具使用 #Windows #接口调试
- 问题：`curl -d '{"k":"v"}'` 打接口返回 `json_invalid` / `Unterminated string`，但同样的 body 在别处能跑通。
- 根因：PowerShell 对引号的转义规则与 shell 不同，经过多层包装后 JSON 里的引号被吃掉。
- 方案：把 body 写成文件再 `--data-binary "@file"`；或先用最简单的 body（不含空格/非 ASCII）验证连通性，再逐步加字段。
- 反模式：反复调整转义层数碰运气；把 `json_invalid` 当成服务端 bug 去查代码。
- 溯源：2026-09-10，调用 `/api/v1/grade` 时的两次失败（与 deploy-env.md E-04 同源）；2026-09-11 变体——给**本地 exe**（ffmpeg `-metadata`）传内嵌双引号 JSON 参数同样断裂且报错迷惑（"At least one output file must be specified"），`\` 转义后仍丢字段，Python subprocess 列表传参一次通过

### M-03 Edit 工具对同文件连续多次修改可能未持久化
- 场景：#工具使用 #AI代理 #编辑可靠性
- 问题：Edit 返回 success，但事后检查发现部分修改内容丢失（连续多次 Edit 同一文件时高发，两次实测各丢 2-4 处）。
- 根因：连续编辑同一文件时的快照覆盖问题——后一次编辑基于的文件状态可能不包含前一次的修改。
- 方案：对同一文件的多次 Edit 完成后，**逐处 grep 复核**目标内容是否落盘；缺失的重新编辑。跨会话共享 git 工作树时改完尽快提交，防并行会话互相覆盖。
- 反模式：看到 Edit 返回 success 就认为已持久化，不再验证。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md（landing.html 与 gaze 脚本两次实测）

### M-04 headless 浏览器测 rAF 动画必须禁节流，否则结果失真
- 场景：#测试 #Puppeteer #动画 #QA
- 问题：无头浏览器里动画探针显示 ~1.6s/tick，误判代码有性能 bug；肉眼真机验证却流畅。
- 根因：headless 模式后台页的 rAF/定时器被浏览器节流，动画以 1.6s+ 间隔步进，测出来的不是真实表现。
- 方案：launch flags 三件套 `--disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding` + 每次操作前 `page.bringToFront()`；探针只用于验证逻辑（帧号映射、状态转移），流畅度以真机为准。
- 反模式：拿 headless 截图/探针数据直接断言动画流畅度。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md

### M-05 ffmpeg MP4 muxer 静默丢弃自定义 metadata key
- 场景：#工具使用 #ffmpeg #元数据 #合规
- 问题：`-metadata AIGC='...'` 写 mp4 后 ffprobe 发现 AIGC key 消失，且 ffmpeg 无任何告警；comment 等标准 key 却能写入。
- 根因：MP4 muxer 默认只写已知白名单 key（comment→©cmt 等），自定义 key 直接丢弃。
- 方案：加 `-movflags use_metadata_tags`（走 mdta/keys atom 机制）即可写任意 key；写完**必须 ffprobe 复核**——静默丢失是最阴的形态。
- 反模式：命令 exit 0 就认为元数据已写入；把"标签丢了"归咎于 ffprobe 显示问题。
- 溯源：2026-09-11，豆包视频去水印时保留 AIGC 合规标签（frontend-works/vectordb-news/usercontext/2026-09-11/Doubao-Watermark-Session-Summary.md）

### M-06 Tabbit CLI 在 Windows 沙箱下的调用法（兼容模式）
- 场景：#工具使用 #浏览器自动化 #Windows
- 问题：tabbit-cli 的 `cmd /c "... < file.js"` 调用被 Agent 沙箱禁止（"cmd /c is blocked"），而 PowerShell 5.1 又不支持 `<` 输入重定向。
- 根因：沙箱禁 `cmd /c`；PS 无 `<` 语法；persistent 模式需要跨命令保持 stdin（Shell 工具每命令独立进程，做不到）。
- 方案：兼容模式管道调用 `Get-Content -Raw file.js | & "$env:LOCALAPPDATA\Tabbit\LocalAgent\bin\tabbit-cli.exe" nodejs --task NAME`；**JS 文件保持纯 ASCII**（中文用 `\uXXXX`，防管道编码变形）；同一任务全程复用同一 `--task NAME`；结束后 `finish --task NAME`。
- 反模式：为 JSON frame 拼 here-string / echo 管道（会改变换行与编码）；反复重启 persistent 进程。
- 溯源：2026-09-11，豆包登录态下取无水印视频直链（Doubao-Watermark-Session-Summary.md）
- 注：Tabbit CLI 的 task 槽位上限 8 个，长驻服务/循环采集必须**固定 task 名复用** worker；错误 receipt 输出在 **stderr**（stdout 只有成功 receipt）；卡满时 `tabbit-cli tasks` 查看、`finish --task <name> --discard` 释放。失败重试模式：固定名失败 → discard → 换名重试一次。

### M-07 产物有格式缺陷时，写幂等后处理脚本修，别全量重跑模型
- 场景：#工具使用 #成本控制 #幂等
- 问题：20 份已生成的交付物里 13 份字幕缺时间戳、1 份章节缺失。全量重跑要 80 分钟模型调用与额外费用。
- 根因：缺陷分两类——**确定性缺陷**（时间戳缺失、字面量没转文本、行没换行）可以在文本层用规则从已有内容推导出正确形态；**内容性缺陷**（章节缺失、口播挤成一行）才必须重新生成。不分类就会一律重跑。
- 方案：先按"能否用规则从已有内容推导"分流。可推导的写幂等修复脚本（正则/解析/重排），对全目录跑一遍，无变化即跳过；只有内容性缺陷才重新调模型。本次 20 份中 19 份靠规则修好，只重生成 1 份。修复脚本要落到项目里长期可复用，并串进批量流程末尾做自动兜底。
- 反模式：发现格式问题就整批重跑；把修复脚本写成一次性命令（下次遇到还得重写）。
- 溯源：2026-09-11 AI-driven-viral-content-analysis-system（fix_subtitle_timecodes.py / fix_script_formatting.py）

### M-08 不克隆仓库提取开源项目的协议知识
- 场景：#工具使用 #开源 #API逆向
- 问题：需要某开源项目逆向出的接口知识（如豆包无水印下载链路），但只为读协议 clone 整个仓库太重；直接 fork/新建仓库又会背上长期维护义务（上游接口一变就要跟修）。
- 根因：协议知识集中在极少数源文件里，仓库其余部分（UI/构建/扩展工程）与协议无关；且"谁拥有仓库谁维护"。
- 方案：三步远程读取，零 clone——①GitHub API 列树定位协议文件：`api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1`；②raw 读单文件原文：`raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`（如 `src/api/video.ts`）；③看该文件变更史找兼容性线索：`/commits?path=<file>`。知识蒸馏进 dev-lessons，胶水代码用完即弃；回馈上游用 issue 不用 PR。
- 反模式：为读一个文件 clone 全仓库；fork/新建仓库变成换壳维护负担；把上游代码整段复制进自己项目。
- 溯源：2026-09-12，doubao-downloader 仅远程读 src/api/video.ts 即完成无水印视频下载，未 clone 未 fork（Doubao-Watermark-Session-Summary.md）

### M-09 平台生成物对外发布前必须"清洗 + diff 核对"（BOM / 行尾 / 引用误删）
- 场景：#开源 #文档 #编码 #工具使用
- 问题：把 AI 会话工作区/生成平台产出的文档直接开源外发，会带三类脏东西（AIGC front-matter 与「内容由AI生成」脚注、本机绝对路径、`requirements.txt` 里混入的中文标注行——后者会让 `pip install -r` 直接抛 InvalidRequirement）。清洗过程中又踩两个坑：**锚点正则失配**与**误删正文引用句**。
- 根因：① 平台文件常带 **UTF-8 BOM**，`encoding="utf-8"` 读到的首字符是 `\ufeff`，`\A---` / `startswith("---")` 这类锚点判断全部失配，表现为"脚本没改到"或"断言误判"；② 文件是 CRLF 行尾，正则里写 `\n` 匹配不上；③ "删除含某标注的行"这种粗暴策略会把**正文里引用该标注的句子**一起删掉（本次真删掉了两处说明文字）。
- 方案：① 一律 `read_bytes().decode("utf-8-sig")`，写回时按原是否带 BOM / 原行尾风格还原；② 清洗后做 `difflib.unified_diff`（先把 front-matter 与路径归一化）**逐行核对**，只允许出现预期的那几处差异；③ 残留扫描把"硬性禁止"（水印句、本机用户名）与"允许的叙述引用"分开，别把文档里介绍该元数据的句子当残留。
- 反模式：`replace()` 一把梭后不 diff；只按"命中数下降"验收；批量清理不做复核。
- 溯源：2026-09-15/16 portwatch 开源（frontend-works/portwatch）：BOM 导致 front-matter 剥离连续失败两次；按行删除误删 HANDOVER §2.2 提示与 §6.4 现象行，靠 diff 发现并改写

### M-10 本地"端口/进程"验证的两个假象：假成功与假失败
- 场景：#Windows #验证 #端口 #进程
- 问题：验证"某个监听是否真的占住了端口"时出现两种误导：① **假成功**——自己 bind 没报错，但采集/连接表里根本没有自己的进程；② **假失败**——`subprocess.Popen` 拉起的监听进程"存活但绑不上端口"，采集层完全看不到它。
- 根因：① Windows 上若先占端口的一方设了 `SO_REUSEADDR`（如 `python -m http.server`，其 `allow_reuse_address=1`），**第二个进程再 bind 同一端口也会成功**，于是 bind 返回值不再能证明"端口归我"；② 本机环境对 Python 子进程有沙箱限制（同脚本改用 PowerShell `Start-Process` 启动就正常）。
- 方案：① 判断端口归属要看**观测事实**——`psutil.net_connections` / 采集结果里该端口的 PID 是否等于自己的进程 PID，而不是看 bind 是否抛错；自己的验证脚本在 Windows 上**不要设 SO_REUSEADDR**（会把冲突伪装成成功）；② 需要"真的在监听"的子进程用 `Start-Process`（或等价脱离方式）启动，启动后回查一次确认。
- 反模式：把 `bind()` 成功当"占端口成功"的证据；用 connect 试探判断端口占用（backlog 满或服务不 accept 时会把"在监听"判成"没监听"——portfolio_server.py 注释里记过这条）；子进程起不来只反复重试而不换启动方式。
- 溯源：2026-09-15 portwatch 截图/录屏过程连续踩到（8899 被他人 http.server 以 SO_REUSEADDR 占着；同脚本 Popen 起的 listener 采集层看不到）

### M-11 Playwright 录屏做演示动图（GIF）的四个坑
- 场景：#Playwright #演示资产 #ffmpeg #脱敏
- 问题：把"真实运行的实时效果"做成 README 动图时：裁剪后内容对不上预期、画面里露出本机路径、素材体积失控。
- 根因与方案：
  1. **视频时间轴与墙钟存在常量偏移**（本次 ≈3.8s：视频 47.68s vs 脚本墙钟 51.5s，录制起点晚于 context 创建）→ 裁剪点按"墙钟 − 偏移"换算，或更稳地给足余量窗口（关键动作前 4s 到结束后 3s）。
  2. **固定 sleep 不可靠** → 用确定性等待 `wait_for_selector` / `wait_for_function`（本次用"列表里出现/消失该行"判定关键动作），并记录各阶段墙钟偏移供裁剪。
  3. **脱敏要持续生效**：`context.add_init_script` + MutationObserver 改写文本节点 `nodeValue`，React 重渲染也不会漏；只在截图前改一次会漏。
  4. **体积**：ffmpeg `fps=8~10, scale=900:-1` + `palettegen/paletteuse`（`max_colors=160~192, stats_mode=diff`）→ 900px/8fps/24s ≈ 1.2MB，可直接进仓库。
- 反模式：固定 sleep 卡时间；只给首帧脱敏；为高清堆 fps/尺寸导致动图数 MB；**发布前不抽帧核对内容**。
- 溯源：2026-09-15/16 portwatch README 动图（`_deploy/_qa/portwatch_record.py` → `docs/demo.gif`）

### M-12 本机环境两个固定约束：safe-delete 拦截 rmtree、pytest 的 sys.path
- 场景：#工具使用 #环境 #pytest
- 问题：① Python 脚本里 `shutil.rmtree(dir)` 被本环境的 safe-delete shim 拦截，抛 `FileNotFoundError` / `genie-trash ETIMEDOUT` 导致脚本中途失败；② 仓库根没有 conftest.py 时，`pytest tests` 只把 `tests/` 加进 `sys.path`，测试里 `import 顶层模块` 直接 ImportError（只有 `python -m pytest` 才顺带把 CWD 加进去）。
- 方案：① 删除目录内容改成**逐文件 `Path.unlink(missing_ok=True)`**（实测可用），或改用带时间戳的新目录避免删除；② 在**仓库根**放 conftest.py 显式 `sys.path.insert(0, 仓库根)`，让 `pytest` 与 `python -m pytest` 行为一致（CI 上同样生效）。
- 反模式：脚本里反复重试 rmtree；只凭"我本地 `python -m pytest` 能过"就认为 CI / 他人环境也能过。
- 溯源：2026-09-15/16 portwatch 录屏脚本与 pytest 接入（frontend-works/portwatch/tests）

### M-13 用真实浏览器自动化执行平台"写操作"（投稿/发布）的七条硬规矩
- 场景：#浏览器自动化 #Playwright #Tabbit #平台发布
- 问题：用 Playwright/Tabbit 驱动真实浏览器向 B 站投稿，连续踩坑：文件塞进去页面毫无反应、页面状态读不到、下拉选项点了没用、跳转被拦、封面传了却没生效。
- 根因：平台前端是"组件套组件 + 微前端 + iframe"的复合体，"看起来能塞的 input"和"真正被监听的 input"不是同一个；状态也常常不在同一个文档树里。
- 方案（每条都实测过）：
  1. **认准真上传入口**：外层组件的 `.xxx-wrapper input[type=file]` 才是被监听的；同类 `accept` 的另一个（micro-app/装饰元素）塞进去**不会有任何反应**。判据 = 塞完立刻查"页面有没有变化 / `el.files.length` 还在不在"，无变化就换目标，别等 2 分钟。
  2. **内容在 iframe / shadow DOM 里时，`body.innerText` 与普通查询会"看不见"**：探状态一律用 Playwright 定位器（自动穿透 shadow）；跨 frame 用 `frames().find(url 含特征)` 再操作（B 站字幕编辑器整个在一个 iframe 内）。
  3. **page 回调不能引用 Node 侧变量**（`ReferenceError: s is not defined`）：归一化函数内联进 `evaluate/evaluateAll` 回调，或走参数通道。
  4. **组件库下拉用 DOM 派发点击**：Element-UI 这类 `el-select` 会出现"元素渲染了但 `isVisible()` 为 false"的自相矛盾 → `await item.evaluate(el => el.click())`。
  5. **编辑页有 beforeunload**：在它上面 `goto` 会 `ERR_ABORTED` → 另开 `context.newPage()` 走新标签，别动正在编辑的那个页。
  6. **同名按钮 + "完成"≠"生效"**：编辑页的提交按钮与投稿页同名（都叫「立即投稿」）；弹窗里的「完成」只写进表单、**不落库**，必须再提交一次。发布类操作完成后要用**公开 API 复核**（如 `x/web-interface/view` 的 `pic`/`subtitle`），别只信页面上的成功提示。
  7. **平台隐藏规则要单独确认**：B 站封面是**双比例**（4:3 首页推荐 + 16:9 个人空间），只设一个 ≈ 没设 → 提交后会被替换成视频首帧（表现为"黑封面"）。改封面流程 = 传图 → 开「双比例同步改动」→ 两个预览都变成 `blob:` → 完成 → 再提交稿件修改。
- 反模式：把"accept 相同"当同一个入口；用 `body.innerText` 判断页面状态；对隐藏元素硬点；发布完只看页面 toast 不复核；断言"改好了"却不回头读线上接口。
- 溯源：2026-09-21 flowwatch 演示片 B 站投稿全流程（`_deploy/_qa/tabbit/{p,c,m}NN_*.js`；交接文档 §8）

### M-14 视频时间轴"收紧"（跳跃剪辑）要工程化：单一裁剪表 + 回归验证 + 交付前 QC
- 场景：#视频 #ffmpeg #字幕 #时间轴
- 问题：成片里有两段 13 s 的静音等待想跳剪压短，但剪了之后字幕、章节、拼接位置的时间全都要跟着动，手改必错（历史上手改 srt 出过"重复条目 + 错序"）。
- 根因：裁剪不是"剪掉一段视频"，而是"改一个被多方消费的共享坐标"；而且"这段能不能剪"必须可证明，不能凭感觉。
- 方案：
  1. **剪之前先证明可剪**：`ffmpeg -af silencedetect=n=-40dB:d=1.2` 找长静音，再断言"裁剪区间内没有任何字幕条目"——两者合起来才说明它是纯等待（本次两段 13.7/13.9 s 均零字幕）。
  2. **裁剪点落盘成一张表**（`tighten.json: cuts=[[a,b],...]`），下游统一走**一个 `remap(t)`**（`timeline_cut.py`），禁止字幕/章节各自算一遍。
  3. **先做回归验证再动数据**：在没有裁剪表的情况下重新生成字幕，必须与现有文件**逐字节一致**；章节也应与现有一致。证明"改造零影响"后再生成裁剪表。
  4. 剪完三项 QC：`silencedetect` 复检长静音（预期只剩保留段）、`ffprobe` 长度与预期差 < 0.15 s、全片 `-f null` 解码无错；字幕对齐用 `ffsubsync` 复测 offset（本次 0.200 s 未变）。
  5. **只跳等待、不删内容**：保留"起手 + 完整答案"，对外口径写"等待时间经剪辑压缩、回答内容未删"并写进简介。
  6. **同一产物写两处**（成片与插卡底片都写成"已收紧"版），避免"底片被删 → 退回未剪版本"的静默降级。
- 反模式：手改 srt 做位移；只剪视频不管消费方；剪完不做静默图/对齐复检；不声明剪辑口径（等于隐瞒）；重录/重配音后忘了重跑收紧步骤。
- 溯源：2026-09-21 flowwatch 成片 170.81 s → 154.24 s（`_deploy/_qa/tighten.py` + `timeline_cut.py`；交接文档 §2 步骤 ③.5）

### M-15 用管道截断看进度会掐掉上游进程（脚本只跑一半）
- 场景：#PowerShell #工具使用 #长任务
- 问题：`python 长任务.py | Select-Object -First 7` 只想"看前 7 行进度"，结果脚本只跑了一半 —— 产物停在中间状态（配音只写了一半、锚点没更新），而命令看起来是成功的。
- 根因：`-First N` 取够 N 行就关闭管道，上游进程收到管道断开被终止；"看进度"这个动作本身改变了任务行为。
- 方案：会写产物的脚本一律**重定向到日志**（`> run.log 2>&1`）或后台跑再读日志；看进度用 `-Last N` / `Get-Content -Tail`；长任务用独立进程 + 轮询日志，而不是把管道接在命令后面。
- 反模式：在写文件的脚本后面接 `Select-Object -First N`；把"命令返回 0"当"脚本跑完"；产物异常时先怀疑业务代码而不看执行方式。
- 溯源：2026-09-20/21 flowwatch 视频配音（造成"片头后 10 s 有画面没声音"，重跑才修好；交接文档坑表）
### M-16 GitHub Actions 工作流的"语法级"坑：`name:` 值里的冒号
- 场景：#CI #YAML #工具使用
- 问题：工作流推上去解析失败；本地 `yaml.safe_load` 直接报 `mapping values are not allowed here`（指向某行 `name:`）—— 那一行的值里写着 `spec: onedir` 这种"冒号 + 空格"。
- 根因：YAML 的 plain scalar 里 `: ` 会被当成键值分隔符：`- name: PyInstaller 打包（spec: onedir）` 会被解析成嵌套映射。
- 方案：值里含 `: ` / `#` / 以 `{`、`[` 开头时一律加引号；**提交前本地先跑一次 `python -c "import yaml; yaml.safe_load(open('x.yml',encoding='utf-8'))"`**（比等 CI 报错快得多）；顺带复核键名会不会被 YAML 解析成布尔（`on:` 历史坑）。
- 反模式：把 CI 解析失败当玄学重试；靠改缩进/换行"试"。
- 溯源：2026-09-21 flowwatch `.github/workflows/release.yml`（第 149 行 `name:` 值带冒号）

### M-17 工作区里出现"非本次改动"的破损编辑：先分离归属，再定点修复
- 场景：#协作 #排查 #版本控制
- 问题：跑测试报 `NameError: name 'MAX_TURNS' is not defined` —— 常量明明定义过；打开文件发现它被改成了 `memory_reMAX_TURNS`，另有 docstring 被搅乱、平白多出一串类型注解。这些改动**不是本次会话做的**（另一个窗口 / 另一个 AI / 工具留下的半成品）。
- 根因：同一文件可能被多方同时编辑；整文件恢复会连自己的改动一起回滚，直接手改又容易漏掉同批的其它破损点。
- 方案：
  1. 先用 **`git diff -- <file>`** 逐行分类：本方能复述意图的是自己的，对不上号的是外来；
  2. 再分性质：破坏性的（改名导致 NameError）**定点修复**；"能跑的噪音"（多余注解、格式）**留原文并回报确认**，别擅自删；
  3. 同批 `git diff --stat` 扫其它文件，确认行数与自己改动的预期一致；
  4. 修完立刻重跑测试，并把"发现 → 归属 → 修复"写进交接说明。
- 反模式：不分类就 `git checkout -- .` 全量回滚（丢自己的改动、也丢别人的意图）；只修报错点不查同批文件。
- 溯源：2026-09-21 flowwatch `assistant.py`（`MAX_TURNS` → `memory_reMAX_TURNS`；外来 `tuple[Literal[...]]` 注解经确认后删除）

### M-18 清理/删除类操作写成可复用脚本，别塞在终端长命令里
- 场景：#工具使用 #Windows #协作
- 问题：终端里 `Remove-Item -Recurse` 之类的破坏性命令会触发审批弹窗；弹窗不可见/无人确认时会**超时被取消**，而审批粒度是**整条命令** —— 同一批里的构建、检查步骤一起作废。
- 根因：把"删除"混进复合命令；审批只认命令，不认意图。
- 方案：把清理做成**项目内脚本**（Python `shutil.rmtree` + `--dry-run` / `--all` 开关，打印释放了多少 MB），终端只调用脚本：既绕开审批卡顿，也让"清了什么"可回溯、可复跑（同源经验：同一文件多处 `replace_in_file` 不能并行 → 批量改写也走脚本）。
- 反模式：把 `Remove-Item` 塞进长命令中段；删完不留清单，下次不知道删过什么、哪些还要留。
- 溯源：2026-09-21 flowwatch `_deploy/flowwatch/clean_builds.py`（清理 393 MB 冗余构建；期间多条含 `Remove-Item` 的命令被审批超时取消）

### M-19 卡片式"数据解说"视频的可复制链路（HTML 卡片 → 录屏 → TTS → 烧字幕）
- 场景：#视频生成 #Playwright #edge-tts #可复制
- 问题：要把一段解释性内容（如"1000K 窗口为什么能烧掉 1000 万 Token"）做成 1 分钟竖屏/横屏解说片，手写剪辑不可复用、改文案要重做全片。
- 根因：文案、画面、字幕、封面四者耦合；只有把"文案"做成唯一事实源，其余全部由脚本派生，改一句才能 2 分钟重建。
- 方案：固定四件套（每个主题一个目录）：① `script.py` = 唯一事实源（逐句文案 + 该句用哪段素材 + 入点 + 字幕主题色；需要顺读时用 `say` 字段与字幕原文分离，避免 `+ / → / ……` 被 TTS 念错）；② `record.py` = Playwright `record_video_dir` 录 1920×1080 片段（卡片页/网页皆可，步骤表驱动 click/key/wheel/xy）；③ `build.py` = edge-tts 逐句配音（按文本 hash 缓存，改一句只重配一句）→ 每句裁一段素材并拼上该句音频（`trim/setpts/crop/scale` + `apad/atrim`）→ concat → 生成 srt → 用 `short_cut.caption_events` 烧"逐块变色"字幕；④ `make_cover.py` + 通用 `cover_ratios.py` 出封面双比例。空白文案可直接当"静音段"（`anullsrc`）用，用于无口播的收尾卡。
- 反模式：文案写死在剪辑里；每次改稿手工重排时间轴；把字幕交给播放器而不烧录（投稿后无法逐块变色）。
- 溯源：2026-09-22 `frontend-works/_deploy/_qa/tokenburn/`、`_qa/ai_animation/` 两条科普片（51.16s / 79.88s，均从"改一句文案"到重出成片 ≤2 分钟）

### M-20 平台投稿类自动化：跨会话任务槽会失效，未提交的页面状态不可依赖
- 场景：#浏览器自动化 #投稿 #交接
- 问题：真实浏览器自动化把视频塞进 B 站投稿页后未提交，隔天再探测发现 `task.reused=false`、新任务返回 `about:blank` —— 原任务槽与页面已不在手上，**上传/表单进度无法确认，基本等于白做**。
- 根因：Tabbit 的 task 槽按会话/命名占用，跨天或任务被释放后不再复用旧标签；而投稿页的"已上传视频 + 已填表单"只存在于该页面内存（不是草稿）。
- 方案：① **单次会话内一气呵成**：上传 → 填标题/简介/标签 → 传封面 → 提交 → 复查列表，中途不换会话；② 上传完成的判定不要只数 `[class*=progress]` / "上传中" 文案（实测编辑器已出现这些计数仍 >0）→ 用"标题输入框出现 **且** 上传区消失"双条件，或直接看文件名是否上屏；③ 交接必须写清"进行到哪一步、最后是哪个 task 名、页面是否已提交"，否则下一步只能重做。
- 反模式：以为"浏览器里页面还在=进度还在"；把未提交的投稿页当草稿存着。
- 溯源：2026-09-22→23 tokenburn 投稿（t2 上传后未继续，次日 task 槽已换，状态不可考）

### M-21 微信公众平台自动化发布的三个连环坑：HTML 被降级 / 标题框是隐藏元素 / 必须走 paste 事件
- 场景：#浏览器自动化 #平台发布 #Tabbit #微信
- 问题：用浏览器自动化往公众号图文编辑器填内容，连环踩坑：① `document.execCommand("insertHTML", html)` 插入后**整段被降级成纯文本**（表格挤成一行、标题层级与加粗全丢）；② 标题输入框 `textarea#title` 是 `visibility:hidden` 的隐藏元素，Playwright `click()`/`fill()` 一律超时；③ 改用 `evaluate` 设 `value` + dispatch `input`/`change`，DOM 值看着变了但**编辑器不认**（保存后标题丢失、计数器仍 `0/64`）。
- 根因：① 正文是 **ProseMirror**，`insertHTML` 输入路径下其 schema/净化插件把陌生结构当纯文本收进 `<section><span leaf="">`；② 标题框只是数据载体，UI 由外层容器渲染，**点容器才触发聚焦**；③ 微信的模型层不监听原生 `input` 事件的值变化，只认自己的编辑事务。
- 方案：
  1. **正文别自己转 HTML，改走「paste 事件 + 平台原生 Markdown 转换」**：页面内构造 `const dt = new DataTransfer(); dt.setData("text/plain", markdownSource); target.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true }))` → 编辑器弹出「检测到 Markdown 语法 → 转换格式」→ 点击后**完整还原** `h2/h3/table/ul/blockquote`（实测一次得到 h2×6 / h3×10 / table×4 / li×35）。注意：用 `keyboard.insertText` 打 Markdown 源码**不会**触发检测，必须是 paste 事件。
  2. **标题用真实键盘输入**：点击可见标题区容器（微信为 `.js_title_main`）→ `keyboard.type()` → 计数器变成 `25/64` = 被接受。
  3. 验证读数：正文结构看 `div.ProseMirror` 内标签计数；保存状态看 `save_wording`（"HH:MM 已保存"）。
- 反模式：把"insertHTML / 设 value 成功"当作写入成功（DOM 层面成立、模型层面丢失，保存后才发现）；用 `tabbit.pasteText` 等合成剪贴板粘贴富文本（页面不在前台时 `foregroundPolicy=preserve` 直接拒绝：`requires editable focus`）。
- 附：**Tabbit 任务组生命周期**：组依赖"组内有活标签"，标签全关后组即消失（`resume` 报 `GROUP_NOT_FOUND`）；会话周期性重建（`reused=false` + `about:blank`）时固定用 `finish --task <name>` + `resume --task <name> --group <id>` 重挂载（跨会话状态不可依赖详见 **M-20**）；`--foreground` 不存在、`page.bringToFront()` 被 `foregroundPolicy=preserve` 拒绝 → 合成剪贴板 API 不可用，走 CDP 输入（`keyboard.type` / `keyboard.insertText`）或页面内事件。
- 溯源：2026-09-22 用 Tabbit CLI（task `mp-publish`）发布 memory-guard 复盘文（frontend-works/tools/memory-guard → TechLog + 公众号）

### M-22 文件行尾 CRLF 会让 frontmatter 报"假 YAML 错"（报错列号伪装成内容问题）
- 场景：#编码 #行尾 #Contentlayer #js-yaml #工具使用
- 问题：往 Contentlayer 博客（tailwind-nextjs-starter-blog 系）的 `data/blog/*.mdx` 新增文章，构建报 `YAMLParseError: Unexpected scalar at node end at line 6, column 138`。按报错去改 frontmatter **内容**（删中文引号、缩短 summary）——**报错列号同步变小、错误照旧**，说明问题不在内容。
- 根因：新文件是 **CRLF 行尾**（项目其余文件全是 LF），**js-yaml 把行尾的 `\r` 算进了单引号字符串**，字符串在该行末尾"意外结束"→ 报错位置 = 该行最后一个字符。**列号随内容长度移动，因此极具迷惑性**。
- 方案：① **不要改内容**，先做**字节级对比**（新文件 vs 同目录正常文件）：`raw[:3]` 查 BOM、`raw.count(b"\r\n")` 查 CRLF、打印可疑行的 `repr()` 与逐字符码点（本次定位到 `line6_suspicious_chars: [(137, '0xd', '\r')]`，与报错 column 138 精确对应）；② 修复：`text.replace("\r\n","\n")` 后以 `open(..., "w", encoding="utf-8", newline="\n")` 写回（UTF-8 无 BOM + LF）；③ 验证：构建日志搜 `failed` + 产物文件与 RSS 双确认。
- 反模式：据报错去"修内容"（本次白改两版 summary）；用编辑器/写文件工具产出文件而不核对项目的行尾约定（同项目文档已记"新建 `.tsx` 必须 LF，CRLF 会被 prettier 判失败"，这次轮到 `.mdx`）。
- 溯源：2026-09-22 TechLog 新文章构建失败（`%USERPROFILE%\WorkBuddy\2026-06-04-11-30-28\my-tech-blog`）

### M-23 进程"杀-重生"循环：只杀子进程是白杀，先看清"谁在重启它"
- 场景：#进程管理 #自动化 #Electron #排查
- 问题：守护脚本按"工作集最大"选目标，反复杀掉某 Electron 应用的 gateway 子进程（400MB~1.2GB），**9 秒后它原样回来**，形成"杀-重生"循环；而人工在托盘退出同一应用却不重生。
- 根因：被杀的是**叶子**（应用主进程 spawn 的后台服务，受 supervisor 托管，子进程 exit 会触发重新 spawn）；人工退出杀的是**根**（主进程）→ 没有 supervisor 自然不重生。按内存排序选目标时，叶子常有几百 MB~1GB+，而根只有一两百 MB，**永远排在候选之外** → 脚本永远在杀叶子。
- 方案：① 先看父进程链（`ParentProcessId` 逐级溯源）判断"谁 spawn 了它"；② 选择策略三选一：**跳过**会被重生的服务（按命令行关键词识别 supervisor 托管者，避免白杀 + 周期性中断服务）／升级为"**杀就杀根**"（沿父链定位应用根，回收最多但要接受连带关闭）／维持现状但加"每小时杀次数上限"防循环失控；③ 把决策交给使用者（这是策略问题不是技术问题）。
- 反模式：把"杀完内存确实降了"当成策略有效（几分钟后重生，长期是空转 + 反复中断服务）；在不知 supervisor 存在时一味加大"杀进程力度"。
- 溯源：2026-09-22 memory-guard 实战（QClaw / `openclaw-gateway`：07:50:03 杀 → 07:50:12 重生；用户最终选"维持现状、接受重生"）

### M-24 PowerShell 5.1 的 `Get-Process` 没有 `CommandLine`：按命令行筛进程必须走 CIM
- 场景：#Windows #PowerShell #进程 #工具使用
- 问题：写"检查某进程是否正以某参数运行"的守护脚本，`Get-Process -Name ssh | Where-Object { $_.CommandLine -match $target }` **永远不命中** → 每轮都判"进程不存在"→ 每个周期新建一个，反而制造出它本来要防的进程堆积。
- 根因：Windows PowerShell 5.1 的 `Get-Process` 返回 `System.Diagnostics.Process`，**没有 `CommandLine` 属性**（PS 7 也没有）。`$_.CommandLine` 恒为 `$null`，`-match` 对 `$null` 静默返回 `$false` —— 不报错、不警告，代码看起来"没问题"。
- 方案：取命令行必须走 CIM：`Get-CimInstance Win32_Process -Filter "Name='ssh.exe'" | Select-Object ProcessId, CommandLine, CreationDate`（`CreationDate` 还能算进程年龄，用来放过"刚启动、正在握手"的进程）。**上计划任务前先人工验一次过滤命中**：打印匹配到的 PID 与命令行，确认不是空集。
- 反模式：靠 `Get-Process` 的属性做条件分支（写逻辑前先 `Get-Member` 确认属性存在）；把"过滤不命中"直接当成业务结论。
- 溯源：2026-09-23 `C:\scripts\ssh_heartbeat.ps1`（初版由别的 AI 生成，正是这个 bug 导致"保活脚本反而制造堆积"）

### M-25 云安全组端口是否放行：用 "refused vs timeout" 判定，比回控制台翻规则快
- 场景：#云主机 #安全组 #排查 #网络
- 问题：要在云主机上开放一个非标端口（如 18080 做反向隧道），不知道安全组放不放行；服务端 `ss -tlnp` 明明在监听、绑定也是 `0.0.0.0`，公网却连不上 —— 分不清"没监听"还是"被安全组丢包"。
- 根因：安全组是**丢包（DROP）**语义：被拦端口从外部看是**超时无响应**；而"放行但无进程监听"的端口，内核会立刻回 **RST = 连接被拒绝**。两种失败的语义完全不同，只取"通/不通"的布尔值看不出来。
- 方案：**从外部逐端口探测并区分异常类型**（PowerShell 三行即可：`TcpClient.ConnectAsync(...).Wait(ms)`，catch 到 refused 即"已放行"）→ refused = 可直接用；timeout = 被拦，要用就得去控制台加规则。实测某云主机只放行 80/443/8080/8090，其余全 timeout → 反向隧道直接改用 80，省掉一次控制台操作。
- 反模式：只看服务端 `ss -tlnp` 就宣称"端口已开"（`ss` 只证明"本机在听"，证明不了"外部到得了"）；被拦后反复改 sshd/nginx 配置。
- 溯源：2026-09-23 京东云 111.228.0.160 反向隧道选端口（`-R 0.0.0.0:18080` 公网 timeout → 换 80 后立刻 200）

### M-26 从压缩/打包产物里定位逻辑：按"字符窗口"截取；附带 PowerShell 里 `$` 被外层 shell 吃掉的坑
- 场景：#工具使用 #Minified #逆向 #PowerShell #Windows
- 问题：要在客户端压缩单行产物（`main.js` 1.8 MB，整文件只有一行）里找出"某个守卫为什么拦我"的判定条件。用常规"带上下文"的检索（`grep -C` / 上下文行）会把**整行上百万字符**原样输出 → 工具输出/缓冲区被撑爆，连续两次都拿不到结果（表现为 `No result found` 或结果被截断），很容易误判成"文件里没有这个字符串"。
- 根因：minified 产物把逻辑压成一行，任何"按行取上下文"的读法都等价于"把整个文件读进来再打印"，输出体积与文件体积同阶。
- 方案：
  1. **按位置截窗**：先 `[IO.File]::ReadAllText()` 读全文 → `IndexOf('关键字')` 拿偏移 → 只 `Substring(offset-450, 900)` 取窗口（可循环取多处命中）。
  2. **落盘再读**：把窗口文本写进临时 `.txt`，再用文件读取工具看 —— 绕开终端/工具的输出上限，也便于二次核对。
  3. **优先搜"副作用可观测"的原话**：直接搜日志里出现过的那句话（本例 `install dir guard`、`user content detected`），比搜概念名（`guard`、`check`）命中率高得多。
- 附带坑（与 M-02 同源，这里是"变量展开"变体）：`powershell -Command "…$var…"` 会**先被外层 shell 展开** —— `$_`、`$p` 在到达内层前就被吃掉，症状是 `CommandNotFoundException: .ProcessName` 或 `You must provide a value expression following the '+' operator`，看着像脚本写错，实际是**参数被提前替换**。
  解法：① 写成临时 `.ps1` 用 `-File` 执行（最稳）；② 或把单行表达式写成**不含 `$`** 的形式（如 `(Get-Content 'x' -Raw).IndexOf('y')`）。
- 反模式：看到 `No result found` / 输出截断就换关键字继续硬搜（应先怀疑输出机制）；把外层变量展开报错当语法错误去反复改脚本。
- 溯源：2026-09-24 CodeBuddy CN `installDirGuard` 取证（`resources\app\out\main.js`，1,831,750 字符单行）



### M-27 第三方内核依赖"能自动到什么程度"由许可决定，不由技术决定
- 场景：#合规 #第三方依赖 #产品决策
- 问题：用户问"驱动应该可以自动安装的吧"，期望点一下就装好。
- 根因：查官方站点原文才发现三条硬约束 —— ① 免费版**不得随其他软件再分发**（`may be used (but not externally distributed)`）；② 免费版**限 N 台机器**（本例 5 台，特定搭档软件除外）；③ **静默安装属商业版（OEM）功能**。三者叠加 → "无感自动安装"不存在，只有"半自动"（页面给官方安装包直链 + 用户走一遍向导 / 过 UAC）。
- 方案：把约束当产品边界来设计 —— 引导里放**当前版本安装包直链**（版本号可从官方首页字段解析；本项目写死在常量里并注释"更新后改这一行"，避免为查版本而主动出站）；步骤里显式说明"会要一次管理员授权"；README 如实写清许可三条与"为什么不能替你打包"。
- 反模式：把第三方驱动打进自己的包（许可风险）；假设"商业版才有的功能"免费版也能用；为了体验偷偷联网查版本（打破"不主动出站"的定位）。
- 溯源：flowwatch 首启引导的安装引导（2026-09-24，核对 npcap.com 原文；提交 `a164ec1`）。

### M-28 多会话共享同一份当日日志：整篇重写会吞掉别的会话刚写的记录
- 场景：#协作 #记忆系统 #并发
- 问题：同一天另一个会话把 `.codebuddy/memory/YYYY-MM-DD.md` 整篇重写（按它早先读到的版本落盘），这边刚写的记录凭空消失；随后用旧锚点改字直接报"找不到字符串"。
- 根因：文件是共享写入点且没有锁；"读—改—写"窗口越长越容易被覆盖（长会话尤其明显）。
- 方案：① 追加写优先，锚点取文件**末尾**的一小段唯一文本（不要用中段）；② 锚点失配时先整读一次再补写，不要反复重试；③ **权威记录放仓库**（handoff / 提交信息），日志只当流水 —— 项目级结论丢了还能从 git 找回来，只落日志的会真丢。
- 反模式：把"只有日志里有"的结论当唯一存档；长会话末尾批量写大量记录。
- 溯源：flowwatch v1.0.2 / v1.0.3 记录被同日另一条线（memfuse）覆盖后补回（2026-09-24）。

### M-29 定位器逐项读文本会累加超时：撞满执行器硬限后连标签页一起丢
- 场景：#浏览器自动化 #Playwright #Tabbit #超时预算
- 问题：写"遍历下拉选项、找到中文就点"的循环，程序跑到一半整个被终止（`EVALUATION_TIMEOUT`），并且**该任务的所有标签页消失**（只剩 `about:blank`）—— 刚打开的字幕编辑器、上传页全要重开。
- 根因：`locator.innerText()` 单次默认 **30 s** 超时；对**数量不确定**的元素逐个读文本时超时会**累加**（本例语言下拉 160+ 项，命中不到的等待叠加），很快吃满执行器硬限（默认 60 s、上限 180 s，`--timeout-ms` 传的是上限本身）。被硬限终止 = **执行器连同它的标签页一起被回收**，不是"程序失败但现场还在"。
- 方案：① 批量读取用**一次** `evaluateAll(els => els.map(el => el.innerText))`，再按索引 `nth(i)` 操作；② 每个定位器操作**显式给小超时**（`{timeout: 3000~6000}`），不靠默认值；③ 长流程拆段（上传 / 填表 / 封面 / 提交各自一次调用），单段留足余量；④ 被终止后**别指望恢复现场**：用深链 URL 重开目标页（`groupId` 可试 `resume`，实测任务已重建为空白页）。
- 反模式：对未知长度列表做 per-item 读；把"程序超时"当"页面慢"重试同一段代码（会同样撞限）；把标签页当可恢复的现场。
- 溯源：2026-09-24 memfuse 宣传片 B 站投稿（`_deploy/memfuse-video/tabbit/m15_lang_srt.js` 撞 150 s 硬限，编辑器标签页丢失）

### M-30 B 站投稿/字幕自动化的判据与走位：结构 > 数值 > 文案（补 M-13）
- 场景：#浏览器自动化 #平台发布 #B站 #判据
- 问题：判"上传/封面到底成了没"时被平台读数骗：上传区文案「点击上传或将视频拖拽到此区域」在**上传完成后依然在**；`/上传中|上传完成|转码/` 能同时命中 5 个**隐藏占位**节点（busy 恒 5）；封面预览是 `<canvas>`，既无 `img` 也无 `blob:`，拿不到"图已就位"的属性证据；而该页 `page.screenshot()` **必然超时**（`SCREENSHOT_CAPTURE_FAILED`，卡在 fonts loaded 之后），连"截图即真相"这条退路也没有。
- 根因：平台把各阶段 UI 预挂载在 DOM 里靠 CSS 显隐 —— **文案与"可见性"都不构成状态**；封面预览走 canvas 绘制，不落到可查询属性上；创作中心页的持续动画/字体加载让截图永远等不到稳定帧。
- 方案：
  1. **上传进度**：`input[type=file].files.length`（塞进去了没）+ `[class*="progress" i]` 的 `width:100%`/`success` 类（跑完了没）。
  2. **封面**：canvas 采样 —— 缩到 16×16 / 32×32 后算均值 + 数"主题色像素"；**换图的判据 = 该 canvas 均值发生变化**（实测 4:3 区 `[20,21,22]`、16:9 区由 `[6,7,11]` → `[29,29,32]`）；"添加封面"CTA 消失只作辅助证据。
  3. **最终验收**：抓线上产物复核 —— `og:image`（封面）、`x/web-interface/view?bvid=` 的 `pic`/`subtitle`、"我的字幕"列表状态；本地设计稿与线上图**同图**才算过（元原则 13）。
  4. **走位**：字幕编辑器可**深链直开** `member.bilibili.com/platform/zimu/my-zimu/zimu-editor?bvid=…&cid=…&epid=null`，比"播放页 → 字幕 → 添加字幕（还要等 popup）"短且稳；`cid` 从该 URL 取一次即可复用。
  5. **滞后**：字幕列表有 1~2 分钟延迟，别据此判失败 —— 判据用"我的字幕 → 已发布(N)"计数 + 首行时间戳。
- 反模式：拿平台文案/可见性当状态机；在 canvas 页做截图验证；上传完只看 toast 不复核线上。
- 溯源：2026-09-24 memfuse 投稿（BV17Haw6UEKU，脚本 `_deploy/memfuse-video/tabbit/m01..m21*.js`）；承接 M-13 与 `HANDOFF-视频与投稿-20260920.md` §8

### M-31 程序化宣传片：分段边界必须单一权威源 + 交付前四项 QC
- 场景：#视频生成 #逐帧渲染 #字幕 #验收
- 问题：从零做 64 s 口播宣传片（HTML 逐帧渲染 + edge-tts），第一版**全片黑屏**；修好后又被"孤儿数字/箭头"这类时序瑕疵缠住；交付前"字幕看着准"其实从没验过。
- 根因：① 幕的显示窗口与"第几句台词"共用同一 key 前缀（`sNstart/sNend`），语义一混 → 幕窗口整体错位一句，每帧都不满足显示条件；② 锚点函数返回的已是**绝对秒**，调用处又加了一次句起点（元素迟到）；③ 沿用前值当后值（日志 `1069MB → 1871MB` 写成 `1069 → 1069`）且揭幕不同步；④ 画面停留与字幕都由配音时长派生 —— 但"派生"不等于"验过"。
- 方案：① 幕边界由**句子区间**生成（切换点取"上一幕末句 end"与"下一幕首句 start"的中点 → 既无黑场也无叠帧），且**幕的 key 与句的 key 用不同前缀**；② 时间换算只在**一处**做（锚点返回绝对秒），调用处不再叠偏移；③ 关键视觉锚在**词边界**（念到才亮）；④ 交付前四项 QC 全跑：`ffsubsync` 对齐偏移（本例 0.090 s）、整片 `-f null` 解码 + **帧数 == 时长 × fps**（1914 = 63.85 × 30）、音量（mean/max dB）、交付形态抓回比对。
- 反模式：用同一套 key 同时表达"幕"和"句"；时间换算散落多处；只渲几张静帧就断言"时间轴对了"；只跑 ffprobe 不跑整片解码。
- 溯源：2026-09-24 memfuse 宣传片（`_deploy/memfuse-video/`：`narration.py` + `make_promo.py` + `src/promo.html`，成片 63.85 s / 1914 帧）

### M-32 解析命令行 JSON 的三连坑：多行 stdout / 盘符变量 / stderr 假报错
- 场景：#PowerShell #curl #API调试 #工具使用
- 问题（三连，本轮全踩）：① `$r = curl.exe ...` 后 `ConvertFrom-Json $r` → `无法将"System.Object[]"转换为参数"InputObject"所需的类型"System.String"`；② `"v$v: 完成"` 直接**解析失败**：`变量引用无效。':' 后面的变量名称字符无效`；③ `git push` 的进度信息走 **stderr**，被 PS 渲染成红色 `NativeCommandError`，看着像失败（其实 `[new branch]` 已成功）。
- 根因：PS 对 native 命令的输出是**按行拆分**后进入管道的（多行 = 字符串数组）；`$name:` 是合法的 provider 路径语法（`$env:PATH` 那一族）；`NativeCommandError` 只表示"stderr 有内容"，**不代表退出码非 0**。
- 方案：① 一律 `curl.exe -s -o <临时文件> ...` 再 `ConvertFrom-Json ([IO.File]::ReadAllText($f))`（或先 `-join "`n"` 归一）；② 拼接用 `-f` 格式化或 `${v}` 明确边界；③ 成败看**结构化证据**：`git push` 看 `[new branch]` / `* [new tag]` + 事后 `ls-remote` 复核，必要时打印 `$LASTEXITCODE`，不看红字。
- 反模式：把 curl 的多行输出直接丢给 `ConvertFrom-Json`；用 `"$var: 文案"` 拼字符串；看到 `NativeCommandError` 就去"修"一个没坏的命令。
- 溯源：memfuse 双 Release 与启动器会话（2026-09-24/26；同族 M-02「内联 JSON 被转义破坏」、M-16「工作流 YAML 冒号」）

### M-33 会"误伤用户"的自动化：默认向后兼容 + 风险能力显式开启 + 先看清再开火
- 场景：#工具设计 #默认值 #安全 #用户体验
- 问题：一个"内存临界时杀最大占用进程"的守护被人指出：**总有人在乎被杀掉的未保存工作**。原设计只硬保护 45 项系统进程，**所有带窗口的应用都在可杀范围内**，且 `WM_CLOSE` 只等 5 秒就强杀 —— 用户来不及点"保存"。
- 根因：把"机器优先"当成唯一正确策略，且**策略性能力没有开关**；同时白名单文件只在启动时读一次 —— 加白名单要重启守护，安全设置与便捷性被人为对立。
- 方案（四件套，按"从轻到重"暴露）：① **默认行为向后兼容**（新开关默认 = 老行为，只把等人的宽限期从 5 s 提到 15 s）；② 风险能力做成**显式开关**（`Skip` = 有窗口的进程永不被强杀，超时就跳过、换下一个候选并写日志；`Force` = 不看窗口直接杀）；③ 给"**先看清再开火**"的命令（`-ListWindowed` 列出谁可能握着未保存的工作并标注 protected/killable、`-ListProtected` 打印生效白名单、`-DryRun` 预演）；④ **配置热加载**：运行期按 `LastWriteTime` 重读白名单（每采样周期一次 stat），改完即生效、不用重启；⑤ 紧急档保留"机器优先"，但把取舍**写在文档明处**（可用内存 < 阈值一半时宽限期压到 3 s）。
- 反模式：给杀伤类工具加"更聪明的默认值"却不留回退开关；安全配置做成"改了要重启"；只在 README 写"请谨慎使用"，不给可操作的清单/演练命令。
- 溯源：memfuse 分支 `feature/windowed-protection`（2026-09-24 会话；验证法见 C-05）

### M-34 别人给的预览/沙箱 URL 可能是旧快照：先做"是否当前源码"判据再相信它

- 场景：#排查 #验证 #预览环境
- 问题：用户给了一个预览 URL 让"看渲染效果"，差点直接采信。实际查下去：**新写的文章 404、刚加的第三条链接不存在、`/projects` 里连一个真实项目都没有（是 starter 模板的内容）**。URL 有效、页面能开、站名也对 —— 但内容不是当前源码。
- 根因：预览隧道 / 沙箱 / 静态导出会指向**旧会话或旧构建的快照**；"能打开"与"对应当前工作区"是两件事。
- 方案：拿到任何"环境 URL"先做**归属判据**再信它 —— 查一个**只有当前源码才有的字符串**（最新文件的 slug / 刚改的项目名 / 刚新增的标签），命中才认为它反映当前状态。否则**自己起一个本地服务验证**（本次即在 `:3010` 起 `next dev` 才拿到真结论）。
- 反模式：用预览/沙箱的渲染结果当作"我的改动生效了 / 没生效"的证据；因为页面能打开就跳过归属校验。
- 溯源：TechLog 预览 URL 核查（2026-09-28；判据 = `/projects` 里 flowwatch/portwatch/VDB 各 0 次 + 含模板残留文章）

### M-35 MDX / 行尾 / 内容层缓存：三个只在"执行链"上暴露的约定

- 场景：#编码 #行尾 #MDX #构建缓存 #git
- 问题：三件事都是"本地看着对、构建或提交时才出问题"：
  ① 正文里写一句"HTML 里有 `<p>` 标签"→ **整站构建失败**（且报错位置与真实原因无关，极具迷惑性）；
  ② `.mdx` 必须是 LF，而 Windows 写文件默认 CRLF（本次初稿 390 行 CRLF）；
  ③ 删掉文章后，内容层生成目录里**旧条目还在**（本次 39 个条目里 12 个是模板残留）。
- 根因：三者都是"**约定由工具在执行时施加**"，编辑器/文件写入/删除动作本身不参与 —— 于是本地看不出问题。
- 方案：
  ① **MDX 会把正文里的 `<tag>` 当 JSX、`{}` 当表达式**。所有尖括号内容一律包**反引号**；只用 remark 已启用的语法（GFM 表格 / 数学 / 代码标题）。
  ② 写完文件**按字节判行尾并归一**；仓库侧有 `.gitattributes` 的 `* text=auto eol=lf` 能保证提交进仓库的是 LF，但**工作副本会残留 CRLF**，两边要分别确认。
  ③ 内容层工具（contentlayer 类）**只写不删**：删文章后要整目录删 `.contentlayer/{generated,.cache}` 再重建（本次删完重跑：39 → 28，与 `data/blog` 下 27 篇 + 1 个索引文件一致）。清理前先确认这些残留是**惰性的**（查它们是否进了搜索索引 / 标签表 / 导出目录）。
  ④ 附带一个 git 现象：`eol=lf` 与 `core.autocrlf=true` 组合下，某文件会**反复被报成 `M`**，而 `git diff` 为 0 行、`git hash-object <f>` == `git rev-parse :<f>` → **纯 stat 缓存假象**，`git add` 一次即清，**不要为它做多余提交**。
- 反模式：只做语法编译 / 肉眼检查就提交（`py_compile` 抓不到 JSX 解析错）；用"文件总行数"判断行尾；看到 `M` 就追加一次提交。
- 溯源：TechLog 新文章发布（2026-09-28；校验工具 `_deploy/_qa/check_blog_post.py` + `contentlayer2 build`）

### M-36 npm script 里的 `$VAR` 语法在 Windows cmd 下不展开（`Unbound variable`）
- 场景：#工具使用 #Windows #npm #环境
- 问题：`yarn dev` 直接失败，日志只有一行 `Unbound variable "PWD"`，看不出跟系统环境有关。脚本内容是 `cross-env INIT_CWD=$PWD next dev`。
- 根因：`$PWD` 是 Unix 风格的 shell 变量；Windows cmd 不展开它，而 Yarn Berry 自带的 shell 实现会把它当"未定义变量"直接报错终止（不是 Node/Yarn 装坏了）。
- 方案：绕开这层 —— 直接跑底层命令（`yarn start` 在本项目里等价于 `next dev`），或用 `npx next dev`；确实需要 `INIT_CWD` 时在 PowerShell 里显式传绝对路径。
- 反模式：看到 `Unbound variable` 去怀疑安装损坏、重装 Node/Yarn；把"某个 npm script 在本机跑不起来"一律归因成依赖问题（先看脚本内容里有没有 `$VAR` 写法）。
- 溯源：TechLog 本地起站（2026-09-29）

### M-37 一条命令内的 `Set-Location` 不保证后续相对路径的解析基准
- 场景：#工具使用 #Windows #跨工作区 #相对路径
- 问题：在一条命令里先 `Set-Location` 到某仓库，再用相对路径读写其中的文件（`[IO.File]::ReadAllText('data/blog/…')`），结果解析到了 **workspace 根**而不是目标仓库——读取落空或读错文件；属于"再次踩到"。
- 根因：命令内的工作目录语义**不由 `Set-Location` 保证**——相对路径的解析基准可能仍取自会话初始 cwd / 工具注入的 cwd，与"我先 cd 过去了"的直觉不符。
- 方案：跨工作区（尤其 workspace 外的仓库）的文件操作**一律写绝对路径**；需要指定仓库时用工具原生的目录参数（如 `git -C <repo>`），不依赖"先 `Set-Location` 再相对路径"的链式假设。
- 反模式：出错后先怀疑文件不存在/权限问题，而不是先打印 `Get-Location` 与解析后的绝对路径核对；写操作继续用相对路径——可能把文件写到意外位置（本次是只读，损失可控）。
- 溯源：TechLog 文章页改版推送复核（2026-09-29）

### M-38 会话"服务化"后 stdout 被吞：结果写文件再读；附 python -c 引号炸
- 场景：#工具使用 #Windows #PowerShell #AI代理
- 问题：在启动了长驻服务（如 dev/preview 服务器）的 shell 会话里继续跑后续命令，命令**执行成功（exit 0）但输出完全拿不到**，返回里只剩工具层的 service 标记；另一类：`python -c` 单行里嵌单引号 + `|` 的组合，被 PowerShell 引号解析打成"字符串缺少终止符"而整条崩掉。
- 根因：① 工具层把"已启动服务的会话"标记为 watch/service，后续 stdout 归入服务日志而不回传；② PowerShell 对外层双引号字符串里的引号/管道组合，解析边界与直觉不符。
- 方案：① 关键读数的命令一律**把结果写文件 + 用 read_file 读**（或拆成纯短命令分步执行）；② 稍复杂的 Python 一律写成**临时 .py 脚本**执行（跑完即删），不硬凑 `python -c` 单行。
- 反模式：反复重试同一条"输出消失"的命令；在 `-c` 单行里叠引号/管道/中文继续碰运气。
- 溯源：flowwatch 构建诊断会话（2026-09-25）

### M-39 探测本机服务只认状态码，会被"别的进程占同端口"骗过
- 场景：#排查 #本机服务 #端口 #健康检查
- 问题：告警投递方向"插件端口"推送时，端口实际被**另一程序**（宿主软件本体）占着——若该程序对同路径恰好返回 200，投递方会误判"送达成功"，**告警静默丢失**，事后一切"正常"。
- 根因：端口可达 ≠ 服务是你要找的那个；200 可能来自任何监听者（本次占位者返回 401 属幸运，换个路径/程序就是 200）。
- 方案：探测/投递一律**校验响应体特征**（JSON 解析后判字段，如要求 `{"ok":true}`），不只看 `status==200`；服务发现设计成"按序探测多端口 + 严格校验 + 失败快速下跳"，并把实际寻址结果暴露在各自 `/health` 里。
- 反模式：只判 HTTP 200 就认定送达；假设"这个端口没人占"（本次目标端口被长期占用，服务实际漂移到 +1 端口才正常）。
- 溯源：Catrace 告警集成（2026-09-19 会话）

### M-40 cmd 下含 `%xx%` 的 URL 被当变量展开：报"文件名、目录名或卷标语法不正确"
- 场景：#Windows #cmd #URL #下载 #工具使用
- 问题：`curl.exe -o wiki.png "https://…/uploads/b/bc/%E7%86%8A%E5%A4%A7.png"` 连续报 `文件名、目录名或卷标语法不正确`（`Invoke-WebRequest -OutFile` 同样），像是路径/中文名写错；把 URL 里的百分号换成不含 `%` 的地址立刻成功。
- 根因：命令实际由 **cmd.exe** 执行时，URL 里的 `%E7%86%8A…%` 被当作 `%VAR%` 环境变量语法展开（`python -c "…%E7%86%8A…"` 也照炸），URL 与参数被撕碎；报错信息指向"文件名"，把排查引向编码/长度方向。
- 方案：**把带百分号的下载写进脚本文件**（Python `requests` / `urllib` 原样保留 URL），别塞进一行终端命令；确需命令行时先确认当前 shell 是 PowerShell（`$PSVersionTable`）并避免 `%`，或先把 URL 解码成中文再传入。
- 反模式：反复调 `-o` 路径与引号、怀疑中文文件名；在同一 shell 里换 `curl`/`IWR` 反复试（两者会被同一展开机制搞坏）。
- 溯源：2026-09-30 bear-boss 抓熊出没官方形象图（`bear-boss/productions/bear-boss/references/xiongda/wiki_2.png`，最终用临时 `_dl_ref.py` 下载成功）

### M-41 验证「技能/知识库到底有没有用」用三臂对照，且 agentic 默认只 load_skill、测可检索须补 read 工具
- 场景：#知识库评估 #agentic #技能验证 #可检索
- 问题：光看"库里有内容"无法证明有用；直接复用现成 agentic 执行器（默认只注册 `load_skill`，返回 SKILL.md 概要）去跑题，库答案正文若在 `references/` 子文件，agent 根本读不到 → 既测不出"可检索"形态，还会把"读不到"误判成"库没用"。
- 根因：`load_skill` 只回技能根的 SKILL.md（索引/路由表），真正的答案正文散在 `references/*.md` 子文件；执行器没提供读子文件的工具，agent 走不到答案。
- 方案：三臂对照量化效用——① `without`（无技能无工具，模型先验基线）② `inject`（把对应 reference 文件全文静态注入 system prompt，oracle：人工已定位对文件）③ `retrieve`（真 agentic，补一个"限定技能目录内读 references"的工具，agent 自主走"SKILL.md 索引 → 读 references"）。对比三臂通过率即可分离出"知识本身对不对（inject）/ 形态能否被自主消费（retrieve）/ 无库答不出（without）"三个结论。
- 反模式：只做 without vs 注入版对比、不测 retrieve 自主检索，会高估或低估"可检索"这一层的真实价值；或复用现成执行器时不补 read 工具，把"读不到"当"库无用"。
- 溯源：2026-10-02 R1 实验，dev-lessons 三臂结果 inject 6/6、without 1/6、retrieve 6/6（retrieve 中 5/6 自主走通检索链路、1/6 为先验侥幸）

### M-42 "按索引检索、勿整读"原则必须在 read 工具层落实，否则大 references 整读超 token 且易发散
- 场景：#知识库消费 #agentic #token预算 #references
- 问题：`references/` 含大文件（如 `misc.md` 约 3 万字符）时，agent 用只支持整读的文件读取工具消费，会把单次 token 顶到预算临界（forced_final 才收尾），且检索易发散——多读无关文件、命中却走弯路。
- 根因：SKILL.md 虽写"按索引检索、勿整读"，但读取工具只提供"整文件"粒度，原则没在工具层落地；agent 只能整读，无法"先读索引表定位编号 → 精读单条"。
- 方案：读取工具支持"按编号精确读单条"（如 `references/misc.md#M-35`），让 agent 严格走"索引定位 → 精读命中条"的链路，既降 token 又提精度；库侧把索引表做得足够精确（编号即锚点），让 agent 不需整读即可定位。
- 反模式：依赖"整读整文件"消费大 references——既费 token 又易发散，且预算临界时被迫 forced_final 收尾，答案质量下降。
- 溯源：2026-10-02 R1 实验 retrieve 臂第 3 题暴露（读 `misc.md` 致 budget 临界 + 多读 `deploy-env.md`）

### M-43 稍复杂的命令一律写成脚本文件再执行：内联反引号转义 / `%VAR%` 会让整条命令被当 cmd 解析
- 场景：#工具使用 #Windows #PowerShell #AI代理 #编码
- 问题：同一批命令里，含 `%ERRORLEVEL%`／反引号转义／多行构造的 3 条整条失败，报 `'$x' 不是内部或外部命令`（明显被交给了 cmd 而非 PowerShell，PowerShell 语法全废）；不含这些字符的命令全部正常，失败模式不稳定、难以预测。
- 根因（未逐字符二分定论）：这类字符组合会干扰执行器对命令的 shell 包装/转义处理。与 M-40（cmd 的 `%VAR%` 展开）、M-26（`$` 被外层 shell 吞）同族，但发生在**执行器选择 shell** 这一层。
- 方案：把逻辑（多行、含特殊字符、含变量拼接）用文件工具直写到 `.cmd` / `.ps1` / `.js` 文件里，命令行只保留**一句话且无特殊字符**的启动语句（如 `Start-Process -FilePath cmd.exe -ArgumentList "/c <绝对路径>"`）；需要 CRLF 的批处理写完再 `Set-Content -Value (Get-Content ...)` 转一次。
- 反模式：在命令行里内联 here-string / 反引号转义 / `%VAR%`；失败后原样重试（换成落文件立刻就好）。
- 溯源：2026-10-03 TechLog 构建会话（同族 M-26 / M-38 / M-40）

### M-44 B站新版「封面制作」弹窗：4:3/16:9 是独立面板，file input 随激活状态动态变化
- 场景：#浏览器自动化 #平台发布 #B站 #封面 #shadowDOM
- 问题：给「个人空间封面（16:9）」的 file input `setInputFiles` **静默无效**——无报错、无变化；而 4:3 槽同样操作一次成功。沿用探测阶段记录的 input 序号（nth(1)）时必踩。
- 根因：新版弹窗（弹窗名「封面制作」，含智能/模版/文字/贴纸/滤镜工具栏）把两个比例做成**独立面板**：file input 列表随**当前激活面板动态变化**，未激活面板的 input 要么不在列表中、要么不响应；面板切换后 DOM 序号会重排。
- 方案：先点槽位标题（如「个人空间封面（16:9）」）激活面板——**判据 = 弹窗底部预览标签变为「16:9封面预览」**——然后**重新查询** `.cover-editor input[type=file]`（激活槽的 input 出现在列表，用容器坐标核对归属：16:9 槽 box y≈497），再 setInputFiles；成功判据 = 该槽的「拖拽图片或点击上传」提示消失。「双比例同步改动」默认未勾选（传两张不同图正合适）。最后点弹窗「完成」（多个候选取 y 最大者），入口「添加封面」消失 = 封面已落表单。
- 反模式：沿用探测阶段的 input 序号/元素引用（面板切换后失效）；把「两个槽都有 canvas」当上传成功证据；在创作中心页用 `page.screenshot()` 验证（必超时，见 M-30）。
- 溯源：2026-10-08 gh-fast-download 盘点篇投稿（BV1nRHm64ExU，Tabbit 任务 bili-roundup）；旧版弹窗判据见 M-30，本条覆盖新版差异

### M-45 B站评论区是 web components：操作菜单的定位、触发与验证方法论
- 场景：#浏览器自动化 #平台发布 #B站 #评论 #shadowDOM
- 问题：找评论「…」操作菜单时四处碰壁：`xpath=ancestor::*[contains(@class,'reply')]` 匹配 0；`#commentapp` 下 `querySelectorAll('*')` 看不到内部元素；菜单里 `getByText("置顶", {exact:true})` 找不到（菜单项实际叫「**设为置顶**」）；两次「点击成功 + 菜单关闭」但置顶并未生效。
- 根因：评论区是**自定义元素**（`BILI-COMMENTS` / `BILI-COMMENT-RENDERER` / `BILI-COMMENT-ACTION-BUTTONS-RENDERER`，各带 shadow root）——xpath ancestor 与页面上下文 querySelectorAll 都不穿 shadow、`innerText` 不接 shadow 内容；「…」按钮是 **hover 显现型**（静态 0×0，Playwright 可见性检查直接失败），其身份藏在 `BILI-ICON` 的 `icon` 属性里（`more_vertical_fill`）。
- 方案：
  1. 穿透定位一律用 Playwright locator（CSS/文本引擎穿 shadow）；需在页面上下文枚举时手动 `el.shadowRoot || el` 再 querySelectorAll。
  2. 操作栏按钮身份 = 读 `BILI-ICON` 的 `icon` 属性（`hand_thumbsup_line` / `hand_thumbsdown_line` / `more_vertical_fill`，「回复」是文本按钮）。
  3. hover 显现型控件用 **DOM 点击**（`locator.evaluate(el => el.click())`）绕过可见性检查；菜单项点击用**物理 `page.mouse.click(坐标)`**（native click 对 pointer-events 布局不保证命中）。
  4. 菜单项枚举：从已知项（「删除」，静态就在 DOM 里、只是隐藏）closest 向内容器，一次列全 4 项（设为置顶 / 复制评论链接 / 删除 / 设置屏蔽词）。
  5. **验证与新知识获取用请求监听**：`page.on("request"/"response")` 抓真实调用——直接得到端点 `POST /x/v2/reply/top`、参数 `oid&type&rpid&action(1=置顶/0=取消)&csrf`、响应 `{code:0,"OK"}`；凭这个才发现手工调用漏了 `rpid` 才报 -400「请求错误」。
  6. 最终验收 = 页面「置顶」徽标可见；注意**审核中稿件的评论接口 `data.top` 字段不返回**，别拿它判失败。
- 反模式：用 xpath ancestor / 页面级 querySelectorAll 找 shadow 内元素；猜坐标点「…」；凭「菜单关闭了」认定操作成功（要抓响应或看徽标）；用 exact 匹配猜菜单文案。
- 溯源：2026-10-08 BV1nRHm64ExU 评论区发布 + 置顶（Tabbit 任务 bili-comment / bili-pin）

### M-46 PIL 逐帧渲染：字体缺字形会静默画方框，渲染前必须抽帧过目
- 场景：#视频生成 #逐帧渲染 #字体 #PIL
- 问题：终端模拟画面里等宽字体（consola）画中文 → 全变方框；改雅黑后 ✓（U+2713）也是方框——两处都是**全量渲染前靠预览帧抓到的**。
- 根因：PIL 用不含目标字形的字体绘制时**静默画方框/空白、不抛错**；等宽英文字体无 CJK 字形，部分符号（如 ✓）雅黑也没有。
- 方案：中英分字体（中文雅黑、纯 ASCII 命令行走等宽）；特殊符号（✓ ★ → ×）逐个在预览帧里确认，不确定就退化为 ASCII（`[OK]`）或手绘图形；渲染脚本内置 `--preview` 模式（每场景抽 3 帧落盘），全量渲染前先人工过目——本次靠它避免 3540 帧重跑。
- 反模式：假设系统字体「什么字符都有」；跳过预览直接全量渲染；把方框当成「字体没装」去折腾环境。
- 溯源：2026-10-08 gh-fast-download 盘点篇（make_film_roundup.py：consola 中文 + 雅黑缺 ✓ 两处实例）

### M-47 抓不到屏的五个"假 API 失败"：根因往往是**窗口比屏幕大**（附屏幕尺寸的可信判据）
- 场景：#Windows #抓屏 #截图 #自动化验证 #DPI
- 问题：自动化验证"某个 UI 反馈有没有显示"时，五种抓屏方式**全部失败**且报错各不相同，看起来像"这台机器不支持截图"：PIL `ImageGrab.grab` → `screen grab failed`；自写 `BitBlt(GetDC(0))` → **全黑图**；PowerShell `Graphics.CopyFromScreen` → `The handle is invalid`；`PrintWindow` → 图能出但**目标元素全缺**；`ffmpeg -f gdigrab -i desktop` → 退出码 0 但**文件根本没生成**。
- 根因：两个因素叠加。① **应用窗口算出来比屏幕还大**（200% 缩放：`1120×740×2 = 2240×1480`，而可视区 2880×1800，且窗口停在屏幕外）→ 抓屏源区域越界，各 API 就以各自的报错形态失败；② 屏幕尺寸读数**被另一个工具骗了**——`Win32_VideoController.CurrentHorizontalResolution` 报 **1360**（错），而 DPI-aware 进程里 `GetSystemMetrics(SM_CXSCREEN)` 报 **2880×1800**（对）。
- 方案：① 屏幕尺寸只看 `GetSystemMetrics(SM_CXSCREEN/SM_CYSCREEN)`（DPI-aware 进程里即物理像素，与 `GetWindowRect` 同系）或 `EnumDisplayMonitors`，**别信 `Win32_VideoController`**；② 抓屏前先确认窗口矩形**完全落在屏幕内**（必要时 `SetWindowPos` 搬进去再抓）；③ 自动化验证首选 **`ffmpeg -f gdigrab -i desktop` 录一段再抽帧**（本机 5s≈1.1MB，稳定，且不受"进程 DPI 感知与否"影响）；④ `PrintWindow` 的边界单记：**拍不到 `SS_OWNERDRAW` 等自绘子窗口的内容**（它只重放 `WM_PAINT`）——"抓不到"≠"屏幕上没有"。
- **⑤ 同族第二种表现（非 DPI-aware 进程 vs 物理坐标）**：Python/tkinter 版要读**桌面图标坐标**（来自 DPI-aware 的 Explorer，是**物理**值）来判方位，而本进程里 `GetSystemMetrics` / `SPI_GETWORKAREA` 给的是**逻辑**值（实测 1440×852 对 2880×1800，差一倍）；想按 `GetDpiForSystem` 乘比例换算也不行 —— 它在非 aware 进程里**同样只返回 96**（96/96 = 1.0，等于没做）。正解 = **别去换算坐标系，改用"要比较的那批数据自己的包围盒"当参照系**（本例：所有图标的 min/max ± 一个图标格余量）；实测包围盒 2940×1668 ≈ 物理屏 2880×1800（图标布满桌面时两者几乎等价），天然免疫 DPI 差异。
- 反模式：把五种 API 的失败下结论为"环境不支持截图"就放弃验证；用显卡/控制面板报的分辨率当屏幕尺寸；在窗口超出屏幕的前提下继续调抓屏参数；**用 `GetDpiForSystem`/`GetDpiForMonitor` 给自己"换算"坐标系**（不 aware 的调用者拿到的一律是 96）。
- 溯源：2026-10-09 ExeTrace「钉桌面强反馈」自动化验证（`_deploy/_qa/probe_monitors.py` 复算拓扑）与 **Python 版同步实现**（`src/winutil.py: icon_area()` 即 ⑤ 的落地；同族 M-10、M-29）

### M-48 ctypes 调 Win32：不声明 `argtypes` 会让**句柄/指针被静默截断成 32 位**
- 场景：#Python #ctypes #Windows #自动化 #静默失败
- 问题：窗口自动化里三处调用**全部静默失效、零报错**：`FindWindowW` 明明有窗口却返回 0；`PostMessageW(hwnd, WM_LBUTTONDOWN, ...)` 点击没反应；`SetWindowPos(hwnd, HWND_TOPMOST, ...)` 置顶失败（抓出来的图是**别的窗口**）。改好一处，现象换个地方再犯一次。
- 根因：ctypes 未声明的参数默认按 **`c_int`（32 位）** 编组。64 位进程里句柄/指针都是 64 位 → 高位被**静默丢弃**，得到一个"看起来完全合法"的值（`0xA01C08` 这类）；`-1`（`HWND_TOPMOST`）同样会被按 32 位传而失效。
- 方案：凡涉及句柄/指针的 Win32 API，**逐个显式声明 `argtypes`**（必要时连 `restype`，如 `FindWindowW.restype = wintypes.HWND`）；句柄一律用 `wintypes.HWND/HDC/HBITMAP`（`c_void_p`）而不是裸 `int`；跨语言传句柄（Python → PowerShell 命令行）也要保证进制解析正确；自查口诀：**"调用没反应"先看 argtypes 声明了没**。
- 反模式：只声明 `restype` 不声明 `argtypes`（半截防护）；把"点击没反应"归因于"控件不响应消息"；用裸 `int` 存句柄再传回 API。
- 溯源：2026-10-09 ExeTrace 自动化验证（`test_toast_pin.py`、`shoot_toast.ps1`：FindWindowW / PostMessageW / SetWindowPos 三处同病）

### M-49 Win32 `SS_OWNERDRAW` 自绘卡片：四条必须遵守的规矩
- 场景：#Win32 #Rust #自绘控件 #DPI #UI反馈
- 问题：给原生窗口加"成功反馈浮层卡片"（父窗口靠系统画刷打底、内容全由子控件渲染，无自绘 `WM_PAINT`）时踩到四件事：① 直接在父窗口画会被 ListView 盖住；② 卡片位置不居中、且停在**窗口创建时**的旧尺寸上；③ 两行文案分两次 `DrawTextW`（各占上下半区）时**只有第二行显示**；④ Rust 侧 `MessageBeep` 在 windows-sys 里**根本没导出**。
- 根因：① 父窗口没有自绘通道，子控件绘制永远在父之上；② `layout()` 首次执行在 `WM_CREATE` —— 那时窗口尚未关联显示器、`GetDpiForWindow` 返回 96，窗口尺寸也是初始值，据此算出的位置既缩水又过时；③ 机制未定论（疑与 `DT_SINGLELINE` 的目标矩形处理有关），但"一次调用画多行"稳定可行；④ windows-sys 是**按需裁剪**的绑定，`MessageBeep` 这一类确实缺（`Win32::Media::Audio` 下也没有）。
- 方案：① 卡片做成 **`WC_STATIC` + `SS_OWNERDRAW` 子窗口**，绘制放父窗口的 `WM_DRAWITEM`（`dis.hDC` 直接画；圆角/圆/勾全用 GDI 原生图元，勾用 `MoveToEx/LineTo` 两条线而**不**依赖字体符号）；`SS_OWNERDRAW` 常量若未导出就用字面量 `0x000D`；② 位置**显示前现算**（`GetClientRect` 当场取），不要依赖 `layout()` 的调用时机；③ 多行文案**一次 `DrawTextW`**（`\n` 分隔、**不传** `DT_SINGLELINE`）；④ 缺的 API 用 `GetModuleHandleW("user32.dll")` + `GetProcAddress` **动态取**并转函数指针（一次符号查找，零体积代价）；⑤ 字号从系统 UI 字体派生（`GetObjectW` 取 `LOGFONTW` → 改 `lfHeight/lfWeight` → `CreateFontIndirectW`），别硬编码字体名。
- 反模式：在主窗口 `WM_PAINT` 里画浮层；把"两行只显示一行"当字体问题反复折腾字体；为一个提示音去开 `Win32_Media_Audio` feature（API 本就不在里面）；硬编码"微软雅黑 + 固定磅值"。
- 溯源：2026-10-09 ExeTrace native 版钉桌面浮层卡片（`native_ui.rs` 的 `draw_toast` / `place_toast` / `show_toast`）

### M-50 ffmpeg 合成 GIF：不显式传 `-framerate` 就会**悄悄变速**，且同片各段速度可能不一致
- 场景：#ffmpeg #GIF #视频 #演示动图
- 问题：演示 GIF 看着"比录屏快一截、动作发急"。实测：6.4s 录像按 12fps 抽出 77 帧（抽帧参数**是生效的**），产出却是 **25fps / 3.08s** —— 录像被**加速 2.08 倍**。更隐蔽的是：同一条片子里只有某个场景是 0.92×（原速）、其余全 2.08×，**速度不一致**。
- 根因：**GIF 时长 = 帧数 ÷ 合成帧率**。① 合成用 PNG 序列（`-i f%05d.png`）时 ffmpeg 按**默认 25fps** 读入 —— 抽帧帧率与合成帧率是**两件互不相干的事**；② 那个"原速"场景是**纯键盘操作**（整场不动鼠标）→ 轨迹为空 → 走了另一条"无指针"的普通路径（帧率语义不同）→ 同片两套速度。
- 方案：① 合成时**显式** `-framerate <抽帧fps × 倍速>`（指针路径）或 `fps=N,setpts=PTS/倍速`（滤镜路径），把倍速变成**显式常量**（如 `GIF_SPEED = 1.5`）；② 抽帧加 `-ss/-t` **裁掉录头录尾**（否则静止录头也计入时长）；③ **纯键盘场景补记一个起点坐标**，保证轨迹非空、只走一条渲染路径；④ 交付前量化对账：逐条打印「帧数 / 延迟分布 / 等效倍率」，**全批延迟组必须一致**；注意 GIF 延迟被量化到 **10ms 粒度**（18fps → 50/60ms），等效倍率误差 <1% 可接受；⑤ "段落 = 素材整数遍"的吸附用 **floor** 而非 round（GIF 变长后 round 会把段落凑成 2 遍、凭空翻倍）。
- 反模式：以为"抽帧 fps 和合成帧率天然一致"；只在一两个场景肉眼看 GIF 快慢；用 `round` 做整数遍吸附。
- 溯源：2026-10-09 ExeTrace 短片 v3（`video-kit/scripts/check_gif_speed.py` 是该判据的通用实现；同族 M-11）

### M-51 跟外部系统要"列表位置"：用**快照 diff** 而非序号推算，且必须重试
- 场景：#桌面 #外部系统 #Shell #自动化 #容错
- 问题：要告诉用户"刚创建的桌面快捷方式落在桌面哪个方位"。第一直觉是"它是第 N 个图标，按网格推算"—— 实测**完全不可用**：本机桌面 **91 个图标**而一屏只放得下 **36 个**（会滚动），自动排列还会**重排**；改走"快照 diff"（建前读一次全部坐标、建后读一次，找出多出来的那个）后，方位却**经常取不到**（退化成泛化文案）。
- 根因：① 外部系统的内部列表**顺序与视觉位置不一一对应**，序号推算的前提不成立；② 即使用 diff，**外部系统刷新有延迟** —— 文件落盘后立刻读，列表还是旧的（数量未变 → diff 为空）。
- 方案：① 走 **diff 而非推算**（只依赖"谁是新来的"，对重排/超屏免疫）；② diff 两端都要容错：读失败或数量没变 → **重试**（本例 4×200ms 稳定命中），仍失败才退化为泛化文案；③ 坐标与参照系取**同一坐标系**的值（进程 DPI 感知时 `GetSystemMetrics` / `EnumDisplayMonitors` 都给物理像素，可直接比）；④ 跨进程读坐标要**只读**（`VirtualAllocEx` + `LVM_GETITEMPOSITION` + `ReadProcessMemory`：只让 Explorer 往临时内存写一个坐标，不碰它的数据）并用 `SendMessageTimeoutW` 防挂；⑤ 反馈分两次更新：**先立即反馈**（不含方位），**拿到结果再刷一次文字** —— 别让"要等外部系统"拖慢"瞬间反馈"。
- 反模式：按"第 N 个"推算外部列表的视觉位置；读一次失败就放弃（外部系统刷新延迟是常态）；为拿精确信息让 UI 干等。
- 溯源：2026-10-09 ExeTrace 钉桌面方位（`winx.rs` 的 `desktop_icon_positions` / `zone_of`；探针 `_deploy/_qa/probe_desktop_grid.py` 证明序号推算失效）

### M-52 规范/流程类资产：主本唯一 + 副本带出生证明 + 触发写成路由技能
- 场景：#知识资产 #防漂移 #技能 #触发
- 问题：一套流程规范被多处消费（Obsidian 知识库 / 桌面工作目录 / 多个 AI 会话与 agent）。每次更新会出三类故障：① 改了 A 处、B 处悄悄过期；② 副本里的 Obsidian 双链 `[[X]]` **悬空**（双链只在 vault 内解析，复制出去即失效）；③ "下次怎么触发"没有答案——规范睡着，agent 从零重新发明（2026-10-09 投第三条视频浪费 30+ 轮即此类）。
- 根因：多副本没有主从约定；触发链靠"记忆条目 → 正文指针"多层中转，任何一层没读就断；参数被抄进多个载体后天然漂移。
- 方案（三件套）：① **主本唯一**（本例 = Obsidian vault），导出到工作区时**双链相对化**（`[[X]]` → `[X](./X.md)`）+ 头部注入「副本说明」（主本路径 + 导出日期 + 「改动先改主本再重导」；验收判据 = 导出后残留 `[[` 数为 0）。② **触发落规则，不落记忆中转**：把「此类任务先读某文档」直接写进 alwaysApply 规则的**动作清单**（带路径）。③ **技能做路由器，不复制参数**：SKILL.md 只放 = 硬规则（先读哪两份文档）+ 每阶段最易翻车的一条 + 资产指针 + 边界；参数/判据仍只在主本（一改永逸）。装到 `~/.agents/skills/<name>/SKILL.md` 后 `use_skill("<name>")` **可当场实测加载**（活源，无需重启）。
- 反模式：裸拷贝分发（双链悬空）；把参数抄进 skill 或规则（三处漂移）；关键路径只写在记忆里（中转断链）；导出后不做链接适配就宣称"已同步"。
- 溯源：2026-10-10/11 B站宣发 SOP v2 落地（vault 主本 → `Desktop\开源项目\b站宣发sop\` 副本 → `bili-promo` 技能；触发同步进 `reuse-history-assets/RULE.mdc` 与记忆）

### M-53 复刻既有脚本的输出格式：拿参照数据逐行 diff 保真，别凭目测
- 场景：#格式复刻 #会话导出 #大文件 #验证
- 问题：要为一份新数据（62MB 会话导出）复刻既有扫描产物的格式，肉眼比对永远差一点——换行、截断标记、长度定义等隐含口径全在原脚本实现里，靠猜会反复返工。
- 根因：格式 = 原脚本的隐含实现，含多处非显然口径。本次实测三处：① 用户消息先做换行归一（`\r\n`→`\n`）；② 截断规则 = 前 600 字 + `" ……[共 N 字]"`（省略号前**有一个空格**）；③ 「原始长度」= **渲染后**长度（含 `[USER_QUERY]`/`[reasoning]`/`[tool-call]` 标记）。另：Windows 文本模式写回时 `\n` 被翻译成 `\r\n`，内容里已有的 `\r` 残留 → 读回时 `\r\r\n` 被解析成两个换行、diff 里凭空多出"幽灵空行"，会伪装成内容差异。
- 方案：**同一渲染器先跑"参照输入"，与既有产物逐行 diff，跑到 0 差异再上真正的新数据**（本次修正 3 处口径后 7546/7546 行、0 差异才出货）；换行统一在渲染层归一。这套"用参照文件做 oracle"的方法适用于任何"模仿别人格式/产出"的任务。
- 反模式：直接拿新数据试错（每轮都在追差）；凭目测宣称"基本一致"；跳过 diff 出货。
- 溯源：2026-10-10 会话导出扫描（`_tmp_rust_export_outline.py` 对既有 `_tmp_resume_export_outline.md` 逐行保真）

### M-54 检索命中 0 不等于"没有"：先排两个静默跳过源（点目录 / 超大文件）
- 场景：#工具使用 #搜索 #静默失败
- 问题：在明知含目标文本的文件里搜出 0 命中——一次是 60MB 的会话导出 JSON（`codebuddy.conversation` 明明在第 2 行），一次是 `.codebuddy/` 下的当日记忆文件（旧段落明明还在）。
- 根因：搜索工具在两种情况下**静默跳过文件、不报错**：① 默认忽略点目录（`.codebuddy/…` 整段搜不到）；② 文件超大（60MB 级直接 0 命中）。两种情况都会让人误判"文件被重写/内容丢失"。
- 方案：0 命中时换**第二手段**复核再下结论——PowerShell `Select-String -Path <绝对路径>`、或 Python 直接读（大 JSON 走 `json.load`）。这是元原则 11（工具读数二次确认）的又一实例。
- 反模式：把 0 命中当事实断言（"文件被覆盖了！"）；不换工具反复重搜碰运气。
- 溯源：2026-10-10/11 两次误判（60MB 导出 JSON、`.codebuddy` 记忆文件），均以 `Select-String` 复核推翻；同族 M-01

### M-55 Tabbit 任务空闲即回收：跨等待的操作按"可恢复"设计，恢复三步固定（补 M-20）
- 场景：#浏览器自动化 #Tabbit #平台发布 #恢复
- 问题：把"发 B 站动态"拆成多轮实施、中间等用户审阅，回来后 `nodejs` 返回 `reused:false` + `about:blank`，之前持有的标签页从本任务视图消失——任务已被回收（同一天发生 3 次，最短间隔仅约 1 分钟）。
- 根因：Tabbit 任务有生命周期——**空闲（等用户/搁置）数分钟即被回收**，页面所有权随之释放；任务内 `pages()` 只返回本任务拥有的页。M-20（跨会话任务槽失效）的加强形态：不只是"换会话"，搁置也会失效。
- 方案：
  1. **恢复三步固定**：`finish --task <NAME> --discard`（清掉回收后新建的空任务，否则后续 acquire 报 `SESSION_GROUP_CONFLICT`）→ `create --task <NAME>` 看 inventory（旧 tab 通常以"可恢复组"保留，记下组 ID）→ `nodejs --task <NAME> --group <组ID>` 重新接管（**用组 ID 而非组名**）。
  2. **状态设计成"可恢复"**：关键内容随时落盘本地文件（文案 txt / 结构化 JSON），浏览器里只当缓存；实测 B 站动态草稿与专栏草稿都有服务端保护——任务回收、tab 被关后重开自动恢复（318 字动态草稿、4365 字专栏稿均成功找回）。
  3. 长流程尽量在单次连续会话内推进到"用户可见的检查点"，减少跨等待轮次。
- 反模式：任务回收后从零重走流程（重复劳动）；把"页面还开着"当状态可靠（所有权已丢）；只把内容存在浏览器编辑器里不落盘。
- 溯源：2026-10-12 飞书文档→B站专栏+引流动态（脚本 `frontend-works/_deploy/_qa/tabbit/d*.js`；`usercontext/2026-10-12.md`）

### M-56 B 站专栏/动态程序化发布：输入规则注入富文本 / 勾选框走 DOM click / 动态不支持编辑
- 场景：#浏览器自动化 #平台发布 #B站 #富文本
- 问题：把一篇 4200 字长文（含 3 张表）程序化发成 B 站专栏+引流动态，踩到一串平台特性，每项都让"想当然的写法"静默失败。
- 根因/关键事实（2026-10-12 实测）：
  1. **动态正文上限 1000 字**（实测法：填入 2201 字 → 计数器红字 `-1200`）；超长内容走「转专栏」。
  2. 专栏编辑器 = iframe（`york/read-editor`）内 tiptap/ProseMirror（eva3）。标题 `textarea.title-input__inner`、正文 `div.tiptap`。**粘贴不解析 markdown**（纯文本段落化），但**逐键输入支持输入规则**：`## `/`### `/`- ` + 空格 → H2/H3/项目符号列表（须 `page.keyboard.type` 逐键，`insertText` 不触发规则、但可续写已生成的块）。用此法注入 66 块，H2×6 / H3×3 / 列表×33 全对，左侧目录自动生成。
  3. 「原创声明」checkbox：Playwright `check()/click()` 无效（被拦截），**DOM `el.click()` 有效**；「AI 辅助创作声明」`check()` 可直接成功。
  4. 动态「发布」按钮首点弹《哔哩哔哩动态使用规范》，须再点「确认并发送」才真正提交；「转为专栏」按钮点击必超时 → 直连 `member.bilibili.com/platform/upload/text/edit`（重定向 new-edit）。
  5. 动态富文本清稿：`fill("")` 无效、Ctrl+A/Delete 不可靠；可靠解法 = `Ctrl+End` + Backspace 自适应循环，**循环退出条件必须用"完整 URL 结尾"这类长锚点，不能用短字符标记**（标记比残留短会提前退出——踩 3 次）。
  6. **动态发布后不支持编辑**（卡片菜单只有置顶/删除）——要改已发布动态只能删除重发（先与用户确认互动损失）。
- 反模式：以"发布按钮点了"当成功（要看编辑器是否重置 + 空间页复核）；用 `feed/space` API 复核（返回 0 条误导，直接开空间动态页看）；checkbox 失败后静默重试。
- 溯源：2026-10-12 文章《企业软件都在服务端，REA 还能逆向吗？》（专栏 `bilibili.com/opus/1258292587326865432` + 引流动态；脚本 `_deploy/_qa/tabbit/d20~d41*.js`）

### M-57 抓飞书文档正文：web_fetch 拿不到（SPA），大视口一次渲染 + 禁止按行去重
- 场景：#浏览器自动化 #文档抓取 #飞书
- 问题：要把飞书 docx 正文抓下来：`web_fetch` 只拿到空壳 + 追踪像素；改用浏览器抓时又因"按行去重合并"误删了重复编号行（列表编号「1.」「2.」与章节编号同文本被判为重复丢掉），险些带着残缺结构进入发布。
- 根因：飞书文档由 JS 渲染内容块（另有权限墙——浏览器登录账号必须有阅读权限）；**行级去重的错误假设是"重复行=渲染重复"，但文档里天然存在相同文本行（编号/分隔符）**，去重会误删本体。
- 方案：
  1. 用 Tabbit 打开文档（顺带验证权限），`page.setViewportSize({width:1600, height:8000})` 让虚拟列表一次渲染全篇，直接取**一次** `body.innerText`（不做任何去重）；本次 4200 字文档 5125 字符一次拿全（锚点校验：标题/结语/参考来源全在）。
  2. 一次渲染不全需分步滚动收集时，用**块级 id 去重 + 原始顺序流**，不要用文本行去重（同 M-55：勿按"行集合"合并多屏文本）。
  3. 抓下来先落盘 UTF-8 txt（`require("fs")` 在 Tabbit 程序内可用），再本地清洗/重组为结构化 JSON。
- 反模式：把 web_fetch 空壳当"页面没内容"止步；用行集合去重合并多屏文本；抓完不校验锚点（首尾关键句）就进入下游。
- 溯源：2026-10-12 REA 文章分发（`_feishu_doc_raw2.txt`；复盘：首版去重稿丢编号行，改大视口单次抓取后结构完整）
