# 数据库与迁移踩坑

场景标签：`#DB` `#迁移` `#SQLite`

## 条目索引（按编号或关键词检索：**先用 search_content 搜编号 / 关键词，勿整读本文件**）

| 编号 | 标题 | 场景标签 |
|---|---|---|
| D-01 | SQLite 生产配置与幂等迁移 | #SQLite #迁移 |
| D-02 | 半截路检查：数据流四层贯穿 | #后端 #功能设计 |
| D-03 | 历史脏数据清理要配套 | #DB #数据修复 |

### D-01 SQLite 生产配置与幂等迁移
- 场景：#SQLite #迁移
- 问题：迁移兼容性差、新增字段重复执行报错。
- 方案：SQLite 上线三件套——
  ```sql
  PRAGMA journal_mode=WAL;      -- 读写不互斥
  PRAGMA synchronous=NORMAL;    -- 性能与安全平衡
  ```
  `ALTER TABLE` 前先查 `PRAGMA table_info` 判断列是否存在，不存在才加（幂等）；迁移脚本可重跑。
- 溯源：frontend/项目开发总结.md、2026-07-03_age_consistency_anchor.md

### D-02 半截路检查：数据流四层贯穿
- 场景：#后端 #功能设计
- 问题：SceneChange 因果链只写了 crud 层，模型、迁移、API、调用方全缺——功能"看起来有"实际不可用。
- 根因：新数据流没有走完 model → migration → API → caller 四层。
- 方案：新表/新字段用四层清单验收；关联实体（如 `Location`）外键设计前置；写入处用 try/except 容错包裹，不让辅助数据流炸主流程。
- 溯源：2026-07-03_scene_change_and_chapter_view.md

### D-03 历史脏数据清理要配套
- 场景：#DB #数据修复
- 问题：修好写入端（如 title 清洗）后，历史脏数据（乱码、fallback 残留）仍在库里。
- 方案：任何清洗/降级逻辑的修复，都要配一个历史数据清理脚本（按特征值扫描 + 批量修复）；见 L-06 救援通道。
- 溯源：luyan/docs/2026-06-28-开发经验总结.md、2026-07-07_complex_event_enrich_timeout.md
