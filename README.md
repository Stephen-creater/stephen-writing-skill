# Stephen Writing Skill

Stephen 在「日课创作」项目里维护的中文写作 Skill：把文章、链接、截图、逐字稿和资料，写成 AI 热点、产品体验、概念拆解和实践指南类的日课文章，写给对 AI 感兴趣但不熟悉术语的普通读者。

## 它怎么工作

1. 写稿的 Agent 读写作指南、所属分类的说明和一两篇范文，按 Stephen 这次的要求写初稿。
2. 另开一个 Agent 按审稿指南找问题，写稿的 Agent 按意见改一轮。
3. 初稿交给 Stephen，他自己动手改成发布版。
4. Stephen 给出定稿后，对比初稿和定稿，只把反复出现的修改写进规则。
5. 每次改规则，都在固定题库上和旧版本盲评对比，通过才上线。

## 文件

| 文件 | 给谁看 | 干什么 |
|---|---|---|
| `SKILL.md` | 写稿 Agent | 要读什么、写作步骤、规则冲突时听谁的 |
| `references/writing.md` | 写稿 Agent、审稿 Agent | Stephen 怎么取舍、怎么讲、用什么语气，每条附一个真实例子 |
| `references/review.md` | 审稿 Agent | 逐项检查什么、怎么写审稿意见 |
| `references/learning.md` | 改 Skill 的 Agent | 怎么从 Stephen 的定稿里学，什么修改才进规则 |
| `references/evaluation.md` | 改 Skill 的 Agent、Stephen | 评测怎么设计、怎么跑、上线标准、怎么恢复旧版本 |
| `examples/<分类>/standards.md` | 写稿 Agent | 这一类文章写给谁、常见写法、容易出错的地方、推荐范文 |
| `examples/<分类>/*.md` | 写稿 Agent | Stephen 确认过的定稿 |
| `scripts/check_style.py` | 审稿 Agent | 数出双引号、破折号、先否定再肯定的句式，偏多时报错 |
| `scripts/eval_writing.py` | 改 Skill 的 Agent | 准备评测任务、汇总盲评结果、记录历史、恢复旧版本 |

## 版本管理

权威维护源是父项目里的 `./stephen-writing-skill/`。更新先提交父项目的 Git，再用父项目的 `scripts/push_stephen_writing_skill.py` 同步到公开仓库 [Stephen-creater/stephen-writing-skill](https://github.com/Stephen-creater/stephen-writing-skill)。通过评测的版本打 `writing-v*` 标签，可以随时恢复。
