# Extraction Cursor（提取游标）

> 记录上次处理到哪篇日记，避免重复调用模型。
> **损坏或为空时，`sleep_purify.py` 会报错退出**（防止一次性全量调用）。

```yaml
last_processed: null
last_daily: null
status: pending
```

---

首次运行前，可以：
- 让 `sleep_purify.py --force` 强制全量（慎用，会逐篇调模型），或
- 手动把 `last_daily` 设成你想从哪篇之后开始处理的日期
