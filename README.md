# Stephen Writing Skill

这是 Stephen 在“日课创作”项目内持续维护和使用的个人写作 Skill。它用于根据 Stephen 的既有文章风格，撰写、整合和修改 AI 热点、产品评测、概念解释与实践指南。

## 最重要的写作原则

- 标题规定文章最终抵达的位置。
- 全文只走一条因果链，每一节回答上一节留下的问题。
- 正确、精彩、信息量大的内容，也可能因为不推动主线而被整节删除。
- 一个意思只说一次，换一种表述仍然算重复。
- Aha moment 由正文的逻辑闭合产生，结尾不临时制造高潮。

## 目录

- `SKILL.md`：AI 使用的入口、分类路由和工作流程。
- `references/voice.md`：作者的语气、解释方式、论证习惯和节奏。
- `references/check_standards.md`：交付前必须执行的检查标准。
- `examples/`：按文章类型分类的定稿案例与分类标准。
- `scripts/save_draft.py`：用户确认定稿后使用的存档脚本。

## 建议阅读顺序

1. 先读 `SKILL.md` 的“最高优先级”和工作流。
2. 再读 `references/voice.md` 与 `references/check_standards.md`。
3. 根据要写的文章类型，只读对应分类的 `standards.md` 和一至两篇最终案例。

## 原文整合

用户授权整合原文时，连续 30 字覆盖率以 80% 为正常验收线。70% 只用于修正事实、补齐缺失图片信息或维持完整逻辑等确有必要的情况，不能作为默认写作目标。

## 版本管理

Skill 的更新先在“日课创作”项目 Git 仓库中提交，再运行项目维护脚本，同步到公开仓库 `Stephen-creater/stephen-writing-skill`。未经确认的初稿保留在项目 `work/` 目录，不直接进入案例库。

本地项目中的公开同步命令：

```bash
python3 scripts/push_stephen_writing_skill.py
```
