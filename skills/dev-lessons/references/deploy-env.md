# 部署与环境踩坑

场景标签：`#部署` `#DevOps` `#环境配置`

## 条目索引（按编号或关键词检索：**先用 search_content 搜编号 / 关键词，勿整读本文件**）

| 编号 | 标题 | 场景标签 |
|---|---|---|
| E-01 | 前端缓存：hash chunk 部署后的强制刷新 | #部署 #前端 #Vite |
| E-02 | MOCK 数据残留 | #前端 #联调 |
| E-03 | 可选依赖优雅降级 | #后端 #环境配置 |
| E-04 | SSH/远程命令的转义与验证 | #运维 #远程服务器 |
| E-05 | 同名包 editable 安装跨项目互相顶掉 | #环境配置 #Python #多副本 |
| E-06 | 根目录临时脚本被 pytest 收集并真实调用外部 API | #测试 #环境配置 #安全 |
| E-07 | 控制台 GBK 渲染制造的“假性乱码” | #Windows #排查 #编码 |
| E-08 | 本地 QA 静态服务器的根目录必须对齐生产 URL 前缀 | #QA #静态资源 #本地调试 |
| E-09 | 长任务（渲染/转码）前先看可用内存：本机守护会静默杀进程 | #环境 #Windows #内存 #渲染 |
| E-10 | 打 exe 前先问"构建环境干净吗"：同一个 spec，33 MB vs 207 MB | #打包 #PyInstaller #Windows #发布 |
| E-11 | 冻结/打包后的路径模型：可写数据与只读资源必须分开定位 | #打包 #PyInstaller #路径 #数据丢失 |
| E-12 | 发布流水线要自带把关，验收要针对"下载下来的资产" | #发布 #GitHubActions #验收 |
| E-13 | Windows 计划任务做"守护自愈"的正确配方（含三个必踩的坑） | #Windows #运维 #常驻服务 #可靠性 |
| E-14 | SSH 交互式会话老掉线：客户端保活 + tmux（服务端 ClientAliveInterval=0 也不代表安全） | #SSH #运维 #Linux #保活 |
| E-15 | 官方安装器的"安装目录守卫"与程序自写目录冲突：自己拦自己的更新 | #Windows #桌面应用 #升级 #自检守卫 |
| E-16 | 发版卫生：版本号同步点先枚举，tag 首推失败可安全重建 | #发布 #GitHubActions #版本号 |
| E-17 | 交付验收的“采样时机”假红：等状态落定再判定 | #验收 #脚本 #假红 |
| E-18 | 长任务在“内存守护”边缘的跑法：按守护阈值设门禁 + 产物可续跑 + 压进程内存 | #环境 #Windows #内存 #渲染 #长任务 |
| E-19 | 发布资产在这台机器传不上去：把构建与挂载搬到 runner（`workflow_dispatch` 补挂老 tag） | #发布 #GitHubActions #网络受限 #代理 |
| E-20 | Windows 交付物的“双击可用”：一个 .cmd 启动器 + 新机器两道闸（含 batch 的括号与行尾坑） | #Windows #交付 #PowerShell #首次运行 |
| E-21 | 增量部署的两条硬规矩：先量代码差集、再让"验证通过才重启" | #部署 #远程服务器 #systemd #验证门禁 |
| E-22 | 第三方嵌入"代码里配了"≠线上可用：缺 env 时渲染 undefined 坏区块 | #部署 #环境配置 #第三方嵌入 #验收 |
| E-23 | 前端构建被环境变量静默改写 API 基址：页面"全空白 + 连接中断" | #部署 #前端 #Vite #环境配置 |
| E-24 | 手动起的常驻服务不落输出：崩溃后死因不可考 | #运维 #Windows #常驻服务 #可靠性 |
| E-25 | 内存守护会杀掉 `next build`：用 protect-list.txt 热加载白名单临时豁免 | #环境 #Windows #内存 #长任务 #构建 |
| E-26 | Android APK 发版前必查 `launchable-activity`：安装成功 ≠ 有桌面入口，目检常量不可信 | #发布 #Android #打包 #验收 |

### E-01 前端缓存：hash chunk 部署后的强制刷新
- 场景：#部署 #前端 #Vite
- 问题：发版后用户端运行时报错，代码明明已修复。
- 根因：Vite hash chunk + 浏览器缓存，旧 JS 与新 API 不匹配。
- 方案：nginx 加 `Cache-Control` 策略（index.html 不缓存，hash 资源长缓存）；引导用户强刷；**E2E 验收必须在真实部署环境做**，本地 dev server 验不出缓存问题。
- 溯源：luyan/docs/2026-06-28-开发经验总结.md

### E-02 MOCK 数据残留
- 场景：#前端 #联调
- 问题：角色筛选器初始值用了 MOCK 角色 ID，接真实后端后筛选全部失效。
- 方案：联调切换清单里加"清除 MOCK 常量"一项；初始值用语义值（`'all'`）而非具体 ID；上线前 grep 一遍 MOCK/mock 常量。
- 溯源：luyan/docs/2026-06-28-开发经验总结.md

### E-03 可选依赖优雅降级
- 场景：#后端 #环境配置
- 问题：本地无 SMTP 时注册流程直接崩；未配 GitHub OAuth 密钥时服务起不来。
- 方案：可选外部服务全部走"降级运行"——无 SMTP 时控制台打印验证码；无 OAuth key 时隐藏登录入口并 log 警告，进程不崩。启动时做依赖检查并明确报告哪些功能处于降级态。
- 溯源：frontend/项目开发总结.md

