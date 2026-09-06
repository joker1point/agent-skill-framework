---
name: weather
description: 获取当前天气和天气预报（无需API密钥）
tags: weather, forecast
always: false
---

# 天气查询技能

使用免费服务查询天气，无需API密钥。

## wttr.in（主服务）

快速查询：
```bash
curl -s "wttr.in/London?format=3"
# 输出: London: ⛅️ +8°C
```

详细格式：
```bash
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
# 输出: London: ⛅️ +8°C 71% ↙5km/h
```

完整预报：
```bash
curl -s "wttr.in/London?T"
```

格式代码：`%c` 天气状况 · `%t` 温度 · `%h` 湿度 · `%w` 风速 · `%l` 位置

提示：
- 空格用 `+` 编码：`wttr.in/New+York`
- 使用 `?m` (公制) 或 `?u` (英制)
- 只查今天：`?1` · 只查当前：`?0`

## Open-Meteo（备用，JSON格式）

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

文档：https://open-meteo.com/en/docs