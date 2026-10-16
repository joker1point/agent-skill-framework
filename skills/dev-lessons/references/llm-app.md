# LLM 应用开发踩坑

场景标签：`#LLM` `#Prompt工程` `#AIGC生图` `#异步生成`

## 条目索引（按编号或关键词检索：**先用 search_content 搜编号 / 关键词，勿整读本文件**）

| 编号 | 标题 | 场景标签 |
|---|---|---|
| L-01 | 结构化锚点：LLM 稳定遵循的属性必须进 DB 列 | #AIGC生图 #DB设计 #Prompt工程 |
| L-02 | 输出多样性双层修复：fallback 和主路径都要查 | #LLM #Prompt工程 |
| L-03 | prompt 上下文注入：生成必须看到历史 | #LLM #Prompt工程 |
| L-04 | 复杂度分级 + 决策选项 LLM-first | #LLM #产品设计 |
| L-05 | 超时预算：复杂 prompt 的 read timeout 要放大 | #LLM #异步生成 #运维 |
| L-06 | 历史 fallback 数据救援 | #LLM #数据修复 #运维 |
| L-07 | 字段级 fallback：部分缺失只补缺失 | #LLM #数据结构 |
| L-08 | AI 生视频做不了"精确运动编排 + 形象保持"，直接程序化兜底 | #AIGC生视频 #素材生成 #程序化渲染 |
| L-09 | 豆包生成视频的去水印正路：vid 溯源走 aispace API，别硬抠画面 | #AIGC生视频 #豆包 #水印 #合规 |
| L-10 | 提示词不声明输出 schema，模型只填它"看见"的那一个字段 | #LLM #prompt #结构化输出 |
| L-11 | 长输出撞网关 524：拆阶段，客户端 timeout 无效 | #LLM #网关 #超时 |
| L-12 | 模型字段类型会漂移：渲染前必须统一 normalize | #LLM #数据校验 #渲染 |
| L-13 | 图生视频"锁不锁首帧"由协议决定：选错协议 = 场景漂移 + 幻觉字幕 | #AIGC生视频 #API协议 #素材生成 |
| L-14 | TTS 偶发"长尾伪影"：不是静音，裁剪会误伤，得用时长合理性 + ASR 内容闸门 | #AIGC配音 #TTS #质检 #重试 |
| L-15 | AIGC 音色"像不像角色"只能人耳验收：候选制 + 两阶段交付 | #AIGC配音 #音色 #验收 #人机分工 |

### L-01 结构化锚点：LLM 稳定遵循的属性必须进 DB 列
- 场景：#AIGC生图 #DB设计 #Prompt工程
- 问题：角色年龄放在自由文本字段，生图时 LLM "自由发挥"年龄段，角色一致性被破坏。
- 根因：`age` 未结构化、未进 prompt 优先级表（`KEYS_PRIORITY`），LLM 输出不稳定。
- 方案：`Character.age` 增加 `Integer` 列 + 迁移；prompt 注入时 `char.age → "X-year-old ..."`；加入 `KEYS_PRIORITY` 保证优先级。双 fallback：结构化 `char.age` 最高 → LLM appearance 字符串次之 → 缺失优雅降级。
- 反模式：手动触发生图的路径直接**替换**完整 prompt，导致注入的 age 描述被冲掉——手动路径必须**拼接**而非替换。
- 溯源：CharacterSeed/docs/dev_lessons/2026-07-03_age_consistency_anchor.md

### L-02 输出多样性双层修复：fallback 和主路径都要查
- 场景：#LLM #Prompt工程
- 问题："一键推演永远是这三条"——用户看到的永远是同样内容。
- 根因：两层病因。第一层：LLM 失败 fallback 硬编码了固定 3 条事件；第二层：LLM 主路径 prompt 无节奏约束，输出固定的"起床/任务/反思"模式。
- 方案：
  1. fallback 层：建 6 主题 fallback 池随机抽取，注入角色名/day 等上下文；解析函数与 fallback 职责拆分（解析函数拿不到上下文就抽不出 fallback）。
  2. 主路径层：prompt 加 5 种 few-shot 节奏示例，约束"随机选择一种 + 根据人设具体化 + 时段主题不重复"。
