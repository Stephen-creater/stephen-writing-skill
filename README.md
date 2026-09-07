# Stephen Writing Skill

这是 Stephen 在「日课创作」项目中维护的个人中文写作 Skill。它用于把文章、链接、截图、逐字稿、研究材料和人工反馈编辑成高信息密度的 AI 热点、产品体验、概念方法与实践指南。

## 它解决什么

这个 Skill 的核心不是复刻几个句式，而是稳定完成四个编辑判断：

1. 标题到底承诺读者获得什么。
2. 哪条主路径能让读者抵达这个终点。
3. 哪些内容即使正确也必须删除。
4. 怎样保留 Stephen 的判断站位与自然中文，同时不伪造经历和事实。

## 信息架构

- `SKILL.md`：任务路由、规则优先级、核心工作流和硬边界。
- `references/editorial_decisions.md`：跨题材的编辑决策系统。
- `references/voice.md`：Stephen 稳定的作者声音与中文表达习惯。
- `references/check_standards.md`：交付前的硬检查表。
- `references/feedback_learning.md`：用户交付定稿或审核反馈时，如何避免补丁式更新。
- `examples/*/standards.md`：每类文章独有的结构选择与代表案例。
- `examples/`：用户确认的最终案例，不自动充当事实来源。
- `scripts/check_style.py`：标点与高频模型句式检查。
- `scripts/save_draft.py`：用户确认定稿后的归档辅助脚本。

## 使用方式

每次写作先完整读取 `SKILL.md`，再按其中的渐进式路由读取核心 references、一个分类标准和一至两篇最接近的案例。不要一次加载全部案例。

初稿默认写入父项目 `work/`。只有用户确认定稿或明确要求更新 Skill 后，才进入案例库并更新规则。

## 反馈如何进入 Skill

未来的反馈不再直接变成新禁令。先比较模型稿、用户定稿和审核原话，再判断根因、作用域与反例。能由现有高阶原则解释的反馈只更新案例；确实暴露规则缺口时，优先替换或合并旧规则，不在多个文件重复追加。

## 质量底线

- 不伪造亲历、实测、采访、业务结果和数据。
- 当前用户要求高于旧案例与默认比例。
- 标题、读者、主路径与结尾必须指向同一终点。
- 信息密度按有效增量与阅读成本判断，不按字数和术语数量判断。
- 面向小白时降低无关门槛，但不牺牲核心机制。
- 正文默认不用双引号，必要时只用「」；尽量不用破折号和翻案句。

## 版本管理

权威维护源是父项目中的 `./stephen-writing-skill/`。Skill 更新先提交父项目 Git，再由 `scripts/push_stephen_writing_skill.py` 同步到公开仓库 [Stephen-creater/stephen-writing-skill](https://github.com/Stephen-creater/stephen-writing-skill)。其他同名安装副本不作为编辑源。