### E-04 SSH/远程命令的转义与验证
- 场景：#运维 #远程服务器
- 问题：SSH 执行含 JSON 的命令时转义出错，改动静默失败。
- 方案：远程改配置后必须回读验证（cat 回来 diff）；复杂变更写成本地脚本 scp 过去执行，不在命令行内联长 JSON。
- 溯源：frontend/项目开发总结.md

### E-05 同名包 editable 安装跨项目互相顶掉
- 场景：#环境配置 #Python #多副本
- 问题：`pytest` 大面积报字段缺失（如 KeyError、缺少某的输出字段），但代码里明明有该字段；同一份代码换个环境却全绿。
- 根因：本机在多个目录对**同名包**做过 `pip install -e .`，后一次 editable 安装覆盖了前一次的 finder/`.pth`，`import` 实际指向另一个副本的旧代码。症状酷似真实回归，极易误判。
- 方案：
  1. 先定位真身：`python -c "import <pkg> as m; print(m.__file__)"` —— 路径不对就不要继续查业务代码；
  2. 卸载错误副本后在项目目录重装：`pip uninstall -y <pkg>` → `pip install -e ".[extras]"`；
  3. `PYTHONPATH=src` 只能临时验证，别当长期方案；
  4. 多项目并行时各自用 `.venv`，从根上隔离。
- 反模式：看到字段缺失就认定回归去改产品代码；或长期靠 PYTHONPATH 掩盖。
- 溯源：2026-09-10 接手 AI-driven-viral-content-analysis-system（本机另有 GitHub 开源同名副本，造成 8 个假失败）

### E-06 根目录临时脚本被 pytest 收集并真实调用外部 API
- 场景：#测试 #环境配置 #安全
- 问题：在仓库根目录跑 `pytest` 耗时近 2 分钟并失败，期间**真实调用了外部付费/限流 API**（返回 402）。
- 根因：`test_*.py` 命名的一次性调试脚本散落在根目录，被 pytest 默认收集；它们是脚本不是测试（无 fixture，直接 NameError），部分还会在收集阶段就发请求。
- 方案：在 `pyproject.toml` 固化 `[tool.pytest.ini_options] testpaths = ["tests"]`；一次性脚本归档到 `scripts/_scratch/` 并 gitignore；接手陌生仓库先用 `pytest --collect-only -q` 看会收集什么。
- 反模式：把调试脚本命名为 `test_*.py` 放在根目录；为了让脚本“通过”而给它补 fixture。
- 溯源：2026-09-10 同上项目

### E-07 控制台 GBK 渲染制造的“假性乱码”
- 场景：#Windows #排查 #编码
- 问题：API 输出里 `→` 显示成 `鈫?`、`衰退期` 显示成 `琛伴€€鏈?`，怀疑源码双重编码。
- 根因：Windows PowerShell 5.1 控制台默认以 GBK 渲染 UTF-8 文本，`Get-Content` / `Out-String` 出来的中文全是假乱码；源码与返回值本身是正确的 UTF-8。
- 方案：
  1. 用第二种工具交叉验证（如 `python -c` 读同一个文件或请求），不要据控制台下结论；
  2. 核对时用 `repr()` 或 `[hex(ord(c)) for c in s]` 打印码点，肉眼不可靠；
  3. 确认是工具假象后再决定是否改代码 —— 误改会把正确字面量改坏。
- 反模式：看到乱码就做“大规模编码重写”；未确认前直接替换字符串。
- 溯源：2026-09-10 同上项目（一度误判为源码缺陷，结论已更正）

### E-08 本地 QA 静态服务器的根目录必须对齐生产 URL 前缀
- 场景：#QA #静态资源 #本地调试
- 问题：本地 `python -m http.server --directory web/static` 起服务后，页面里 `<video src="/static/motion/x.mp4">` 全部 404（video `error.code=4`），误以为文件损坏。
- 根因：生产路由是 `/static` → `web/static`，本地服务器把 `web/static` 当根目录后，绝对路径 `/static/...` 会多挂一层前缀。
- 方案：根目录选**生产 URL 前缀的父目录**（`--directory web`，URL 走 `/static/landing.html`）；起服后先 curl 一个引用资源验证 200 再跑页面 QA。
- 反模式：看到资源加载失败先怀疑文件本身或 MIME 类型；换端口反复重试。
- 溯源：2026-09-11，landing 背景视频去水印后的浏览器 QA（Doubao-Watermark-Session-Summary.md）

### E-09 长任务（渲染/转码）前先看可用内存：本机守护会静默杀进程
- 场景：#环境 #Windows #内存 #渲染
- 问题：Python/ffmpeg 渲染跑到一半"无声消失"，调用方拿到的报错是**空字符串**（`ffmpeg 失败：`），既不像 OOM 也不像异常；重跑有时又能过，像玄学。
- 根因：本机装了内存守护（`tools/memory-guard/`，<12% 警告、<7% **杀掉工作集最大的进程**、每小时上限 6 次）。渲染任务往往正好是最大的那个；被杀时进程直接消失，异常信息全丢。
- 方案：
  1. 长任务前先查可用内存（`Get-CimInstance Win32_OperatingSystem` 的 `FreePhysicalMemory`），低于阈值先腾内存（本机常见大头：浏览器多进程、IDE 的 `git status -z -uall` 周期扫描）；
  2. 失败时**先看守护日志** `tools/memory-guard/logs/` 有没有 ACTION 记录，再决定重试还是排查；
  3. 区分两类"中断"：**进程起来就退出（rc=0）** 通常不是守护干的，而是工具自身启动抖动（如 msedge 逐帧截图偶发 `TargetClosedError`/浏览器秒退）→ 直接重跑即可；
  4. 渲染任务**串行跑**，别并行开两个（两个都容易被杀）。
