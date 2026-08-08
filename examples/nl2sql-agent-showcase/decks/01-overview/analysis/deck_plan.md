# Deck Plan

## Context

- deck_id: 01-overview
- title: NL2SQL Agent：从自然语言到可信 SQL
- profile: technical
- audience: AI 应用工程师、后端工程师、技术评审者
- presentation_context: 开源项目介绍与架构说明
- source_scope: repository README, implementation plan, core contracts, orchestrator, gate, executor, judge, refiner, and tests
- target_page_count: 12
- language: zh-CN
- approval_mode: automatic

## Outcomes

- Primary communication outcome: 说明该项目如何把一次性 SQL 生成改造成可验证、有界修复的状态机。
- Audience action or understanding: 能区分 Gate、数据库执行、Judge 与 Refiner 的职责边界。
- Verified boundary: 当前 WSL 隔离依赖环境下 25 项测试通过；未运行真实模型与 BIRD benchmark。

## Page Plan

| Page | Title | Purpose | Key content | Source | Density | Layout family | Visual need | Visual route | Risk | Scene profile |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | NL2SQL Agent：从自然语言到可信 SQL | 开场定位 | 确定性安全 Gate + 有界语义修复 | README, source | anchor | cover | helpful | generated | low | conceptual |
| 2 | 单次生成解决不了“可信”问题 | 建立问题 | 意图偏差、执行风险、语义错误三类失效 | source synthesis | breathing | thesis | helpful | generated | low | conceptual |
| 3 | 系统把生成拆成一条可追踪流水线 | 总览架构 | SchemaLinker 到 Refiner 的主链路 | README, orchestrator | anchor | process | required | native | low | technical |
| 4 | Builder 输出的是可质疑的合同 | 解释合同 | SQLArtifact、DraftIntent、版本化修订 | contracts, builder | dense | evidence | helpful | native | low | technical |
| 5 | Gate 只阻断高确定性风险 | 解释边界 | 只读、单语句、解析、占位符、授权 Schema | gate, plan | dense | comparison | required | native | medium | technical |
| 6 | SafeExecutor 先分清“没执行”和“执行失败” | 解释执行 | Gate block、DB failure、DB success 三种路径 | executor | anchor | process | required | native | medium | technical |
| 7 | Judge 只在执行成功后使用语义 LLM | 解释成本与职责 | gate/database deterministic；semantic LLM | judge, plan | dense | comparison | helpful | native | medium | technical |
| 8 | Refiner 的修复循环有明确上限 | 解释有界修复 | 2/2/5 repair budgets、总 10 次、1 次补 Schema | orchestrator | dense | evidence | required | native | medium | technical |
| 9 | 停止条件比“多试几次”更重要 | 防止死循环 | duplicate SQL、重复 fingerprint、预算耗尽 | orchestrator, tests | breathing | process | helpful | native | low | technical |
| 10 | 没有执行器时，结果只能叫 generated_unverified | 强调可信状态 | success=false；只有 semantic PASS 才 success | README, orchestrator, tests | anchor | comparison | required | native | low | technical |
| 11 | 当前回归集验证了关键边界 | 展示证据 | 25 tests passed；覆盖 Gate、executor、Judge、retry、artifact | current pytest | dense | evidence | helpful | native | low | technical |
| 12 | 可信 SQL 不是“生成出来”，而是“验证出来” | 收束 | 已验证保证与未验证模型效果边界 | source synthesis | anchor | close | unnecessary | none | low | |
