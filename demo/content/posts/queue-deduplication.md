Title: 当任务被投递两次：队列消费的幂等设计
Slug: queue-deduplication
Date: 2026-11-24T09:30:00+08:00
Summary: 从一次重复投递出发，梳理幂等键、事务边界，以及任务超时后什么时候可以安全重试。
Tags: engineering, distributed-systems
Source: example-engineering
Source_url: https://example.org/engineering/queue-deduplication
Source_title: When a job is delivered twice
Source_author: Demo Editorial Team
Source_date: 2026-11-21
Kind: guide

一个队列任务可能在业务写入完成后、确认消息之前超时。消费者再次收到消息时，需要能判断原操作的结果，避免重复写入。

## 用业务操作确定幂等键

让生产者为同一次业务操作提供稳定的键。例如，用订单号和操作名称标识一次状态更新。消费者在一个事务中记录该键并应用变更。若发现相同的键已经完成，确认消息即可。

```python
with database.transaction():
    if operations.reserve(operation_id):
        orders.mark_paid(order_id)
```

## 重试的边界

| 失败位置 | 恢复方式 |
| --- | --- |
| 事务提交前 | 回滚并重新处理 |
| 事务提交后、消息确认前 | 查询操作记录，确认重复消息 |
| 调用外部系统后丢失响应 | 查询外部操作状态或使用对方支持的幂等键 |

本地事务只能覆盖同一个数据库内的更新。涉及第三方支付或邮件时，应为外部操作单独保留可追踪的标识。
