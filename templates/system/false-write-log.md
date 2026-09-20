# False Write Log（被拒条目日志）

> review 模式下，置信度低于阈值或被安全拦截的 Claim 会记在这里，便于复盘阈值是否合理。

## 格式说明

每条形如：`时间 | subject.predicate | source | confidence | kind | 拒绝原因`

## 记录