- 反模式：把"无输出的失败"一律当代码 bug 查；内存临界时并行开渲染；把所有中断都归因于杀软/守护而不看日志。
- 溯源：2026-09-21 flowwatch 视频重渲与 B 站卡片渲染（守护日志 08:21–08:29 记录杀过屏保/Tabbit；msedge 抖动见当天交接文档坑表）
### E-10 打 exe 前先问"构建环境干净吗"：同一个 spec，33 MB vs 207 MB
- 场景：#打包 #PyInstaller #Windows #发布
- 问题：同一个 PyInstaller spec，在开发机（conda 基环境）打出 **207 MB**；在只装了运行依赖的 venv 里只有 **33 MB**。多出来的是 jieba / sphinx / babel / jedi / PyQt5 这类谁都没 import 的东西。
- 根因：PyInstaller 的依赖分析受构建环境污染 —— site-packages 里被其它工具/包带进来的模块、被 hook 扫到的可选依赖都会被收进 `_internal/`。环境越"全能"，产物越胖。
- 方案：
  1. 专门建构建用 venv：`python -m venv .venv-build` → `pip install -r requirements.txt pyinstaller`；
  2. `--workpath/--distpath` 指到仓库外（`dist/`、`build/` 本就在 .gitignore）；
  3. **形态选择**：onedir > onefile（启动快、杀软误报少）；`upx=False`（压缩率换不来误报率）；
  4. 打包放 CI 也顺带解决污染 —— runner 天然是干净环境。
- 反模式：在 conda 基环境 / 日常开发环境里直接打 exe 并当成"体积正常"；为了"单文件好看"选 onefile。
- 溯源：2026-09-21 flowwatch `packaging/flowwatch.spec`（写进 spec 头部与 README）

### E-11 冻结/打包后的路径模型：可写数据与只读资源必须分开定位
- 场景：#打包 #PyInstaller #路径 #数据丢失
- 问题：exe 能跑、界面能开，但历史库与助手记忆每次重启就空 —— 数据写进了临时解包目录（`sys._MEIPASS`），退出即清；自启注册的命令还指向不存在的 `server.py`。
- 根因：打包后 `__file__` 指向**只读的临时解包目录**；凡是"以 `__file__` 为基准推导可写路径"的地方全部失效，且这些推导散落在多个模块（DB、配置、`.env`、用户数据目录、临时工作目录），还有"把 `__file__` 写进注册表"这种隐性依赖。
- 方案：
  1. 新增**唯一的** `datadir.py`：`frozen → 可执行文件所在目录 / 否则项目目录 / 支持环境变量覆盖`（`FLOWWATCH_DATA_DIR`）；
  2. 所有运行期数据路径改走它；全仓搜一遍 `__file__`，把自启命令、相对资源这类隐性依赖一并处理；
  3. 冻结分支单独验收：解压到干净目录运行，**断言数据落在 exe 旁边**（而不是"能跑就行"）。
- 反模式：只在入口脚本里 `if frozen` 打个补丁；靠 `chdir` / 相对路径碰运气；把写操作留在 `_MEIPASS`。
- 溯源：2026-09-21 flowwatch（`datadir.py` + assistant / server / notes / collector / autostart 六处；实测数据落在 exe 旁边）

### E-12 发布流水线要自带把关，验收要针对"下载下来的资产"
- 场景：#发布 #GitHubActions #验收
- 问题：tag 推送后 Release 里只有 Source code 两个 zip —— 用户得装 Node、开两个终端才能看到界面；而且**按分支过滤的 CI 不会在 tag 上跑**，等于发版没有测试把关；本地构建通过 ≠ 发布物可用（CI 用的是另一条打包命令，产物结构可能不同）。
- 根因：把"能跑"当成"能交付"，把"本地构建"当成"发布资产"；CI 触发条件（branches vs tags）与发版时机错位。
- 方案：
  1. 发布工作流**自带测试 job**（`needs:` 串起来），不依赖另一个 workflow 的触发条件；
  2. 产物按用户形态给：源码包（含预构建前端，免 Node）+ 免 Python 的 exe 包，各附 `sha256`；
  3. 打包前**清掉运行期数据** —— 在构建目录里跑过冒烟，`history.db` / 日志就会被打进 zip（脚本清理 + 打印清理清单）；
  4. 验收以**发布后下载的资产**为准：下载 → 解压 → 运行 → 查健康/页面/版本号；
  5. Release 正文写清"哪个包给谁、怎么用、什么依赖仍需另装"（如驱动级依赖）。
- 反模式：只发 Source code zip 当"发布"；在开发目录里直接 zip 上传；只验本地产物；把"还要装 Node/驱动"藏在 README 深处。
- 溯源：2026-09-21 flowwatch v1.0.1（`release.yml` 三个 job：tests → package → package-exe；两个资产 16.55 MB / 3.32 MB；线上资产实测 6 s 采集正常、`/api/meta` = 1.0.1）

