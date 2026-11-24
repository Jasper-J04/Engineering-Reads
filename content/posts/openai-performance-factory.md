Title: ChatGPT 变慢后，OpenAI 怎样用 Codex 定位性能回归
Slug: openai-performance-factory
Date: 2026-11-24T17:22:45+08:00
Summary: 把告警变成可追踪的任务，让 Codex 找证据、另一轮调查复核，最后用生产指标确认恢复。
Tags: performance, engineering, ai
Source: openai-engineering
Source_url: https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast
Source_title: How OpenAI’s Performance Factory keeps ChatGPT fast
Kind: guide
Source_date: 2026-11-19
Source_author: Okay Zed, Cyrus Forbes

性能告警通常只能回答「什么指标变差了」。从那里到恢复，还要定位受影响的请求、找到可复核的解释、部署修复，并确认线上指标回到正常范围。OpenAI 的 Performance Factory 把这段工作记录为可以暂停、移交和恢复的任务。

## 从人工调查到自动化工作流

以首 token 延迟为例，它衡量发出请求到收到第一个输出 token 的时间。遇到回归，工程师通常会按请求类型、地区或发布版本缩小范围，再借助剖析工具寻找热点。CPU 剖析关注时间花在哪段代码，分配剖析则关注哪些操作产生了较多的内存分配。把重复使用的查询和工具固定下来，调查才容易交给另一个人或助手继续。

## 系统由四部分组成

| 组件 | 职责 |
| --- | --- |
| 任务服务 | 保存阶段、进展与调查证据，允许工程师定义不同工作流 |
| 调度循环 | 找出已具备继续处理条件的任务，并分配助手 |
| 云端 Codex | 执行分析，记录发现与下一步 |
| 订阅 | 在评论、部署等事件改变任务状态时，让等待中的任务重新进入调度 |

任务的进展由任务服务保存。例如，修复部署之前没有必要重复运行恢复检查。等部署事件到来，下一轮助手可以读取已有证据再继续。

## 第一个工作流：从告警到恢复

1. **调查根因。** 从监控信号和历史变更中找出解释，并把证据集中记录在任务里。
2. **独立复核。** 复核者尝试证伪诊断。例如，某次发布真是原因时，未受发布影响的相似请求是否也变慢？时间先后是线索，仍需对照。
3. **修复与验证。** 助手可以提出修复，由工程师决定审核和部署。部署后，助手回看指标，确认用户看到的异常是否已经消退。

## 运行结果和取舍

原文报告，三个多月追踪了 1,700 多次调查，其中 600 多起找到了根因。定位数量和完成修复的数量是两个不同口径。作者也强调保护工程师的注意力、评估每次工作流改动，以及把经常反复出现的故障转成专门工具。对已有稳定告警和观测能力的团队，先做「证据留存和可暂停的任务」就能验证这套设计是否适合自己的值班流程。

## 原文插图

- [性能工程工作方式的演变](<https://images.ctfassets.net/kftzwdyauwt9/581rKVIvguLraKii21zIgr/83deca5cdcec639b656a9a5ec1954f4b/performance-factory-evolution-light.png?w=3840&q=90&fm=webp>)
- [Performance Factory 调度架构](<https://images.ctfassets.net/kftzwdyauwt9/4GVsirng1kgJ1GzSsQ9Iof/f21a0b8682d456132be1ef8e1b9ce0ed/performance-factory-orchestrator-architecture-light.png?w=3840&q=90&fm=webp>)
- [从检测到恢复的交互流程](<https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast#:~:text=The%20Regression%20Workflow%E2%80%99s%20steps%20include%20finding>)
- [工作进程启动回归的调查报告](<https://images.ctfassets.net/kftzwdyauwt9/5w8KpwlFR3tNfJbAStImkG/ee5f1df65a302cb09dde0a7d52d09138/performance-factory-worker-startup-report.png?w=3840&q=90&fm=webp>)
- [不同工作流之间的任务协作](<https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast#:~:text=From%20one%20workflow%20to%20many.%20The>)
