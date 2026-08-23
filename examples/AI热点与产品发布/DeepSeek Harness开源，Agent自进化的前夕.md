# DeepSeek Harness开源，Agent自进化的前夕

DeepSeek Harness（DSH）发布的是一套可以热重载的 harness，并且设计成适合 coding agent 自己去修改、进化的形态。这个发布思路很有野心，没有在白领工作、coding agent 这些方向去和 Claude Code、Codex、WorkBuddy 竞争产品，而是延续了他们一以贯之的思路：开源、infra 化。

## 一、DSH这次发布了什么？

从产品表面看，DeepSeek Harness（DSH）是一个带本地 Web UI 的 Coding Agent。

但我们可以把这次发布分为三层去拆解。

第一层是 Coding Agent。DSH 没有把 Terminal-first TUI 或桌面端作为主要产品形态，而是选择了更像开发者 Demo 的本地 Web UI。标准模式已经包含真实编程工作需要的主要能力，包括执行命令、修改和搜索文件、调用 Skills、维护计划与目标、启动子代理，以及运行工作流。系统还提供 Context Compaction、会话持久化、Sandbox 和权限审批。

第二层是 everything-is-a-plugin 的 harness 构造框架。Model Adapter、Tool Registry、Sandbox Policy、Subagent Backend，甚至默认 Agent Loop，都可以由 Cordis Plugin 提供。开发者因此可以替换一个能力的 Provider，同时尽量保持其他组件不变。

第三层是 Cordis meta-framework。Cordis 进一步解决的是：这些组件怎样加入、删除和重新组合，能够不把正在运行的系统破坏掉。

## 二、Cordis怎么让Harness活起来？

多数 Agent 插件系统主要关心怎样增加功能：安装更多 Tool、Skill 和 MCP。但组件不断增加后，系统也会积累更多 Tool Schema 和依赖关系。模型需要在更多能力之间进行选择，很多人在 Claude Code 中遇到过 Skills 过多后反而效果变差的情况。

这里可以把这种现象理解为一种工程上的“熵增”：系统不断增加能力，却缺少对应的删除和重组机制。这也是 Cordis 论文《A Programming Paradigm for Spatiotemporal Composability》讨论的核心问题。论文把插件的动态组合拆成两个相互独立的维度来解决。

时间可组合性 Temporal Composability，是解决处理组件的退出。

一个 Plugin 加载时，可能注册 Tool、Prompt Section、Event Listener、Timer 和 Service。如果只删除插件代码，这些已经进入 Runtime 的状态可能继续存在，形成无法正常清理的“幽灵组件”。Cordis 要求组件在注册 Effect 时，同时提供对应的撤销方式。组件卸载后，Runtime 会撤销它在 Context 中留下的 Effect。

空间可组合性 Spatial Composability，处理组件之间的依赖。

组件不直接绑定某个实现，而是声明自己需要什么 Service。当依赖尚未出现时，组件保持 Waiting；依赖满足后，组件进入 Active；正在使用的 Service 消失或被替换后，组件先撤销自己的 Effect，再根据新的依赖关系重新激活。

这也是插件化的真正意义。它不仅方便开发者扩展功能，也把原本开放式的软件修改，变成了一组边界更明确的操作。Agent 不需要重写整个系统，而是可以尝试替换任何一个组件。如果实验失败，系统还可以卸载插件并恢复原来的组合。自我修改因此从一次高风险的整体重写，变成一系列可以测试和回滚的局部实验。

## 三、它距离真正的self-evolve还有多远？

当前 DSH 的产品形态更像开发者预览版，不是面向普通用户的成熟 Coding Agent，而是把主要精力放在一个可以被深度修改的 Runtime 上。

DSH 虽提供了 agent runtime self-modification 的底座，但距离真正的 self-evolve 缺少一个完整的学习闭环，需要有 Learning Loop 来学习并提出修改、Eval 评估修改的有效性。因此当前其实是 Harness-level RSI 的第一步，自身拆成可定位、可替换的组件。

目前 Cordis 解决的主要仍是“Harness 能否被更可控地调整”。它不知道为什么应该替换 Agent Loop，也不能判断新 Loop 是否真正提高了整体能力。它提供了运行和管理候选方案的底座，却没有完成问题诊断和效果的自动化评估。

总而言之，DSH有点像一艘持续航行的忒修斯之船，Agent能够一边执行任务，一边更换支撑自身运行的部件。但真正重要的是每次更换之后，它是否能航行更快，以及判断下一次应该更换什么。