### E-13 Windows 计划任务做"守护自愈"的正确配方（含两个必踩的坑）
- 场景：#Windows #运维 #常驻服务 #可靠性
- 问题：常驻守护脚本（内存守护/看门狗）要求"开机自启 + 自己死了能自动回来"，用 `Register-ScheduledTask` 配置时踩两坑：① `-RepetitionDuration ([TimeSpan]::MaxValue)` **注册直接报错**：`The task XML contains a value which is incorrectly formatted or out of range. (10,42):Duration:P99999999DT23H59M59S`；② 只配 `-AtLogOn` 触发器时 `NextRunTime` 为空（已登录状态下"下次登录"无法计算），"自愈到底有没有生效"不可观测。
- 根因：① 任务计划对 `RepetitionPattern.Duration` 有上限，不接受 MaxValue；② `AtLogOn` 是事件触发器，不产生"下一次运行时间"。
- 方案（可复制配方）：**双触发器 + 四个设置**
  1. 心跳触发器：`New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)`，**省略 `-RepetitionDuration`**（空 Duration = 无限重复）；配合 `-MultipleInstances IgnoreNew`：守护活着时心跳是 no-op，死后 ≤5 分钟自动拉起（实测：20:10:34 杀 → 20:15:19 触发 → 20:15:20 新进程出现）。
  2. 登录触发器：`-AtLogOn`（开机/登录自启）。
  3. 设置项：`-ExecutionTimeLimit ([TimeSpan]::Zero)`（永不超时终止）、`-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries`、`-RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)`。
  4. 注册后**必须校验**：`Get-ScheduledTask` 看 State；`Get-ScheduledTaskInfo` 看 `NextRunTime`（应为 5 分钟内滚动；`LastTaskResult 0x800710E0` = 心跳被 IgnoreNew 忽略，属正常值）。
- 附（PowerShell 健壮性）：给任务计划 `-File` 启动的脚本，**param 默认值里的 `$PSScriptRoot` 可能为空**（复杂调用/包装下实测出现过）→ 把路径默认值挪到函数体，用 `$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }` 兜底。
- 附（第三个坑 · 2026-09-23）：**不要给 `Register-ScheduledTask` 传 `-Principal`** —— 即便写成 `-LogonType Interactive -RunLevel Limited`，非提权会话也是直接 `Access is denied.`；省掉 `-Principal`（默认主体 = 注册者本人、仅登录时运行）即成功。想表达"登录自启"用 `-AtLogOn -User $env:USERNAME` 就够了。
- 反模式：只配 `-AtLogOn` 就宣称"配了自启"（运行期死掉无人管）；把注册失败当成功（`Register-ScheduledTask` 报错后脚本仍继续打印 success → 必须 `-ErrorAction Stop` + 注册后复查存在性）。
- 溯源：2026-09-22 memory-guard 计划任务（`frontend-works/tools/memory-guard/memory-guard.ps1`，任务名 MemoryGuard）

### E-14 SSH 交互式会话老掉线：客户端保活 + tmux（服务端 ClientAliveInterval=0 也不代表安全）
- 场景：#SSH #运维 #Linux #保活 #远程开发
- 问题：挂着 `ssh <host>` 做交互式操作（跑 pwd/ls 学 Linux），过一段时间会话就断，现场全丢；直觉以为是"服务端把我踢了"。
- 根因：客户端与服务端**都没开保活探测**时，空闲 TCP 连接会被**中间的 NAT / 防火墙 / ISP 连接跟踪**按空闲超时清掉。实测服务端 `sshd -T | grep clientalive` = `clientaliveinterval 0`（**从不探测、也不踢**）——锅在链路，不在 sshd。Windows 客户端睡眠或切换网络（Wi-Fi↔有线）同理。
- 方案：
  1. **客户端保活**（最小改动，写进 `~/.ssh/config` 对应主机块）：`ServerAliveInterval 30` + `ServerAliveCountMax 6`（容忍 ~3 分钟无响应才判死）+ `TCPKeepAlive yes`；临时用命令行等价写法 `-o ServerAliveInterval=30 -o ServerAliveCountMax=6`。
  2. **tmux 兜底**（真正解决"现场丢失"）：`tmux new -A -s learn`（不存在就建、存在就 attach）；断线重连后 `tmux a -t learn` 接着用，长命令/编辑器都不受影响。screen 同理。服务器上先 `which tmux screen` 确认。
  3. 只有在"链路单向空闲被清"的少数场景才需要服务端也发探测：`ClientAliveInterval 60` + `ClientAliveCountMax 3`；改之前先分清是谁掉（客户端报错文本：`Connection reset by peer` vs `Timeout, server not responding`）。
- 反模式：一掉线就去改服务端 `ClientAliveInterval`（服务端 0 = 不踢，改了治不了中间设备）；把耗时任务直接跑在裸 ssh 会话里（一断全丢）；只在命令行加保活参数、不进 config（下次又忘）。
- 溯源：2026-09-23 京东云服务器（`~/.ssh/config` 的 `Host jdcloud` 补保活三行；服务端已装 tmux/screen）