- 反模式：只修 fallback 就收工；把 fallback 逻辑塞进无上下文的解析函数。
- 溯源：2026-07-03_event_fallback_diversity.md、2026-07-03_llm_schedule_diversity.md

### L-03 prompt 上下文注入：生成必须看到历史
- 场景：#LLM #Prompt工程
- 问题：事件生成主题重复、叙事不连贯。
- 根因：`fill_pool` 的 prompt 缺少历史 completed 事件、记忆、当前场景上下文。
- 方案：注入 `recent_completed`、`recent_memories`；加 per-character LRU `_FALLBACK_THEME_HISTORY` 避免 fallback 撞主题。
- 反模式：让 LLM 在真空里生成序列内容。
- 溯源：2026-07-06_stage_summary.md

### L-04 复杂度分级 + 决策选项 LLM-first
- 场景：#LLM #产品设计
- 问题：事件推进"永远三件事"、决策选项（brave/cautious/defer）与事件内容脱钩、复杂事件生成质量撞墙。
- 根因：无复杂度分级，所有请求用同一套参数；决策选项硬编码。
- 方案：`_COMPLEXITY_TIERS` 三级配置差异化 `temperature/timeout/max_tokens/impact`；复杂度分类器用关键词优先级避免误分类；决策选项改为 LLM 按事件内容生成 + 字段校验。
- 配套：`_cumulative_impact_clamp` 防数值无限膨胀；memory 写入设门槛防长期记忆噪声。
- 溯源：2026-07-06_event_complexity_and_decision_llm_first.md

### L-05 超时预算：复杂 prompt 的 read timeout 要放大
- 场景：#LLM #异步生成 #运维
- 问题：复杂事件 enrich 后只显示 21 字降级文案，无任何报错。
- 根因：`httpx` read timeout=30s；复杂事件 prompt 大且 `max_tokens=2000`，LLM 实际响应 25-50s，超时静默走 fallback。**症状是输出变短变烂，不是报错**。
- 方案：`httpx.Timeout.read` 30s → 60s。注意：类级缓存的 timeout 修改必须**重启后端进程**才生效。
- 溯源：2026-07-07_complex_event_enrich_timeout.md

### L-06 历史 fallback 数据救援
- 场景：#LLM #数据修复 #运维
- 问题：修好 timeout 后，历史已落库的降级数据不会自动重跑，用户仍看到短文本。
- 根因：fallback 结果已写 DB，属于既成事实，代码修复不追溯。
- 方案：批量救援脚本扫描特征值（如 `result_json LIKE '%LLM 降级%'`），重置为 `pending_enrich` 再调 `enrich_event_result` 重跑。
- 通用规律：凡是"静默降级"写库的流程，都要配一个可重跑的救援通道。
- 溯源：2026-07-07_complex_event_enrich_timeout.md

### L-07 字段级 fallback：部分缺失只补缺失
- 场景：#LLM #数据结构
- 问题：LLM 返回的结构化卡片缺个别字段时，整体替换成兜底内容，浪费了正常的部分。
- 根因：fallback 粒度是整条记录而非字段。
- 方案：字段级 fallback——逐字段校验，缺失字段才用默认值补，正常字段保留。
- 溯源：2026-07-05_event_struct_card_plan_a.md

