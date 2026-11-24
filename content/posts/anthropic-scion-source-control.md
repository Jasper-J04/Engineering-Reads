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

当工程师与大量自动化任务同时修改一个大仓库，版本控制服务既要快速接收变更，又要让用户方便地查询历史和更新分支。Anthropic 的 Scion 把这些操作拆开，各自使用合适的数据结构。

## 快照和变更记录有什么区别

Git 提交指向一棵目录树，从而描述某一时刻的文件快照。Scion 的 changeset 则记录相对第一父提交变了哪些文件，并存下指向压缩文件内容的地址。地址由内容决定，因此可以把“文件内容存在哪”与“哪个变更引用这个文件”分别处理。

## 分开写入变更和更新分支引用

Scion 在服务端把 changeset 写入日志。保存变更时无需接收 Git packfile，也无需同时移动分支引用。要更新分支时，系统才对 Spanner 中的一行执行比较并交换。直观地说，只有分支当前值仍是调用方之前看到的值，才接受这次更新。这可以避免两次并发更新无声地覆盖彼此。

## 读取侧需要另外准备索引

变更日志适合追加写入，但单看一条变更，很难立即回答“谁最后修改了这一行”或“哪些提交改过这个路径”。Scion 从变更和父提交派生出行级历史、路径历史等查询结构。这样，写入可以保持简洁，查询则不用每次都重扫历史。

Scion 的取舍适用于并发写入和历史查询都很重的场景，也带来额外的索引维护工作。可以对照[OpenAI 的 Pando](/posts/openai-pando-git/)，后者在 Git 协议内扩展对象读取和分支写入。