### E-15 官方安装器的“安装目录守卫”与程序自写目录冲突：自己拦自己的更新
- 场景：#Windows #桌面应用 #升级 #排障 #自检守卫
- 问题：升级 IDE 弹窗「无法安装必要的更新 — 检测到应用安装目录下存在用户项目目录」，指名安装目录里的一个 `.marscode\`。按提示删掉后**重开一次应用它又回来了**，更新再次被拦；看上去像"删不干净"。
- 根因：两件事撞在一起 ——
  1. **守卫是白名单制**：`readdirSync(安装目录, {withFileTypes:true}).filter(e => e.isDirectory() && !白名单)`，白名单 = `bin locales resources tools log logs crashpad gpucache _`（另放行 `$*` / `nsis*`）→ 安装目录下**任何"非白名单目录"都被判成用户项目**（注意：**只查目录、不查文件**）。
  2. **程序自己往里写**：该应用每次启动约 23 s 后会把 `deviceInfo.json` 写进 `<安装目录>\.marscode\`（同一 deviceId 反复生成）→ "官方守卫拦官方产物"，**每次启动必触发**。
  守卫只在检查入口短路（`doCheckForUpdates(){ if(!url || checkInstallDirGuard()) return; ... }`，守卫不过连检查请求都不发）；而 `handleRelaunch() → doQuitAndInstall()` **不含**守卫 → 只要过了检查阶段，下载/安装不会再被拦。
- 方案：
  1. **取证定责**：把"现象时间"与"产物时间戳"对齐 —— 目录 `CreationTime` 与进程 `StartTime` 相差 23 s、内容只有 `{"deviceId":…}`、`LastAccess` 恰是上次检查那一刻 ⇒ 判定为程序自写产物，不是用户工程（据此才敢动）。
  2. **过关姿势（顺序是关键）**：**不要重启应用**；在**当前已打开的窗口**里删掉该目录 → 立刻触发「检查更新」→ 下载完选「重启并安装」。（先重启的话目录会先被写回来，永远过不了。）
  3. 怕中途被回写就挂限时看守：每 3 s 检测一次，把回写目录**移出**到备份目录（而不是直接删，可回溯）；本次落地为 `C:\scripts\cb_update_unblock.ps1`（默认前台看守，`-Once` 只清一次，`-Restore` 可搬回）。
  4. 兜底：官网手动下载安装包覆盖安装，完全绕开应用内 updater。
- 反模式：把守卫报的路径当成"用户工程"去迁移（迁完还会回来）；反复重启应用重试；直接删而不留备份（万一是真记录就不可逆）；只看"弹窗还在"就判定"守卫还在拦"（要看日志里有没有新的 `blocked by ... guard` 行）。
- 溯源：2026-09-23/24 CodeBuddy CN 1.106.1 升级受阻（日志 `%APPDATA%\CodeBuddy CN\logs\*\main.log` 的 `update#checkForUpdates: blocked by install dir guard`；守卫代码 = `resources\app\out\main.js` 内 `installDirGuard.js` 段）



### E-16 发版卫生：版本号同步点先枚举，tag 首推失败可安全重建
- 场景：#发布 #GitHubActions #版本号
- 问题：① 打 tag 前只改了 README 徽章，漏掉代码里的对外版本常量（发布的包会报旧版本号）；② 某次 tag 推上去了，但打包 job 全 skipped（**零资产**），需要重发同一个版本。
- 根因：版本号在不同项目里散布位置不同 —— 本例只有两处（`server.py` 的 `VERSION`，经 `/api/meta` 暴露；README 徽章；**打包配置里没有**版本元数据），但"哪些地方要改"从来没人列过。
- 方案：① 发版前先 `git grep` 把版本串全找出来（排除 lock 文件）再动手，并在常量旁注释"发版时与 git tag 一起改"；② **零资产**的失败 tag 可安全删重建：`git tag -d <t>` → `git push <remote> :refs/tags/<t>` → 重新指向修复提交 → 重推（不要另起新版本号）；③ 查资产别看 `/releases/tags/<tag>`（该端点会把 `assets` 报成 0，是缓存坑），要查 `/releases/<id>/assets`，或直接按下载 URL 探测 302。
- 反模式：tag 推上去就当发完了；只改文档里的版本号；为"重发"而跳版本号。
- 溯源：flowwatch v1.0.2（2026-09-23）/ v1.0.3（2026-09-24）两次发版会话。

### E-17 交付验收的"采样时机"假红：等状态落定再判定
- 场景：#验收 #脚本 #假红
- 问题：验收脚本报「采集设备未打开 / degraded」，看着像产品坏了，其实**同一时刻 `packets` 已经在涨**。
- 根因：设备是**异步选定**的（自动挑网卡要逐张试抓，每张 1 秒）；脚本在服务一响应就采样，采到的是"还没挑完"的中间态。人肉采样同样会踩 —— 本轮在源码包 smoke 上又犯一次。
- 方案：① 断言"最终会成立的状态"时先轮询到落定（本例：`device` 非空或出现 error，上限 ~25 s）；② 用**第二个读数交叉验证**（`packets` 是否增长、`seconds_since_last_packet`）—— 元原则 11 的典型场景；③ 报告里写清"哪个读数是采样时机造成的假红"，别把它当结论。
- 反模式：拿启动瞬间的第一个 health 响应下结论；看到 degraded 就去改产品代码。
- 溯源：flowwatch `_deploy/_qa/exe_release_check.py` 修假红 + 源码包验收复发（2026-09-24）。

### E-18 长任务在"内存守护"边缘的跑法：按守护阈值设门禁 + 产物可续跑 + 压进程内存
- 场景：#环境 #Windows #内存 #渲染 #长任务
- 问题：渲染 1914 帧前可用内存只剩 **2.5 GB（7.8%）**，正卡在本机内存守护的阈值边缘（<12% 警告、<7% 连续 3 次采样即杀最大占用者）—— 按经验，长任务很可能中途"静默消失"（报错是空字符串）。
- 根因：守护按**可用内存百分比**决策，而渲染（浏览器/编码器）会稳定吃掉几百 MB 并持续几十分钟 → 长任务恰好落在它最想动手的区间；且它是"杀掉一个再看"，被杀的进程没有恢复机制。
- 方案（承接 E-09 的"先查内存"，补上跑法与工程化）：① 开工前读 `FreePhysicalMemory`，并**按守护的阈值**给自己设门禁（本机取 >2.5 GB 才启动）；② 让任务**可续跑**：产物按帧/分片落盘，重跑时跳过已存在的（`--resume`）—— 被杀了只损失当前一片，而不是从头再来；③ 压进程内存：浏览器加 `--disable-gpu --renderer-process-limit=1 --js-flags=--max-old-space-size=192`；④ 长任务**串行**跑，别并发压内存。实测：1914 帧一次跑完未被守护杀。
- 反模式：内存已到阈值边缘还直接开长任务；任务不可续跑（一被杀全白干）；把"进程静默消失、报错为空"当代码 bug 查。
- 溯源：2026-09-24 memfuse 宣传片逐帧渲染（`_deploy/memfuse-video/make_promo.py`），承接 E-09。

