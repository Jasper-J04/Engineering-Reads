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

一次发布之后，用户等待 ChatGPT 开始输出的时间变长了。告警能指出异常，但工程师还要判断变慢发生在哪类请求上、哪些版本发生了变化，以及改动上线后是否真的恢复。Performance Factory 把这条原本靠人接力的流程拆成了有状态的任务。

## 先理解什么是性能回归

性能回归是一次变更让原来正常的性能指标变差。例如首 token 延迟指从发送请求到收到第一个输出 token 的时间。此时，即使整段回复的生成速度没变，用户也可能觉得产品变慢了。单一指标可以提示调查方向，定位原因仍需要把异常与版本、流量或依赖变化对照。

## 从告警走到恢复

告警创建任务。任务服务存下当前阶段、已有证据和下一步，调度循环为可执行的阶段分配云端 Codex。任务需要等待部署或新的数据时，可以停在当前阶段，由订阅在状态变化后唤醒后续调查。

调查助手先提出原因并记录证据，再由复核助手尝试推翻这个解释。例如，如果怀疑某次发布造成变慢，可以对照受该发布影响与未受影响的相似请求。工程师仍负责审查与部署修复。部署后，系统回看线上指标，确认异常是否消退。

## 这套做法的边界

OpenAI 报告，在三个多月中，这条流程追踪了 1,700 多次调查，600 多起找到了根因。这两个数字描述的是调查和定位的进度，修复与恢复需要另行确认。对一般工程团队来说，可先从保存告警证据、让任务能暂停和恢复做起，再决定哪些调查步骤适合交给助手。
