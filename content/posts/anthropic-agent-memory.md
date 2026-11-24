Title: 智能体怎样把会话经历变成下次可用的记忆
Slug: anthropic-agent-memory
Date: 2026-11-24T17:22:45+08:00
Summary: 拆解会话记录、长期笔记与离线回顾，理解下一次会话怎样找到需要的知识。
Tags: ai, architecture, engineering
Source: anthropic-engineering
Source_url: https://www.anthropic.com/research/components-of-agent-memory
Source_title: The components of agent memory
Kind: translation
Source_date: 2026-11-06
Source_author: Lance Martin

<figure>
  <img src="https://assets.claude.com/c370e12cc7b368ea06cd08e2495a366c7cfc7edc.jpg?w=1920&amp;q=75&amp;fm=webp&amp;fit=max" alt="原文封面插画">
  <figcaption>原文封面插画</figcaption>
</figure>

克尔凯郭尔写道，人生只能回头理解，却必须向前生活。我们在设计 AI 智能体的记忆时，也遇到了类似的难题。

人在日常生活中不断形成记忆。[海马体](https://stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf)在其中发挥关键作用：它即时捕捉经历，使记忆迅速形成并可立即调用。但只有[部分经历](https://www.science.org/doi/10.1126/science.adk8261)最终会巩固为长期知识。

许多巩固过程似乎发生在大脑离线的时候。在睡眠和[安静休息](https://www.nature.com/articles/s41467-018-06213-1)期间，海马体会重放近期经历。研究者认为，这让经历逐渐得到[提炼，并融入新皮层](https://www.nature.com/articles/s41593-019-0467-3)。我们通常所说的知识，很大一部分存储在那里。

智能体的记忆也可以这样分工。智能体通过日志或会话记录保留许多工作细节。Letta 和加州大学伯克利分校的研究者提出了[睡眠期计算](https://arxiv.org/abs/2504.13171)：让模型在交互间隙利用空闲时间重新组织已有上下文。智能体同样可以回看日志、修正错误、创建笔记和新的记忆表示。这一过程常称为 [*dreaming*](https://platform.claude.com/docs/en/managed-agents/dreams)，下文译作「离线回顾」。

我们发现，离线回顾有助于 Claude 形成有效的记忆。本文介绍我们如何理解智能体记忆，以及用哪些评估来研究记忆和离线回顾，并查看各个组成部分怎样帮助组织记忆。

<figure>
  <img src="https://assets.claude.com/a0bcfa203214d817d2b4261b7188aba8be6db5b2.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="离线回顾可以修正错误、创建笔记、构建新的记忆表示，或决定未来会话开始时预先加载哪些内容。">
  <figcaption>图 1 · 离线回顾可以修正错误、创建笔记、构建新的记忆表示，或决定未来会话开始时预先加载哪些内容。</figcaption>
</figure>

## 记忆笔记

本文所说的「智能体记忆」，是 Claude 从经历中获取、跨会话保留，并能在之后作为上下文读到的知识。这些经历包括与用户的交互和接到的任务。这里将几种机制另作区分：训练时改变模型内部参数，单次对话内的[上下文学习](https://www.anthropic.com/research/in-context-learning-and-induction-heads)，以及用摘要替换旧对话轮次、让工作能在新上下文窗口中继续的压缩。

在人脑中，一段经历前后或发生期间释放的化学信号，可以[标记某些记忆的重要性](https://www.nature.com/articles/385533a0)。离线时，被标记的记忆更常被重放。重放有助于稳定这些记忆，并把它们融入长期记忆。

Claude 同样可以在会话日志里即时标记重要事件，方便日后查找，也可以把事件写入[记忆存储](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)，例如一个保存记忆笔记的目录。可是在还不知道接下来会发生什么时，Claude 怎样判断什么值得记下？

<figure>
  <img src="https://assets.claude.com/2ef2bf5c81ea6d578749782782eff10cf3136de4.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="Claude 可以将重要观察写入记忆笔记。">
  <figcaption>图 2 · Claude 可以将重要观察写入记忆笔记。</figcaption>
</figure>

## 记忆可以预测未来需要什么

有时，记忆是一种预测。智能体写下一条规则，就相当于预测它描述的规律以后还会用到。记录一个已验证的事实，也是在预测未来会话可能直接采用它，而无需再次核查。随着模型迭代，Claude 越来越擅长做这类判断。

以[持续学习基准 CL-Bench 1.0](https://continual-learning-bench.com/news/cl-bench-1-0/) 为例。它评估智能体能否用记忆完成长程任务。其中一个任务要求 Claude 查询数据库，逐一回答一系列问题。每次作答后，Claude 会获知正确答案，也可以写下以后可能有用的记忆。

记忆在这里可以形成一个学习闭环。Claude 答错后可以记录失败，提出原因假设，验证这些假设，再把结果归纳为未来作答可用的规则。

我们用 [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) 运行了这项任务。每道题都从新会话开始，唯一例外是 Claude 可以读取[跨会话保留的记忆目录](https://platform.claude.com/docs/en/managed-agents/memory)。

各模型建立学习闭环的程度不同。Claude Sonnet 4.6 能提出答错的原因假设，目录中却散落着多个文件，每个都记录了若干未经检验的猜想。

<figure>
  <img src="https://assets.claude.com/bb0d44c78cc431fb5e84fbf2cb17c4303bc6bd65.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="CL-Bench 数据库任务中，各模型使用记忆与无状态基线的比较。">
  <figcaption>图 3 · CL-Bench 数据库任务中，各模型使用记忆与无状态基线的比较。</figcaption>
</figure>

Claude Opus 4.7 把笔记整理成单份参考文档，并标出哪些事实已核验、哪些还待确认。Claude Sonnet 5 在阅卷系统确认后给答案加上标记，答错时则写下更正。

Claude Opus 5 最早完成了这个闭环。它的大多数笔记都记录了规则、规则成立的依据、之前问题的答案，以及探索中发现的陷阱。

Claude Opus 5.5 和 Claude Sonnet 5.5 同样能完成闭环，利用记忆保存经验证的规则，供未来作答使用。二者使用记忆时的分数与 Opus 5 大致相同，不使用记忆时的基线略高。

## Claude 学会判断什么值得记住

我们也用《宝可梦 红》测试 Claude 的判断。游戏要求完成[复杂的长程任务](https://www.youtube.com/watch?v=CXhYDOvgpuU)，每次开始时，模型都可以在游玩过程中读写一个记忆目录。

我们各取 Claude Sonnet 3.7 和 Claude Fable 5 的一次运行，在各自约 10,000 步时比较。两者对「值得记住什么」的看法不同。Sonnet 3.7 认为任何事都可能重要，遇见的战斗、物品、非玩家角色经常各自建档。它在 225 个目录里写了 413 份文件，获得一枚衡量游戏进度的徽章。

Fable 5 在两个目录里写了九份文件，另外顶层有一份 `global.md`，取得了四枚徽章。

<figure>
  <img src="https://assets.claude.com/5e15e10f665773050d90fafc38ab8dd76ae5368b.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="Sonnet 3.7 与 Fable 5 玩《宝可梦 红》时的记忆目录。">
  <figcaption>图 4 · Sonnet 3.7 与 Fable 5 玩《宝可梦 红》时的记忆目录。</figcaption>
</figure>

游戏状态不断变化，Sonnet 3.7 的详细记录也随之迅速过时。随着进度推进，Claude 花在整理记忆上的时间和资源越来越多。比如在约第 10,000 步，它开始建立第四个「主记忆」目录。接下来的 17 步里，它创建了六个文件、删除了九个文件，没在游戏中执行任何动作。

Fable 5 主要保存游戏画面不会直接告诉它的信息。玩家有多少钱、目前在地图哪里，每回合都可以从屏幕读出。策略、计划和已经试验过的规律则需要 Claude 自己归纳，并写下来才能保留。

Fable 5 也据此组织记忆。顶层的 `global.md` 像一块仪表板，保存当前目标、道馆挑战计划和模型自己的记忆使用规则。位置目录保存具体路线，玩法目录保存从游戏中学到的策略。比如，连续扔了七次精灵球也没捉到容易捕获的鲤鱼王后，Claude 记下：连续失败三次以上时，可以调整时机，在菜单操作之间插入额外的等待；它这样操作后便捕获成功。

Fable 5 的记忆目录小得多，游戏进度却远超 Sonnet 3.7。Opus 5.5 采用了类似方式，用一个小目录记录当前目标和接下来的步骤，边玩边改，最终通关。

## 如何引导 Claude 写记忆

我们发现，向 Claude 交代记忆的用途很有帮助。在 CL-Bench 中，仅告诉模型有一个可用的记忆目录，Opus 4.7 和 Opus 5 就能有效使用记忆，表现也明显改善。

我们还逐条测试了规定「该写什么」的提示，把每条规则下的记忆收益和没有规则时的收益比较。要求「只记失败」时，Opus 5 和 Opus 4.7 都失去了原有记忆收益中的很大一部分。对能力更强的模型，让它自行判断重要性更有效；预先设定的固定规则反而可能降低表现。

<figure>
  <img src="https://assets.claude.com/da03e864e4eba93a91314fa5f2a5d0e4c14b2a0f.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="左：引导记忆用法前后，Sonnet 4.6 的数据库任务表现。右：要求只记失败后，各模型的记忆收益变化。">
  <figcaption>图 5 · 左：引导记忆用法前后，Sonnet 4.6 的数据库任务表现。右：要求只记失败后，各模型的记忆收益变化。</figcaption>
</figure>

这些引导最能帮助较早的模型。例如，Sonnet 4.6 常忘记读记忆目录，也往往没有验证自己对答错原因的猜测。

提醒它回答前读记忆，并明确检验猜测，基准分数几乎翻倍。Sonnet 5 自己就会这样做：没有提示时，作答前有九成机会先读记忆；Sonnet 4.6 这样做的比率不到一半。

对于前沿 Claude 模型，我们通常只提示它在用户提出要求或遇到显然值得保留的信息时写笔记，并把具体判断交给它。

## 离线回顾可以纠正错误

笔记可能起初就写错，也可能随着环境变化而过时。Claude 以后读到它时，仍可能把它当成可信信息。

离线回顾可以用原始会话记录检验笔记。我们在 Claude Managed Agents 中挂载了记忆目录，让 Claude 玩《宝可梦 红》，看到一个具体例子。

<figure>
  <img src="https://assets.claude.com/55ce85bd12860090704a5543a3da7504334ad9a9.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="离线回顾可以用会话记录修正记忆笔记。">
  <figcaption>图 6 · 离线回顾可以用会话记录修正记忆笔记。</figcaption>
</figure>

游戏中，玩家必须穿过月见山。洞口在地图西侧，出口在东侧。入口附近有个单向台阶，从那里跳下去会回到来时的道路，很难原路爬上来。Claude 把入口附近的宝可梦中心当作地标。它是否会跳错地方，取决于它判断这个地标在山的哪一侧。

Claude 一度误记宝可梦中心位于东侧。走出中心后，它说月见山已在身后，并在笔记里标为完成。实际上它还在西边。几步之后，它跳下台阶回到了来路。导航工具没有显示落差，Claude 便以为自己往西走过了头，而且之前一直在正确的一侧。

<figure>
  <img src="https://assets.claude.com/d906d6ed9ac92db36631a624ad517183b07a545d.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="左：错误笔记把 Claude 引回旧路。右：修正笔记后，Claude 重新寻找洞口。">
  <figcaption>图 7 · 左：错误笔记把 Claude 引回旧路。右：修正笔记后，Claude 重新寻找洞口。</figcaption>
</figure>

随后我们让 Claude 对包含错误位置的记忆目录做离线回顾。它用会话记录比对笔记，找出错误并改写。得到正确笔记后，它直接返回洞穴，最终抵达华蓝市。

使用未修正笔记的那次运行中，Claude 三次跳回旧路。第三次失败后，它说要停下来，以免继续绕圈。实验系统自动要求它继续，于是它一路回到山前的深灰市，想恢复状态、补充物资。运行结束时，它仍未抵达华蓝市。

<figure>
  <img src="https://assets.claude.com/2eb2bfe6d01e9a1fca74a41e952d948c09d42008.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="有离线回顾的运行到达华蓝市；保留错误笔记和无记忆的对照运行都未通过月见山。">
  <figcaption>图 8 · 有离线回顾的运行到达华蓝市；保留错误笔记和无记忆的对照运行都未通过月见山。</figcaption>
</figure>

## 离线回顾可以创建新的记忆表示

Claude 能用离线回顾建立帮助导航的表示，例如 [Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。Wiki 是 Claude 撰写和维护的一组页面，把它知道的同主题内容收在一起，并链接相关笔记。遇到新任务时，这些链接就像一张地图，帮助 Claude 找到所需的记忆。

<figure>
  <img src="https://assets.claude.com/30923242548d746ee77784c87826cadc46574c34.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="从会话记录和记忆笔记构建 Wiki 等表示。">
  <figcaption>图 9 · 从会话记录和记忆笔记构建 Wiki 等表示。</figcaption>
</figure>

我们用软件公司 Stainless 的内部资料测试 Wiki 的用途：约 35 万个文件，约 4.2 亿 token。我们针对资料编了 25 道评估题，并给 Claude 一个搜索工具，同时让它通过离线回顾建立 Wiki。128 次会话中，Opus 5 智能体探索资料，撰写和修正有链接的页面，合并重复内容，并对照来源核查说法。

各次会话借助一份共享工作日志接续前面的进展。回顾从两次增加到 128 次时，25 道题的评估中，只使用 Wiki 的达标比例由 13% 升到 48%。

Claude 会逐步建立 Wiki，之后反复增补、修改和删减。早期的 Wiki 像新员工刚建立的知识地图，能回答的问题有限；回顾久了，知识地图像资深员工的一样丰富。实验中，搜索与 Wiki 一起使用效果最好：随着 Wiki 增长，综合分从 54% 升到 61%；只搜索是 53%，只用 Wiki 的最高分是 48%。两者一起使用还让每道题少用约 20,000 个 token。

<figure>
  <img src="https://assets.claude.com/1d2dbef8673a89b6e02f9f64672a7a39f50d3884.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="中：Wiki 逐步建立时，25 道题的评估分数。两侧：回顾两次与 128 次后的 Wiki 网络，每个点代表页面。">
  <figcaption>图 10 · 中：Wiki 逐步建立时，25 道题的评估分数。两侧：回顾两次与 128 次后的 Wiki 网络，每个点代表页面。</figcaption>
</figure>

为了解哪些任务受益，我们还用 [Harvey 的 LAB 基准](https://github.com/harveyai/harvey-labs)和一组企业并购文档。LAB 让 Claude 用给定文档撰写法律简报，再按评估标准逐项打分。虽然它可能没有宝可梦那么好玩，这些材料可以提供多样的 Wiki 构建任务。

我们让 Claude 从材料生成 Wiki，再用 Wiki 或直接搜索来回答并购问题、生成法律简报。一项测试有 24 道并购题，过半需要结合多份文档，许多还要求判断或计算。在这类题目上，查 Wiki 的得分为 87%，只搜索为 73%。

<figure>
  <img src="https://assets.claude.com/73f1419705be76d3759949cf0de96e26c0540a4b.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="左：并购问题常需综合多份文件。右：一项 LAB 任务的大多数标准可从单份文件满足，Wiki 的增益不明显。">
  <figcaption>图 11 · 左：并购问题常需综合多份文件。右：一项 LAB 任务的大多数标准可从单份文件满足，Wiki 的增益不明显。</figcaption>
</figure>

在另一些测试里，Wiki 的帮助更小。例如，一项 LAB 任务的大部分标准可以在同一份文件中用文本搜索满足，Wiki 没有带来明显改善。还有一项任务，Wiki 的体量比原材料更大。就像博尔赫斯《论科学的精确性》里绘制出帝国等比例地图的制图师，Claude 做出了一份过于详细的 Wiki，几乎没有提炼材料。

<figure>
  <img src="https://assets.claude.com/ffa35479b1dea63b7948f76995b488d08854e86d.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="一个 Wiki 的体量超过了原始文件。">
  <figcaption>图 12 · 一个 Wiki 的体量超过了原始文件。</figcaption>
</figure>

## 离线回顾可以把笔记提升到记忆顶层

离线回顾能把笔记提升到记忆层次的顶层。智能体运行框架可以在每次会话开始时将它们预先放进 Claude 的上下文。这样 Claude 不必知道要找什么，也不必主动搜索。

这种上下文注入需要谨慎。常驻内容占用 token，错误笔记也可能被带入每一次会话。加载了笔记并不能保证 Claude 会遵循：[Claude Code 的文档](https://code.claude.com/docs/en/memory)提醒，说明文件越长，遵循程度可能越低。因此顶层需要保持精简。离线回顾可以把细节移至下层，在顶层只保留链接。

Claude Code 的自动记忆也按类似方式保持注入层精简，在会话中由 Claude 维护。它不会将所有自动记忆放入上下文，只加载 `MEMORY.md` 的前 200 行或 25 KB。开头部分像索引，告诉 Claude 自己记住了什么、其余细节在哪里。

<figure>
  <img src="https://assets.claude.com/c88bcc04c5d0e77db5828c9dbe72faf1c4421f8f.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="顶层注入上下文在每次会话时加载，下层记忆需要时才读取或搜索。">
  <figcaption>图 13 · 顶层注入上下文在每次会话时加载，下层记忆需要时才读取或搜索。</figcaption>
</figure>

## 离线回顾可以围绕具体目标组织记忆

离线回顾也能引导记忆往某个方向发展。例如 [Claude Duet](https://support.claude.com/en/articles/17631495-get-started-with-claude-duet) 这类助手可能受益于围绕所服务的人组织记忆；具体任务也可以重点保留它需要的信息。

指导记忆增长的提示因任务而异。LAB 有一个模拟企业收购的任务，资料是一组合同，简报按是否准确描述合同条款打分。

我们起初只给了生成 Wiki 的基本指示，没有教 Claude 怎样用 Wiki。任务很依赖条款信息，构建时多个智能体同时写同一张合同条款表。

<figure>
  <img src="https://assets.claude.com/592f604d38e90537553ab7127d1d3115924fda92.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="左：共写一张表时保留了 41 项条款事实。右：每份合同独立成页并逐字摘录时保留了 57 项。">
  <figcaption>图 14 · 左：共写一张表时保留了 41 项条款事实。右：每份合同独立成页并逐字摘录时保留了 57 项。</figcaption>
</figure>

结果有关键事实缺失。根据 Wiki 生成的简报只包含 57 项事实中的 41 项，也就是 72%。检查后发现，共享表对条款的概括不够准确，而并发写入相互覆盖，让一些内容完全消失。

合同条款最重要，最初的指示却没有说明。为找到更好的指示，我们让 Claude 反思失败、提出提示改动，再重新构建 Wiki。通过这个循环，Claude 认识到保留合同条款的重要性，并据此改写了构建指示。

改进后，每份合同在 Wiki 中独占一页，由一个智能体撰写并逐字引用条款。再次评估生成的简报时，可满足的标准由 72% 上升到 100%。

## 离线回顾可以填补单次会话留下的空缺

即时写笔记时，Claude 只看到当前会话的上下文。离线回顾可以搜索多次会话，寻找共性或纠正反复出现的错误。

在为 LAB 建 Wiki 时，Claude 有时会链接到还未创建的页面。再做一轮回顾，可以弥补许多这样的缺口。在一项任务里，它找出九条指向同一缺失页面的链接，将其改到同一份文档的已有页面，还新增了含索引在内的三页。

<figure>
  <img src="https://assets.claude.com/5f7e61c50360f39ddad5c7188191562a59e12e11.png?w=3840&amp;q=75&amp;fm=webp&amp;fit=max" alt="进行第二轮离线回顾前后的 Wiki。">
  <figcaption>图 15 · 进行第二轮离线回顾前后的 Wiki。</figcaption>
</figure>

## 回头思考，向前使用

智能体记忆系统还有不少开放问题。首先是什么时候记忆。执行任务时，Claude 可以把重要信息当场写入目录、文件或数据库，方便之后的轮次或会话立即使用。但当场写笔记会分散做主要任务的注意力。离线回顾可以把整理放到后台，代价是产出可能无法立即使用。

另一个问题是记忆如何保持最新。Claude 可能预测错未来需要什么，或写入本来就错误的规则，环境变化也会让笔记过时。离线回顾能修正这些问题，但需要算力。持续检查所有记忆可能不现实，更值得尝试的是优先检查容易变化的信息，或根据读取频率调整回顾节奏。

还可以把会话记录搜索作为记忆的基础。Wiki 等表示有时能与搜索配合得很好，但维护这些表示、避免其中累积错误和幻觉，仍要消耗算力。

Claude 对信息重要性的判断已有改善，但未来会发生什么仍无法预知。离线回顾给了 Claude 回看经历的机会，让它用算力整理记忆、改正错误，并维护便于后续会话访问的表示。记忆系统会随着 Claude 的能力演进，怎样设计这样的系统还有很多值得学习。

可参阅原文附带的[离线回顾](https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow)与[知识 Wiki](https://github.com/anthropics/claude-quickstarts/tree/main/managed-agents/knowledge-wiki)上手资料。

## 作者与致谢

Lance Martin 撰写本文，Caitlin Love、Tom Chivers、Rebecca Hiscott、Jake Eaton 和 Blake Wilson 提供编辑指导。感谢 Barry Zhang、Theodora Chu、Daliang Li、Mahesh Murag、Jake Noble、Ravi Trivedi、Tina Vachovsky、Brad Abrams、Henry de Valence、Jeremy Fox、Matt Bell、Allen Li、Chris Gorgolewski、Eugene Yan、Artur Renault、Wei Zhang 和 Kevin Chen 的讨论与贡献，以及 David Hershey 对 Claude 玩《宝可梦》的支持。插图由 Monika Tuchowska 绘制。
