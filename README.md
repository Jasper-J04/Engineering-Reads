# Engineering Reads

Engineering Reads 是一个面向中文读者的技术阅读站。Python 和 Pelican 将 Markdown、Jinja2 模板和 CSS 构建为静态网站，提供按收录时间排序的首页、文章、主题、归档和 RSS。

发布链路为 **GPT 定时任务 → GitHub 提交 → Cloudflare Pages 构建**。文章整理使用 ChatGPT 套餐额度。演示站提供两篇自建示例。正式来源已确认，首批文章待审核后导入。

## 本地构建

在仓库根目录安装锁定依赖。项目使用 Python 3.12，部署版本记录在 `.python-version`。

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

构建和预览演示站。

```sh
.venv/bin/python -m engineering_reads build --demo
.venv/bin/python -m http.server 8000 --directory output-demo
```

浏览 `http://localhost:8000/` 查看首页，或打开 `/tags/`、`/archives/` 与 `/rss.xml`。演示站读取 `demo/` 内的占位来源、两篇虚构稿件和状态，所有原文入口指向 `example.org`。

正式构建读取根目录的来源与状态，以及 `content/posts/` 的稿件。站点默认以空内容启动。

```sh
.venv/bin/python -m engineering_reads validate
.venv/bin/python -m engineering_reads build
.venv/bin/python -m unittest discover -s tests
```

正式产物为 `output/`。使用 `.venv/bin/python -m http.server 8000 --directory output` 可以本地预览。验稿命令也支持 `validate --demo`。

## 内容和定时任务

- `sources.json` 管理来源 ID、语言、官方 RSS 或技术文章索引、允许域名和全文翻译权限。
- `topics.json` 管理主题 ID 和中文名称。
- `content/posts/` 保存稿件，`state/articles.json` 保存去重键和处理状态。
- `theme/` 包含站点模板和样式。

使用[发布契约](docs/publishing-contract.md)编写稿件和状态。将 [GPT 定时任务指令](docs/gpt-scheduled-task.md)复制到你配置的定时任务。当前来源由维护者手动筛选，正式站点从空稿件状态启动。

## Cloudflare Pages 部署参数

项目交付后，在 Pages 中连接本仓库，并按以下参数配置 Git 集成。

| 项目 | 配置 |
| --- | --- |
| 生产分支 | `main` |
| 构建根目录 | 仓库根目录 |
| 框架预设 | None |
| 构建命令 | `python -m pip install -r requirements.txt && python -m engineering_reads build` |
| 输出目录 | `output` |
| Python 版本 | 使用 `.python-version`，也可将 `PYTHON_VERSION` 设为文件记录的版本 |
| 生产环境 `SITE_URL` | 站点的公开 HTTPS 地址，例如 `https://engineering-reads.pages.dev` |
| `SKIP_DEPENDENCY_INSTALL` | `1`，由上面的构建命令安装锁定依赖 |

定时发布前，用实际任务的写入身份验证一次普通 push，对照 Pages 上记录的 Git 提交 SHA 和线上页面。构建失败时按该 SHA 检查校验或构建日志，修复后重新部署。 [Pages 构建环境](https://developers.cloudflare.com/pages/configuration/build-image/) · [Git 集成](https://developers.cloudflare.com/pages/configuration/git-integration/)
