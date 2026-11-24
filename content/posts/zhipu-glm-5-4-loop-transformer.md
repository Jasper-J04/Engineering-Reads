Title: GLM‑5.4 如何重复使用 Transformer 层
Slug: zhipu-glm-5-4-loop-transformer
Date: 2026-11-24T17:22:45+08:00
Summary: 用共享权重、逐 token 门控和 KV 缓存三个概念，读懂智谱公布的 Loop Transformer 设计。
Tags: ai, architecture, performance
Source: zhipu-research
Source_url: https://www.zhipuai.cn/zh/research/164
Source_title: GLM-5.4：瞄向泛Coding，首个Loop Transformer带来的惊喜
Kind: digest
Source_date: 2026-11-22

智谱用「瞄向泛 Coding」概括 GLM‑5.4 的方向，并以视频、3D、游戏等场景说明代码怎样驱动其他产出。理解这篇发布文的技术部分，可以从作者的核心表述入手：「Loop Transformer 可以让一组共享权重的层循环执行」。原文作者将 GLM‑5 基座中的 28 层运行两轮。

## 什么是把一组层再跑一次

Transformer 的一层会根据已读到的信息更新 token 的内部表示。典型模型逐层运行，每层有各自的权重。循环层会把第一轮输出送回同一组权重处理。相同参数做第二次计算可以精炼结果，计算时间仍应计入推理成本。

## 智谱公布的三个实现选择

1. **门控渐进更新。** 每轮为每个 token 计算写回比例。原文描述的训练结果中，多数位置第一轮更侧重建立上下文，第二轮在此基础上精炼。门控也能对较难预测的位置调整写入力度。
2. **全局复用 KV，局部保留新 KV。** KV 缓存保存注意力读取此前 token 时可复用的数据。第二轮复用第一轮为长距离注意力选出的缓存，并保留近邻滑动窗口内第二轮的新缓存。这样能获得局部更新，又不必给每一轮准备完整长上下文缓存。
3. **复用稀疏注意力索引。** 稀疏注意力只挑选一部分位置参与计算。第二轮复用第一轮已挑出的位置，节省再算索引的代价。原文报告，在作者的实验里，这种复用与每轮重新计算的效果接近。

## 如何读原文的性能结论

参数、显存、算力衡量不同成本。共享权重限制了参数增长，缓存和索引复用减少了额外资源需求，第二轮的计算仍然存在。对照原图或评测时，应同时关注上下文长度、任务类型与推理条件。

## 原文插图

- [GLM‑5.4 发布首图](<https://www.zhipuai.cn/api/media/file/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20261123150241_492_40.jpg>)
- [原文第二张插图](<https://www.zhipuai.cn/api/media/file/c1b61892-d25a-461d-8789-31315d77de15.png>)
- [原文第三张插图](<https://www.zhipuai.cn/api/media/file/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20261123163301_500_40.jpg>)