### L-08 AI 生视频做不了"精确运动编排 + 形象保持"，直接程序化兜底
- 场景：#AIGC生视频 #素材生成 #程序化渲染
- 问题：需要"眼珠沿眼眶顺时针匀速转一圈、首尾闭环、形象与现有角色一致"的素材。文生视频：实际轨迹"中→左→右→中"，非圆周；图生视频（换提示词+首帧）：角色被再创作（白壳→纯黑头、身体消失、背景变色），且轨迹 上→左→下→上 全程缺一个方位。多次重试均不可控。
- 根因：视频模型对逐帧运动编排和首帧形象还原都没有可靠的服从机制；提示词描述不了精确的帧级约束。
- 方案：只把 AI 生成用于"氛围/风格"类、不要求精确对齐的素材；凡是**几何可定义**的动画（贴边转圈、匀速圆周、方向映射），用程序化渲染兜底——程序检测关键部位（如连通域 + 对称成对约束定位眼眶）+ 公式逐帧绘制 + 拼图集，角度-帧号严格线性，首尾天然闭环。
- 反模式：反复调提示词重试视频生成碰运气；把"重新生成"当修复手段。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Dify-Avatar-Gaze-Session-Summary.md

### L-09 豆包生成视频的去水印正路：vid 溯源走 aispace API，别硬抠画面
- 场景：#AIGC生视频 #豆包 #水印 #合规
- 问题：豆包生成并下载的 mp4 右下角带「豆包AI生成」水印（且是动态的：淡入淡出+运动模糊），要用在正式页面里。
- 根因：水印烧在画面里，但豆包服务端始终留有无水印原片；下载件元数据里带 `comment: vid:<id>` 可作溯源钥匙。
- 方案：登录态下（浏览器扩展 doubao-downloader 同款，或 Tabbit 复用用户登录态在 doubao.com 页面上下文 fetch）三步拿 `main_url`：`/samantha/aispace/homepage`（找「我的创作」id）→ `node_info`（按 key=vid 找节点）→ `get_download_info`（取 `download_infos[0].main_url` CDN 直链）。原片分辨率/码率高于下载件（如 1112x834@11.5Mbps vs 960x720@1Mbps），重编码压回预算；**必须写回 AIGC 合规标签与 vid comment**（`-movflags use_metadata_tags`，见 misc M-05）。未登录报 `code:710012001 login invalid`。
- 反模式：ffmpeg delogo 硬抠动态水印（动画区插值痕迹明显）；删掉 AIGC 元数据（丢合规）。
- 溯源：frontend-works/vectordb-news/usercontext/2026-09-11/Doubao-Watermark-Session-Summary.md（commit 8396382）
- 注：豆包改接口导致本卡片失效时，按 misc.md M-08 三步法远程读上游 `src/api/video.ts` 的最新实现同步更新，勿 clone 勿 fork。
- **图片补充（已实测 2026-09-12）**：图片与视频不同路——`get_download_info` 对图片节点（node_type=4）返回的 main_url 模板是 `image_dld_watermark_1_5b`（**反而带水印**），创作空间缩略图是 `downsize_watermark`，对话页 DOM 预览是 `cpreview_wm1`（含"AI生成"角标）。唯一无水印源是对话页 SSR 内嵌 JSON 里的 `creation.image.image_ori_raw.url`（模板 `image_raw`，全尺寸原片）。取法：Tabbit 打开对话页 `doubao.com/chat/<conversation_id>`（conversation_id 可从 node_info 的 children[].content 拿），对 `document.documentElement.innerHTML` 正则提取 `"image_ori_raw":\{.{0,500}?"url":"(https:[^"]+)"`（HTML 里 `/` 转义成 `\u002F` 需还原），签名 x-expires 约 1 天有效，curl 直接下。上游扩展的机制是 MAIN-world hook 对话响应收集同一字段。