### E-19 发布资产在这台机器传不上去：把构建与挂载搬到 runner
- 场景：#发布 #GitHubActions #网络受限 #代理
- 问题：Release 建好了（tag、正文都在），但 **zip 资产传不上去**：`uploads.github.com` 连不上，`--resolve` 到候选 IP 全是失败形态（0 字节 / 404 / `Bad request · GitHub` HTML）；直接 POST `api.github.com/.../releases/<id>/assets` 也是 404；连取源码包的 `codeload.github.com` 都只回 14 字节。
- 根因：这台机器的 GitHub 通道是被 hosts/加速器**半接管**的，只覆盖 `github.com` + `api.github.com` 的**部分**服务 —— `uploads.github.com`、`codeload.github.com`、`objects.githubusercontent.com` 同样被钉到 `127.0.0.1`；而 DoH（`dns.google` / `1.1.1.1`）在本网络被丢包，**拿不到真实 IP**，`--resolve` 也就无从下手。
- 方案（把“打包 + 挂载”整个搬到 GitHub runner，本机只发一条 dispatch）：
  1. `.github/workflows/release.yml`：`on: push: tags: ['v*']` **+ `workflow_dispatch`（输入 `tag`）**，`permissions: contents: write`；
  2. job 内 `actions/checkout`（`ref` 取输入或 `GITHUB_REF_NAME`，`fetch-depth: 0`）→ `git archive --format=zip --prefix=<name>/ HEAD` → `gh release view <tag> || gh release create <tag> ...` → `gh release upload <tag> <zip> --clobber`；
  3. 本机触发：`POST https://api.github.com/repos/<o>/<r>/actions/workflows/release.yml/dispatches`，body `{"ref":"main","inputs":{"tag":"v1.0.0"}}`（走 `--resolve api.github.com:443:<ip>`），**204 即已排队**；再用 `/actions/runs` 的 `conclusion` 收尾；
  4. **`workflow_dispatch` 必须存在于默认分支**才能被派发 → workflow 放 `main`；老 tag 也能靠它补挂资产，不必删 tag 重建。
- 反模式：为发资产去改 hosts / 关掉加速器；用 `curl -k` 把 token 送进本地 MITM 代理；只闷头重试上传，没想到“换个网络（runner）就解决”。
- 溯源：memfuse v1.0.0 / v1.1.0 双发布（2026-09-24 ~ 09-26 会话；同族 E-16「查资产要查 `/releases/<id>/assets`」）

