# 发布契约

定时任务以仓库最新目标分支为输入。一个批次可新增 `content/posts/*.md` 并更新 `state/articles.json`，两者进入同一个提交。来源、主题和站点代码由维护者更新。

## 来源与主题

`sources.json` 的 `sources` 是来源数组，默认为空。每个来源的字段为 `id`、`name`、`language`、`feed`、`hosts`、`allow_full_translation`。来源 ID 唯一，由小写英数字和连字符组成。语言为 `en` 或 `zh`，`feed` 为 HTTPS URL，`hosts` 列出文章允许的准确小写域名。全文翻译权限由维护者审核后设置。

`topics.json` 将稳定的主题 ID 映射到中文标签。文章从这个清单选择 1 至 5 个不同主题，按逗号和空格分隔。

## 规范化 URL

对原文 URL 使用 HTTPS，主机名转小写，移除默认端口 `443`、URL 片段、末尾斜杠和追踪参数。根路径保留为 `/`。移除的查询参数包括 `utm_*`、`gclid`、`fbclid`，按 URL 解码后的参数名忽略大小写匹配。其他查询项保留原内容和顺序。文章的 URL 必须属于其来源的 `hosts`。

例如 `https://EXAMPLE.org:443/notes/queues/?id=42&utm_source=feed#details` 规范化为 `https://example.org/notes/queues?id=42`。稿件的 `Source_url` 与状态记录的键使用同一个规范化值。

## 稿件 Markdown

使用 UTF-8 文本，文件大小上限为 128 KiB。一个字段占一行，拼写和大小写按表填写，形式为 `字段: 值`。元数据与正文之间空一行。

| 字段 | 规则 |
| --- | --- |
| `Title`、`Summary` | 中文标题和独立摘要 |
| `Slug` | 小写英数字词组，使用连字符分隔，最多 80 字符，与文件名一致。首次确定后保持稳定 |
| `Date` | 首次成功收录的北京时间，格式为 `YYYY-MM-DDTHH:MM:SS+08:00` |
| `Tags` | 从 `topics.json` 选择 1 至 5 个 ID |
| `Source`、`Source_url`、`Source_title` | 来源 ID、规范化原文地址、原文实际标题 |
| `Kind` | 外文导读用 `guide`，中文整理用 `digest`，获授权的外文全文翻译用 `translation` |
| `Source_author`、`Source_date` | 可选，核实后填写。原文日期用 `YYYY-MM-DD` |
| `Source_license`、`Source_license_url` | 可选，核实后填写。提供 HTTPS 许可链接时同时填写许可名称。全文翻译要求两者齐全且来源已获准 |

下面使用演示来源。可直接对照 [完整演示稿](../demo/content/posts/queue-deduplication.md)。

```markdown
Title: 当任务被投递两次：队列消费的幂等设计
Slug: queue-deduplication
Date: 2026-11-24T09:30:00+08:00
Summary: 梳理重复投递时确定幂等键、事务边界和重试时机的方法。
Tags: engineering, distributed-systems
Source: example-engineering
Source_url: https://example.org/engineering/queue-deduplication
Source_title: When a job is delivered twice
Source_author: Demo Editorial Team
Source_date: 2026-11-21
Kind: guide

## 解决的问题

任务可能在提交业务变更之后、确认队列消息之前超时。重试时需要找回本次操作的结果。
```

正文侧重原文提出的问题、实现方法、能核实的结果与适用范围。原文中的许可和转载范围由维护者确认。可使用代码块、列表和表格，渲染会清理不安全的 HTML 和链接。

## 处理状态 JSON

`state/articles.json` 的顶层字段为 `version` 和 `articles`，当前版本为整数 `1`。以规范化原文 URL 为唯一键，每条记录共用 `source`、`status`、`attempts` 三个字段。

| 状态 | 尝试次数 | 附加字段与处理 |
| --- | --- | --- |
| `pending` | 0 | 保存已发现、待处理的条目，即使下次运行时条目已离开 Feed |
| `retry` | 1–2 | `retry_at` 为北京时间，格式与 `Date` 相同。用 `reason` 记录简短原因，到时再处理 |
| `held` | 1–3 | 用 `reason` 记录原因。第三次失败或需要人工核实时暂停 |
| `published` | 1–3 | `slug` 指向对应 Markdown，来源 ID 和 URL 也必须一致。此状态表示稿件已入库 |

`reason` 使用最长 240 字符的单行文字。一个失败条目仍可与本批其他成功条目一起提交。推送后的 Pages 上线进度查看对应提交的部署记录。

```json
{
  "version": 1,
  "articles": {
    "https://example.org/engineering/queue-deduplication": {
      "source": "example-engineering",
      "status": "published",
      "attempts": 1,
      "slug": "queue-deduplication"
    },
    "https://example.org/engineering/recovered-comments": {
      "source": "example-engineering",
      "status": "retry",
      "attempts": 1,
      "retry_at": "2026-11-25T09:30:00+08:00",
      "reason": "原文暂不可读"
    }
  }
}
```

## 提交与故障处理

同一输入重复运行时，跳过已入库 URL，复用已有状态和稿件文件名。无变化时保持工作树整洁并直接结束。远端分支已前进时，读取最新状态并重新核对去重键，再用普通 push。

本地可以运行 `python -m engineering_reads validate`；部署构建也会执行同样的校验。检查失败时按输出修正文档或 JSON，保持稿件与状态一致。发现已上线内容问题时，以更正提交更新受影响稿件及状态。