### L-10 提示词不声明输出 schema，模型只填它"看见"的那一个字段
- 场景：#LLM #prompt #结构化输出
- 问题：schema 有 9 个分析字段，实际返回里 8 个是 null，只有提示词里被点名的那一个字段有值。下游连带崩两处：评分 6 个维度只剩 2 个有效（分数被压在 57 分天花板），聚类从 90 条裂成 85 类。
- 根因：system prompt 只写了"返回一个 JSON object"，没给字段清单和类型，模型自由发挥——只填提示词中唯一被提及的字段名，其余字段名它根本不知道。
- 方案：system prompt 里显式给出**完整 JSON 形状**（字段名 + 类型 + 一句话说明 + 示例值），并加硬规则：不得省略字段、不得返回 null；分类类字段（emotion / structure / angle）必须是**受控短标签**——给枚举词表、限 ≤8 词，禁止整句或段落。补全后同一批数据：字段填充 89/90、成功率 88→90、Top1 分数 57→71.3。
- 通用规律：凡后续要按某字段做**分组、打分、筛选**的，该字段必须在提示词里被枚举约束——自由文本字段等于没有该字段。
- 反模式：只写"返回 JSON，字段含义见文档"（文档模型读不到）；把长句塞进本该枚举的字段当作"信息更丰富"。
- 溯源：2026-09-11 AI-driven-viral-content-analysis-system（90 条抖音内容分析）

### L-11 长输出撞网关 524：拆阶段，客户端 timeout 无效
- 场景：#LLM #网关 #超时
- 问题：让模型按 2000 字模板一次性输出完整脚本，请求稳定失败（HTTP 524，Cloudflare 超时）；把客户端 read timeout 从 120s 提到 420s 完全没用。
- 根因：524 是**网关等待源站**的超时，发生在服务端，与客户端愿意等多久无关；单次生成越长越容易越过这条看不见的线。
- 方案：把长产出拆成 4 个独立小阶段（元信息+钩子 / 口播+字幕 / 分镜 / 发布配套），每阶段输出控制在 500–800 字，上一步结果作为下一步输入；每阶段独立重试，失败只损失片段而非整条。分阶段后 20 条批量零 524。
- 反模式：调大客户端 timeout 期待绕过 524；把"输出太长"误判成"服务不稳定"。
- 溯源：2026-09-11 AI-driven-viral-content-analysis-system（短视频脚本批量生成）

### L-12 模型字段类型会漂移：渲染前必须统一 normalize
- 场景：#LLM #数据校验 #渲染
- 问题：同一字段在不同条目上类型不一致——`followup` 有时是对象数组、有时是字符串数组（渲染直接 AttributeError 崩溃）；`hashtags` 有时是数组、有时是整串空格分隔文本；口播时间戳有时与句子同行、有时独占一行；`publish_time` 把 Python/JSON 字面量 `[{'reason':...,'time':...}]` 原样印进成品。
- 根因：JSON 只约束"合法"，不约束"结构稳定"；模型对同一字段的形态没有一致性保证。
- 方案：在"模型返回"与"渲染/落库"之间加一层 normalize：`as_lines`（按行拆）、`as_tags`（空格/逗号拆）、`as_rows`（字符串升级为单列对象）、`as_text`（结构化字面量转人话）。渲染层只消费 normalize 后的形状。20 条里 13 条命中此问题。
- 反模式：直接 `x.get("k")` 假设类型；用 try/except 吞掉类型错误（数据静默丢失）。
- 溯源：2026-09-11 AI-driven-viral-content-analysis-system（批量脚本生成，20 条中 13 条触发）

