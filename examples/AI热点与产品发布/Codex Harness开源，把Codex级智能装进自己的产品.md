# Codex Harness开源，把Codex级智能装进自己的产品

OpenAI 已经正式开源 Codex Harness，开发者可以使用 Codex SDK 和 Codex App Server，快速搭建专属智能体。

## 一、开放Harness的好处？

统一的通用智能体，比如 Codex App，虽然很好用，但作为一个闭源的封装产品，无法满足定制化智能体开发需求。

对于大多数传统的 Agent 开发框架（比如 LangChain）来说，仍然还停留在把工具组装成一个 Agent 的层面。但一个真正能在工作区里长时间干活的 Agent，需要的是最好的 Harness。

Harness 是模型周围的整套执行系统。它需要理解任务、持续维护上下文、检查资料、调用工具、暴露进度、处理失败、申请人类审批，最后返回可用结果。

而 Agent = Model + Harness，模型层面除了使用 GPT 5.6 sol、Claude opus 5 级别的世界第一梯队模型外，Harness 的版本答案一直是 Claude Code 和 Codex，前者最新版本仍是闭源，此次 Codex Harness 开源后，我们拥有了研究和使用当下 Harness 领域最强版本答案的机会。

## 二、Codex SDK和App Server有什么区别？

开源的两个核心入口，分别是 Codex SDK 和 Codex App Server。

Codex SDK 适合快速完成自动化调用。它可以在程序中启动、继续和恢复 Codex 线程，并消费流式事件。如果是脚本、CI 任务、后台工作流，或者想把 Codex 放进现有的应用代码中，可以先用 SDK。

官方的 TypeScript 版可以直接安装 `@openai/codex-sdk`，Python 版则是 `openai-codex`。基础调用只需创建 Codex、启动 Thread，然后运行 Prompt。

Codex App Server 适合更复杂的产品级集成。它通过 JSON-RPC 暴露线程、回合、事件、工具、审批和生命周期能力，应用可以创建或恢复对话，启动新回合，实时接收模型消息、命令运行、文件变更和工具调用事件，还能处理需要人确认的操作。

你可以把 Codex SDK 理解成快速调用 Codex 服务的编程接口，而 Codex App Server 负责维持 Codex Harness 更底层功能的持久化运行。

总而言之，以后再做自己的 Agent 产品，不必从 0 搭建，也不必参考大多数落后的架构，不妨直接从 Codex Harness 这套版本答案开始尝试。
