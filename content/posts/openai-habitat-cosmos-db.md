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

OpenAI 用 Habitat 为 ChatGPT 等产品提供在线数据访问。Storage Part II 从一个很常见的问题开始：多个功能共享容量时，一项流量突增可能拖慢无关的关键请求。文中记录了团队如何从依赖数据库内建能力，走到默认共享但能主动隔离的架构。

## 理解 Cosmos DB 分区

逻辑分区由分区键决定。例如同一用户的数据可以使用同一个键。多个逻辑分区可以共享一个物理分区的吞吐。同一个用户的不同功能也可能争用同一个键。一个热点会让同一物理分区中的其他键被限流；总容量还有余量时，局部也可以已经饱和。

## 三个阶段的取舍

1. **依赖内建分区机制。** 工程团队遇到了逻辑键自身的限制、物理分区上的互相干扰，以及分区拆分后容量与需求不匹配的问题。
2. **按工作负载拆分容器。** 独立容器改善隔离，但每个容器要各自规划容量。历史流量比例稳定也无法保证新功能在上线时继续按同一比例增长。
3. **默认共享，同时保留搬迁能力。** 热键限流限制最热的键，服务质量策略先限制低优先级后台请求。团队也保留把负载迁走的手段，避免极端负载长期占用共享容量。

## 跨区域与变更流

部署遍布多地时，计算和数据可能落在不同区域。访问路径绕远会直接体现在延迟上。原文分别介绍了全球流量路径、读延迟优化，以及变化数据捕获（CDC）的扩容。CDC 可以理解为把存储写入的变化交给下游处理，因而也有自己的吞吐与延迟预算。

原文图 05 给出的读 p50 约从 120 毫秒降到 10 毫秒，指该案例中多项改动后的中位延迟。看自己的系统时，可以分别观察分区热点、业务优先级和跨区路径，再决定该调容量、加限流还是搬迁数据。

## 原文插图

- [图 01 · Habitat 平台](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2001%20%C2%B7%20What%20is%20Habitat%3FOnline>)
- [图 02a · 同一分区键的资源争用](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2002a%20%C2%B7%20Logical%20partition%20key>)
- [图 02b · 不同键共用物理分区](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2002b%20%C2%B7%20Noisy%20neighborsDifferent%20users%2C>)
- [图 02c · 分区拆分后的容量不足](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2002C%20%C2%B7%20Weak%20partitionsThe%20limit>)
- [图 03 · 负载增长与容量余量](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2003%20%C2%B7%20Lack%20of%20stable>)
- [图 04 · 全球读流量](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2004%20%C2%B7%20Improving%20performance%20at>)
- [图 05 · 读延迟 p50](<https://openai.com/index/scaling-storage-one-billion-users-part-two#:~:text=Figure%2005%20%C2%B7%20Improving%20performance%20at>)