### L-13 图生视频"锁不锁首帧"由协议决定：选错协议 = 场景漂移 + 幻觉字幕
- 场景：#AIGC生视频 #API协议 #素材生成
- 问题：拿定角图喂图生视频接口出三段短片，画面**整段漂移**（同机位的办公室变成了书房/森林）、角色被重绘成另一只熊，其中一段还**幻觉出了英文台词字幕**；换成同平台 2.5 系列的 keyframe 模式，同一张图就锁得严丝合缝（陈设、光位、角色都对得上）。
- 根因：同一家的不同模型族对"输入图"的语义不同——旧接口的 `image_url` 只当**宽松参考**，2.5 系列的 `mode:"keyframe"` 才是首帧强约束，且字段名不同（`first_frame`；传 `image_url` 直接 400 `not an allowed request field`，传 `images` 数组报 `keyframe mode requires first_frame and/or last_frame`）。
- 方案：需要"形象/场景保持"时**先问该模型族的输入语义与字段名，再选协议**；客户端把两套协议都固化（本项目 `gen.py video --mode keyframe --image-url <首帧URL> --size 720P`，请求体 `{model, mode, prompt, first_frame, size, seconds}`，轮询端点与旧协议相同）。另证 **L-08**：最终成片仍由 ffmpeg 程序化合成，AI 只出素材。
- 反模式：把"模型支持 image-to-video"等同于"会保留首帧"；拿宽松参考模式的产物直接交付（本次三段全废）。
- 溯源：2026-09-29/30 bear-boss（`bear-boss/productions/bear-boss/SERVICES.md` §1.2 / §1.2b、`drafts/shotA_v1..v3`）

### L-14 TTS 偶发"长尾伪影"：不是静音，裁剪会误伤，得用时长合理性 + ASR 内容闸门
- 场景：#AIGC配音 #TTS #质检 #重试
- 问题：7 个字的句子被生成成 **12 s**（另一段 16 s）：本地 ASR 只在前段识别出那句台词，之后是一段**持续长音**（频谱呈谐波堆叠）；`silencedetect=noise=-45dB` 一个静音区间都找不到，按静音裁剪会把真实台词一起切掉（"我不客气"位于低电平段，被切成"再托别怪"）。
- 根因：伪影是"有音量的持续音"，任何基于静音/电平的中段裁剪都会误伤；台词本体、伪影之间不一定有可判定的静音。
- 方案：① 主判据用**时长合理性**——上限 ≈ 字数 × 0.42 s ÷ 语速 + 1.0 s，超限即判废重生成；② 第二道闸门用**本地 ASR 比对文本**：目标字命中率 ≥ 60%、且**多出的字数 ≤ 3**（挡"马上马上马上"式加词）、关键目标字不得缺失；③ 两条都过才收，否则最多重试 4 次、保留内容命中最高的一条；④ 只做**尾部收口**（最后一个有效帧 + 0.15 s），绝不按静音切中段。
- 反模式：用 `silencedetect` 判伪影；把"静音裁剪"当 TTS 产物的常规后处理；一次生成即入库。
- 溯源：2026-09-30 bear-boss `tools/dub.py`（加闸门前，12 s / 16 s 废片已进过一版配音）

### L-15 AIGC 音色"像不像角色"只能人耳验收：候选制 + 两阶段交付
- 场景：#AIGC配音 #音色 #验收 #人机分工
- 问题：同一 voice_id 反复生成，**自动指标全绿**（ASR 命中率 100%、时长合理、无伪影）的若干句，用户听完全部否掉；他只认可其中某一次 take。我"按指标筛最优"的那条，在他听来"不像熊二"。
- 根因：音色相似度是**感知量**，ASR/时长/基频都替代不了听感；同一音色的多次采样质量分布很宽（本次还踩到平台未文档化的 `speed` 参数会改变音色，见 SERVICES.md）。
- 方案：**候选制 + 两阶段交付**——① 每句生成 N 条候选（本项目：`dub.py --audition N --lines 1,2,3,7`，自动剔除伪影/加词候选后再凑够 N 条）；② 交用户试听，按"句号-编号"点单（收到的是 `1-2，2-3，3-2，7-2`）；③ **选定后才合成画面**。音色/情感类验收以人耳为准，自动指标只承担"废片剔除"。
- 反模式：用 ASR 命中率/时长当"音色合格"判据并直接合成交付；每句只生成一条 take。
- 溯源：2026-09-30 ~ 10-01 bear-boss（用户原话"先生成语音让我检查完再生成视频"、"这个熊二比较像其他都不像"）
