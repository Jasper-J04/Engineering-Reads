Title: Anthropic 的 Scion 如何把保存变更和移动分支分开
Slug: anthropic-scion-source-control
Date: 2026-11-24T17:22:45+08:00
Summary: 从提交快照与变更日志的区别出发，理解 Scion 如何缩短并发写入路径，并另外构建历史查询索引。
Tags: distributed-systems, infrastructure, engineering
Source: anthropic-engineering
Source_url: https://www.anthropic.com/research/redesigning-source-control
Source_title: Redesigning source control at Anthropic
Kind: guide
Source_date: 2026-10-13
Source_author: Nick G. and the Anthropic source control team

Anthropic 工程团队在单体仓库增长过程中遇到了大量并发变更。Scion 的出发点是把保存变更、移动分支指针和读历史索引拆成各自独立的问题。

## 快照和变更日志

Git 提交指向一棵目录树，可以用它解释当时完整的文件结构。Scion 的 changeset 保存相对第一个父提交发生变化的文件列表，文件内容压缩后存入对象存储，变更通过由内容决定的地址引用它们。changeset 是预写日志里一条记录，存储系统可以据此追加变更。

## 保存变更与移动分支分别执行

Scion 在服务端生成 changeset，创建与读取提交时无需先移动分支引用。需要更新引用时，服务在 Spanner 中对单行执行比较并交换。它先检查分支仍指向调用者预期的旧值，匹配才写入新值。这样并发修改不会默默覆盖彼此的引用更新。

## 为历史查询预计算数据

变更日志容易追加，不过回答「某一行最后由谁修改」时，逐条重放会很慢。Scion 从父提交及当前变更递推计算派生数据，例如文件行历史、路径历史或提交图索引。团队还讨论了检出架构以及对原生 Scion 仓库观察到的性能变化，原图提供比较口径。

把写入路径做短，需要在读取和索引维护上付出相应成本。如果要保留标准 Git 客户端，可以比较 [OpenAI 的 Pando](/posts/openai-pando-git/) 如何在 Git 协议内处理并发与读取。

## 原文插图

- [封面插画](<https://assets.claude.com/cfb6c0671a1e04252d55fc3c6776daad399e8356.jpg?w=1920&q=75&fm=webp&fit=max>)
- [单体仓库每日合并量](<https://assets.claude.com/1e2a750dba61db4a76b72eec5b0cf50b8a7f878c.png?w=3840&q=75&fm=webp&fit=max>)
- [传统 Git 检出扩展架构](<https://assets.claude.com/ff019752973f6d83d2f6ba3bf56636aced3ea82c.png?w=3840&q=75&fm=webp&fit=max>)
- [Scion changeset 的结构](<https://assets.claude.com/71c83868210b4b571abb068ea4cd76de749566b1.png?w=3840&q=75&fm=webp&fit=max>)
- [Scion 检出架构](<https://assets.claude.com/cba1eaaa67385fd00f210badaacd147de480120b.png?w=3840&q=75&fm=webp&fit=max>)
- [Scion 与 Antique 每周变更量](<https://assets.claude.com/dd91296719203f38229824bb9bc9e9a61c76ed67.png?w=3840&q=75&fm=webp&fit=max>)
- [原生 Scion 仓库性能](<https://assets.claude.com/c706fa6efb4b9e5cd2566cb080acbfce7218042d.png?w=3840&q=75&fm=webp&fit=max>)