### E-20 Windows 交付物的“双击可用”：一个 .cmd 启动器 + 新机器两道闸
- 场景：#Windows #交付 #PowerShell #首次运行
- 问题：干净目录里放一个 `.ps1` 就能跑（零依赖、自动建 `logs\`、缺配置文件不报错），但**“裸运行”在新机器上必被拦**——实测两种原文：策略 `RemoteSigned` + 文件带 Mark-of-the-Web → `is not digitally signed. You cannot run this script on the current system.`；策略 `Restricted`（Windows 客户端出厂默认）→ `cannot be loaded because running scripts is disabled on this system.`（都 exit 1）。
- 根因：Windows 对“下载来的脚本”有**两道独立闸**——文件来源标记（`Zone.Identifier`）与执行策略；文档里写 `-ExecutionPolicy Bypass` 能过，但要求用户照着敲，于是“开箱即用”停在最后一步。
- 方案：交付一个纯 ASCII 的 `.cmd` 启动器，恒定带 Bypass：
  ```bat
  @echo off
  setlocal
  if "%~1"=="" goto usage
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0<tool>.ps1" %*
  endlocal
  exit /b %ERRORLEVEL%
  :usage
  echo <tool> - 常见用法...
  endlocal
  exit /b 0
  ```
  要点：① **无参数只打印用法**（双击不会误启动常驻/杀伤类工具）；② `-ExecutionPolicy Bypass` 一次绕过两道闸（连下载标记一起绕），**无需改机器全局策略**；③ 用 `goto label` 结构，**别在 `if (...)` 括号块里 echo 含 `(` 的文本** —— 未转义的 `(` 会让 cmd 报 `: was unexpected at this time`（exit 255）；④ `.cmd/.bat` 必须 **CRLF**（写完验 `bareLF == 0`），LF 行尾会破坏标签跳转；⑤ README 放一张“报错原文 ↔ 解法”对照表，用户搜得到。
- 反模式：只写“用 `-ExecutionPolicy Bypass` 跑”就当交付完成；让用户自己猜 `Unblock-File`；启动器“没参数就直接启动”。
- 溯源：memfuse `memfuse.cmd`（2026-09-24 会话；实测带 MOTW 的 `.ps1` 经启动器 exit 0）

### E-21 增量部署的两条硬规矩：先量代码差集、再让"验证通过才重启"

- 场景：#部署 #远程服务器 #systemd #验证门禁
- 问题：改完功能只推了 4 个"本次相关"文件到线上，**服务直接起不来** —— `web/api.py` 里 `from rag.query_rewrite import ...` 报 `ModuleNotFoundError`，systemd 退出码 1、服务宕。实查：线上代码是 **10 天前**的版本，本地这期间新增 54 个文件、改动 15 个。
- 根因：两条，各修一条：
  ① **代码分叉是静默的**——本地迭代时没有任何信号提醒"线上落后"，于是"推几个文件"隐含假设了两边同步；
  ② **把"上传"与"重启"做成了连续动作**——systemd 的语义是"**没重启之前服务一直跑旧代码**"，所以那次导入失败本不该影响线上，是这个顺序把**可避免的失败变成了宕机**。
- 方案：
  ① **动手前量差集**：全量 md5 三方对照（`只在本地有` / `内容不同` / **`只在线上有`**）。最后一项最危险——"整目录覆盖"式部署会**静默删掉线上独有文件**（本次实测有 2 个）。同步清单收敛到"**运行时**代码"，分析脚本等惰性文件不进运行链路。
  ② 部署流程加**导入门禁**，位置必须**在停服之后、启动之前**：
     ```
     本地预检（编译 + 前端语法）
       → 线上预检（服务状态 / 目标文件指纹）
       → 备份所有将被覆盖的文件
       → 上传
       → 停服
       → 门禁：python -c "from web.api import app"      ← 依赖缺失只有真正 import 才暴露
            ├─ 通过 → 启动
            └─ 失败 → 自动回滚 + 启动旧代码，中止
       → 启动后验证：健康检查 + 真实请求端到端 + 关键落库校验
     ```
     要点：**门禁必须能抓到 `py_compile` 抓不到的错误**（缺模块、循环导入）；**失败路径自动恢复**，使最坏情况是"没更新成功"而不是"服务挂了"。
- 反模式：用"整目录覆盖 + `rm -rf`"的首装脚本做增量更新（**首装脚本会连 `data/` 一起覆盖**，必须与增量脚本分开）；把 `py_compile` 当导入校验；上传完直接 `systemctl restart`。
- 溯源：vectordb-news 线上埋点部署（2026-09-28 事故与重写；工具 `_deploy/_qa/vdb_code_sync_audit.py` + `deploy_vdb_telemetry.py`）

### E-22 第三方嵌入"代码里配了"≠线上可用：缺 env 时渲染 undefined 坏区块
- 场景：#部署 #环境配置 #第三方嵌入 #验收
- 问题：文章页底部评论区线上空白。代码里 `provider: 'giscus'` 明明配着；实查线上 DOM：giscus iframe 的 repo 参数是字面 `undefined`，控制台报 "giscus is not installed on this repository"。构建、部署、页面 200 全都"成功"。
- 根因：giscus 的 4 个身份值（repo / repositoryId / category / categoryId）走 `NEXT_PUBLIC_GISCUS_*` **构建期环境变量**，CI 里从未配置；组件不做空值守卫，把 `undefined` 原样拼进 iframe src → 坏区块不报错、不崩，只在运行时静默降级成"什么都看不到"。
- 方案：① 上线验收必须覆盖"依赖 env 的第三方件"——不看构建绿不绿，直接在**线上页面**查 DOM（iframe src / 容器节点）与 console；② 不用的功能显式下线 + 留恢复说明（`comments: undefined`，注释写明恢复路径：到 giscus.app 生成 4 个值 → 配 CI env → 改回 provider），比留一块坏 iframe 好。
- 反模式：把"站点能构建 + 页面 200"当作上线完成；对 `undefined` 环境变量无守卫地拼进第三方组件；本地与 CI 是两套 env 却按一套心态验收。
- 溯源：TechLog 文章页改版（2026-09-28，`data/siteMetadata.js` 注释 + 线上 console / DOM 复核）

### E-23 前端构建被环境变量静默改写 API 基址：页面"全空白 + 连接中断"
- 场景：#部署 #前端 #Vite #环境配置
- 问题：本地预览页（静态服务器端口）某天整页「连接中断」：SSE 断、历史/排行全空、顶部数字停在断流前最后一帧。后端 API 正常、CORS 正常、dist 也是"新鲜构建"的——三个直觉全指向"不可能是前端"。
- 根因：构建 dist 时 shell 里残留 `VITE_API_BASE=/`（演示包/CI 的"同源部署"口径）→ 源码 `RAW_BASE.replace(/\/+$/,'')` 把 `/` 处理成**空字符串** → 前端所有请求打向静态服务器自己（无 /api）→ 全 404。构建"成功"、产物"看起来正常"，只是 API 基址被静默改写。
- 方案：**构建后自查打包产物**：`dist/assets/*.js` 里应含预期 API 主机（如 `127.0.0.1:8788`）；构建前确认环境无该变量（`.env*` 文件与持久环境变量两处都查）。修复 = 停预览服务（释放 dist 文件锁）→ 干净环境重建 → 重启服务。**诊断口诀：页面全空先查 dist 里的 API 基址**。
- 反模式：看到"连接中断"就查后端/CORS（本次三者全正常）；相信"dist 是刚构建的所以没问题"——新构建 ≠ 对口径。
- 溯源：flowwatch 4173 页面空白事故（2026-09-25 会话）

### E-24 手动起的常驻服务不落输出：崩溃后死因不可考
- 场景：#运维 #Windows #常驻服务 #可靠性
- 问题：长期运行的服务进程某刻静默消失（端口无监听、进程无、任何日志都没有）；连"什么时候死的"都只能靠外部观察（浏览器断流）反推。
- 根因：进程是手动 `Start-Process` 起的，未做任何输出重定向 → stdout/stderr 丢失，崩溃信息（异常栈）随进程一起消失；而"整机是否重启过"还得另找证据（如 explorer 进程启动时间）才能排除。
- 方案：常驻服务启动时**输出落盘**——用 `cmd /c "python server.py ... >> _run\server.out.log 2>&1"` 包装（比 `Start-Process -RedirectStandardOutput` 省事且没它的已知不便）；重启操作顺手记"起于何时/因何重启"。
- 反模式：手动起长驻服务图省事不给日志；出事后凭印象猜"是不是重启过了"。
- 溯源：flowwatch 8788 静默死亡（2026-09-30 会话）

### E-25 内存守护会杀掉 `next build`：用 protect-list.txt 热加载白名单临时豁免（构建/编译类长任务的完整跑法）
- 场景：#环境 #Windows #内存 #长任务 #构建 #Node
- 问题：`next build` 在 webpack 阶段**静默消失**：日志停在 "Creating an optimized production build"，无 error、无栈、无 exit code；node 进程不见了，系统可用内存回升；重跑仍复现。
- 根因：本机内存守护（现位于 `Documents/trae_projects/memfuse/memory-guard.ps1`，ScheduledTask「MemoryGuard」每 5s 采样）在可用内存 <7% 持续 15s（<3.5% 立即）时杀掉**工作集最大且未被保护**的进程；`node` 不在保护名单 → 构建正好是最大目标。
- 方案：
  1. **先看守护自己的证据**（应用日志里什么都没有）：日志在 `memfuse/logs/memory-guard-<守护启动日>.log`（文件名按守护启动日、不是当天，别被日期骗）；桌面 `memory-guard-alert.txt` 每次击杀都写 `killed: node (pid …, …MB) cmd: …`；
  2. **白名单热加载**：把 `node` 等临时写进 `protect-list.txt`（守护每 tick 检查该文件 mtime，**免重启生效**；也可 `-AddProtect node`，会自动备份 .bak）；把可能被"顺位下一个"选中、且持有用户窗口的应用（聊天/浏览器）一并保护，否则守护会继续找下一个 ≥300MB 的目标；
  3. 压峰值：`NODE_OPTIONS=--max-old-space-size=1536`（本次实测构建全程通过）；
  4. **构建完立刻恢复白名单**——临时豁免，不做永久降低守护能力的改动。
- 反模式：把"构建静默消失"当 Webpack/Node 的 bug 查；永久保护 node（等于让守护在最需要动手时无目标可杀）；只保护 node 不管"顺位下一个"（会误伤用户应用）。
- 溯源：2026-10-03 TechLog 本地构建（两次被守护杀，21:06:50 killed node pid 67144 1177MB，桌面 alert 文件实证；同族 E-09 / E-18）

### E-26 Android APK 发版前必查 `launchable-activity`：安装成功 ≠ 有桌面入口，目检 Manifest 常量不可信
- 场景：#发布 #Android #打包 #验收
- 问题：APK 安装成功，但桌面/应用抽屉没有图标（"设置 → 应用"列表里却能看到它）；`aapt dump badging` 输出中**没有 `launchable-activity:` 行**。
- 根因：launcher intent-filter 的 category 常量拼错（`android.intent.action.LAUNCHER`，应为 `android.intent.category.LAUNCHER`，即 `action.` 误代 `category.`）。PackageManager 按标准常量做精确匹配，匹配不到就不把应用注册为桌面入口——**应用本体安装完全正常**，现象极具迷惑性。更隐蔽的是**宽容型渲染工具会掩盖错误**：`aapt2 dump xmltree` 与文本编辑器（含 AI 的 Read）都把错误值"校正显示"成 `category.LAUNCHER`，肉眼目检必然漏诊——「打印出来正确」≠「字节正确」≠「系统语义正确」。
- 方案（发版闸门，按成本递增）：
  1. **静态闸门**：`aapt dump badging app.apk` 必须有 `launchable-activity: name='<pkg>/.MainActivity' …`；等价的第三方仲裁：pyaxmlparser `APK(f).get_main_activity()` 非 None。注意要用**按标准常量做匹配**的工具（badging），而非只做渲染的 xmltree；
  2. **字节仲裁**：怀疑常量被写错时，解开 APK 的 AndroidManifest.xml，在原始字节里搜字符串池（AXML 字符串是 UTF-16LE，如 `'category.LAUNCHER'.encode('utf-16-le')`），不信任何渲染/解码层的显示；
  3. **设备闭环**：有模拟器/真机时 `adb install` → `adb shell "cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.LAUNCHER | grep <pkg>"` 必须命中，再截图应用抽屉；用"旧包先装复现、覆盖新包转好"形成根因闭环（同签名 debug 包可直接覆盖）；
  4. **对照组排错**：工具输出可疑时，拿一个已知正常的 APK 跑同一条命令——aapt 35 的 badging 会输出一行孤立的 `main`，是工具固有行为、与故障无关。
- 反模式：构建成功 + 能安装 + 验过签名/包信息就发版（安装成功不代表存在可启动入口）；用 xmltree/编辑器目检 intent action/category 常量；遇到异常输出先怪工具版本而不做对照。
- 溯源：2026-10-14 TechLog 薄壳 APK v1.0 桌面无图标事故（修复版 v1.0.1 / versionCode 2，提交 a3911f1；线上 SHA256 与本地一致）；usercontext/2026-10-14.md「TechLog 1.0 桌面无图标事故 → 1.0.1」。**再次验证元原则 11**（宽容型工具的"假正确"读数，必须换严格匹配型工具二次确认）与**元原则 13**（构建/安装通过 ≠ 交付物可用，发版闸门要打在系统真实识别的入口契约上）。
