Title: OpenAI 怎样用 Pando 扩展 Git 服务
Slug: openai-pando-git
Date: 2026-11-24T17:22:45+08:00
Summary: 理解 Git 对象、分支引用和 packfile，再看 Pando 如何让并发写入和高吞吐读取共存。
Tags: distributed-systems, infrastructure, engineering
Source: openai-engineering
Source_url: https://openai.com/index/scaling-git-at-openai
Source_title: Scaling Git at OpenAI
Kind: guide
Source_date: 2026-11-02
Source_author: Aaron Friel, Taylor Blau, Ted Nyman

OpenAI 的工程团队面对大量自动化任务同时推送、拉取和克隆仓库的压力。Pando 的设计从一个具体问题开始：Git 客户端看到新的分支指针后，服务端怎样让它拿到背后的对象，同时避免让不同分支的写入彼此等待？

## Git 对象、引用与打包

提交对象指向一棵目录树和它的父提交。目录树指向文件内容对象或子树。分支引用保存的是提交 ID，像一个可以移动的入口。Git 可以把对象独立存储，也可以将它们装进 packfile，对相似内容只存差异。服务端更新引用时，读者也必须能取到所需的对象。

## 从已有做法到 Pando

原文比较了协调多副本的三阶段提交方案，以及以对象存储保存预写日志的方案。设计上的关键是写入何时可读，以及跨副本或跨对象的等待会怎样影响吞吐。Pando 用因果一致性明确可见范围：一个读取者看到某次写入，也应看到这次写入已经依赖的历史。

用一个例子理解：主分支推进后，写入者基于新的主分支继续推送功能分支。读取该功能分支的客户端需要依赖的主分支历史。Pando 记录这种依赖；功能分支的包可包含该分支此前的提交，读取端按客户端现有对象和目标引用选包。

## Push、Fetch 与后台压实

写入时，Pando 将包保存到对象存储，并在元数据服务记录引用版本。读取时，服务从已存在的包里挑出客户端缺少的范围，包括尚未取得的分支依赖。后台会把多个小包压实为更大的包，改善压缩率与读取效率。

官方文章的模拟将「写入确认」和「另一个读者能检出该版本」都纳入比较。实际部署中的读写比例、分支结构与包大小会影响收益。另一条设计路线在 [Anthropic 的 Scion](/posts/anthropic-scion-source-control/) 一文中可对照阅读。

## 原文插图

- [开篇交互图](<https://openai.com/index/scaling-git-at-openai>)
- [Git 对象与引用关系](<https://images.ctfassets.net/kftzwdyauwt9/2HM5lol94vaZXcGl7zXuf1/96c979a79f2b5971397cf3068a4767da/how-git-objects-reference-each-other-diagram-desktop-light.svg?w=3840&q=90>)
- [packfile 和增量压缩](<https://images.ctfassets.net/kftzwdyauwt9/4xklltw3tJY3qRk8mzW0l3/f7f44a2cb856b00677a31506465e6d1a/storing-git-objects-in-packfiles-diagram-desktop-light.svg?w=3840&q=90>)
- [主分支与功能分支的包](<https://images.ctfassets.net/kftzwdyauwt9/5wDkqDPp9fjzOjtAQRDRzw/117b2f107fd11818f7e9154c958b0878/representing-branches-in-pando-diagram-desktop-light.svg?w=3840&q=90>)
- [Git 服务方案模拟](<https://openai.com/index/scaling-git-at-openai#:~:text=Simulating%20Git%20Server%20ImplementationsFollow%20each%20writer>)
- [Pando 推送与读取](<https://openai.com/index/scaling-git-at-openai#:~:text=Pushing%20and%20Fetching%20a%20Branch%20in>)
- [公布引用数量与包大小](<https://images.ctfassets.net/kftzwdyauwt9/3H8EcvD2zWlkO6LDnf4Zzy/90597498322b48ae7215638f012fe716/how-advertised-refs-affect-packfile-size-diagram-desktop-light.svg?w=3840&q=90>)
- [规划读取所需的包](<https://openai.com/index/scaling-git-at-openai#:~:text=Planning%20fetches%20in%20PandoPando%20compares%20what>)
- [后台压实过程](<https://openai.com/index/scaling-git-at-openai#:~:text=Compaction%20in%20PandoSmall%20packfiles%20are%20grouped>)
- [部署数据图（原文部署一节含两图）](<https://openai.com/index/scaling-git-at-openai#:~:text=Deploying%20Pando>)
