Title: 把一次数据库变更拆成可回滚的发布
Slug: safe-database-migrations
Date: 2026-11-23T15:00:00+08:00
Summary: 用一次字段替换演示如何分步升级表结构、应用读写逻辑和历史数据。
Tags: engineering, databases
Source: example-notes
Source_url: https://example.org/notes/database-migrations
Source_title: 把一次字段替换拆成几个安全步骤
Kind: digest

给线上表增加一个替代列时，发布期间通常会有新旧版本应用同时读写。可以将这次迁移拆成几次独立发布，为每一步留出观测和回退时间。

## 让新旧版本同时工作

1. 添加新列，保留旧列的读写行为。
2. 部署兼容版本，将新写入同步到两列，并分批回填历史数据。
3. 核对数据一致性后切换读取。等需要旧列的版本退出，再清理旧列。

## 回填关注什么

按主键范围划分小批次，记录已完成的位置。回填速度由线上延迟和锁等待决定。切换前再对一遍空值数量与差异记录，并为异常批次保留重跑入口。
