Title: 智能体怎样把会话经历变成下次可用的记忆
Slug: anthropic-agent-memory
Date: 2026-11-24T17:22:45+08:00
Summary: 拆解会话记录、长期笔记与离线回顾，理解下一次会话怎样找到需要的知识。
Tags: ai, architecture, engineering
Source: anthropic-engineering
Source_url: https://www.anthropic.com/research/components-of-agent-memory
Source_title: The components of agent memory
Kind: guide
Source_date: 2026-11-06
Source_author: Lance Martin

智能体在任务中获得的经验，往往在下一次会话开始时派上用场。Anthropic 将这件事拆成几个问题：何时写笔记，怎样用原始记录纠错，什么时候给长期记忆建立索引，以及哪些内容值得在新会话开始时直接加载。

## 记忆的四层

会话记录是可回查的原始证据。记忆笔记是助手当时判断有价值的观察。Wiki 等表示将多条笔记按主题组织起来。注入上下文则是每次会话开始时直接交给模型的信息。上下文窗口里的内容会占用当次输入预算，因此只有反复用到的信息适合常驻。

例如，排查故障时，一条笔记可以记录已经验证过的假设，并附原始日志位置。下一轮助手可以先读笔记，遇到不确定的地方再查日志。

## 当场写笔记与会话间回顾

当场记录的优点是线索还新鲜，难点是当时并不知道哪些信息以后重要。文章将空闲时重新浏览会话与笔记的过程称为 dreaming，可以理解为离线回顾。它能对照记录修正误记，也能建立 Wiki 或调整下次启动时加载的内容。

文中游戏案例展示了误记路线对后续行动的影响。回顾阶段发现笔记与原始记录不符，修正后助手走到了下一座城市。企业文档案例则比较了 Wiki 与文档搜索：横跨多份材料的问题更可能受益，答案集中在一份文档时已有搜索就能覆盖不少需求。

## 使用这些结果时看什么

数据库任务的图表比较了不同模型在不同记忆设置下的表现，并展示了记录指令如何影响结果。Wiki 还会增长，甚至超过原始文档，因此整理也有成本。文章的结论适合指导实验设计：记录是否可核查、命中时是否有用、错误是否能被修正，应分别测量。

## 原文插图

- [封面插画](<https://assets.claude.com/c370e12cc7b368ea06cd08e2495a366c7cfc7edc.jpg?w=1920&q=75&fm=webp&fit=max>)
- [会话间回顾与记忆层次](<https://assets.claude.com/a0bcfa203214d817d2b4261b7188aba8be6db5b2.png?w=3840&q=75&fm=webp&fit=max>)
- [会话中写入记忆笔记](<https://assets.claude.com/2ef2bf5c81ea6d578749782782eff10cf3136de4.png?w=3840&q=75&fm=webp&fit=max>)
- [CL-Bench 数据库任务结果](<https://assets.claude.com/bb0d44c78cc431fb5e84fbf2cb17c4303bc6bd65.png?w=3840&q=75&fm=webp&fit=max>)
- [不同模型的游戏记忆目录](<https://assets.claude.com/5e15e10f665773050d90fafc38ab8dd76ae5368b.png?w=3840&q=75&fm=webp&fit=max>)
- [记录提示对数据库任务的影响](<https://assets.claude.com/da03e864e4eba93a91314fa5f2a5d0e4c14b2a0f.png?w=3840&q=75&fm=webp&fit=max>)
- [用会话记录校正笔记](<https://assets.claude.com/55ce85bd12860090704a5543a3da7504334ad9a9.png?w=3840&q=75&fm=webp&fit=max>)
- [游戏地图上的两条路线](<https://assets.claude.com/d906d6ed9ac92db36631a624ad517183b07a545d.png?w=3840&q=75&fm=webp&fit=max>)
- [路线修正前后的进度](<https://assets.claude.com/2eb2bfe6d01e9a1fca74a41e952d948c09d42008.png?w=3840&q=75&fm=webp&fit=max>)
- [从记录和笔记建立 Wiki](<https://assets.claude.com/30923242548d746ee77784c87826cadc46574c34.png?w=3840&q=75&fm=webp&fit=max>)
- [Wiki 建设与问答表现](<https://assets.claude.com/1d2dbef8673a89b6e02f9f64672a7a39f50d3884.png?w=3840&q=75&fm=webp&fit=max>)
- [综合多文档和单文档任务对比](<https://assets.claude.com/73f1419705be76d3759949cf0de96e26c0540a4b.png?w=3840&q=75&fm=webp&fit=max>)
- [Wiki 与原始文档的体量](<https://assets.claude.com/ffa35479b1dea63b7948f76995b488d08854e86d.png?w=3840&q=75&fm=webp&fit=max>)
- [把常用信息放进启动上下文](<https://assets.claude.com/c88bcc04c5d0e77db5828c9dbe72faf1c4421f8f.png?w=3840&q=75&fm=webp&fit=max>)
- [合同事实的并发写入对比](<https://assets.claude.com/592f604d38e90537553ab7127d1d3115924fda92.png?w=3840&q=75&fm=webp&fit=max>)
- [两轮回顾后 Wiki 的变化](<https://assets.claude.com/5f7e61c50360f39ddad5c7188191562a59e12e11.png?w=3840&q=75&fm=webp&fit=max>)
