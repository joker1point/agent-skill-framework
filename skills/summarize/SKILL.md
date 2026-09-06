---
name: summarize
description: 文本摘要工具，用于总结文章、网页内容
tags: nlp, summary, text
always: false
---

# 文本摘要技能

使用Python进行文本摘要处理。

## 使用方法

### 提取关键词
```python
import jieba.analyse

text = "这是一段需要提取关键词的文本..."
keywords = jieba.analyse.extract_tags(text, topK=10)
```

### 简单摘要
```python
from collections import Counter

def simple_summary(text, max_sentences=3):
    sentences = text.split('。')
    return '。'.join(sentences[:max_sentences]) + '。'
```

### 网页摘要
```bash
# 使用curl获取网页内容
curl -s https://example.com | grep -o '<title>[^<]*</title>'
```

## 提示
- 长文本可以先提取关键词再生成摘要
- 使用正则表达式清理HTML标签
- 可以结合web_fetch工具获取网页内容后再处理