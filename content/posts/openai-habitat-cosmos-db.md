Title: ChatGPT 的在线存储怎样隔离分区热点
Slug: openai-habitat-cosmos-db
Date: 2026-11-24T17:22:45+08:00
Summary: 从 Cosmos DB 的逻辑键和物理分区入手，看共享存储如何应对热点、后台任务和租户迁移。
Tags: databases, distributed-systems, infrastructure
Source: openai-engineering
Source_url: https://openai.com/index/scaling-storage-one-billion-users-part-two
Source_title: Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)
Kind: guide
Source_date: 2026-10-23
Source_author: Jon Lee, Hrachya Hakobyan, Chaomin Yu

ChatGPT 的不同功能会共享在线存储平台 Habitat。共享资源便于利用闲置容量，但一个流量突然上涨的功能也可能拖慢登录等关键请求。OpenAI 的这篇复盘围绕 Azure Cosmos DB 展开，记录团队怎样在共享和隔离之间调整。

## 分区键划分数据，物理分区分配资源

以用户 ID 为分区键时，同一用户的记录可以落在同一个逻辑分区。数据库会把许多逻辑分区放到物理分区上，它们共享这一物理分区可用的吞吐。如果一个用户或工作负载突然变热，即使其他用户用了不同的键，也可能因共享资源而被限流。这就是一种“吵闹邻居”问题。

## 从专用容器回到有保护的共享容器

团队试过把负载拆到独立容器，降低彼此影响。这改善了部分隔离问题，但每个容器都要提前规划容量，流量骤增或资源分布变化时仍然难以调整。后来 Habitat 默认使用共享容器，同时保留迁移数据的能力，把不适合继续共享的负载移走。

在共享容器里，热键限流优先限制最热的键。服务质量策略则会优先限制批量导入、数据抽取等低优先级流量，为在线交互保留空间。前者按热点限制，后者按业务优先级分配资源。

## 对日常系统设计的启发

容量监控需要能下钻到分区和流量类型，否则总吞吐还有余量也可能掩盖局部拥堵。共享资源适合容量需求分散的工作负载。准备请求优先级、限流和搬迁路径，可以减少团队在发现热点后临时拆库的压力。
