---
schema: ppt-series-execution-lock.v2
scope: deck-snapshot
generated_snapshot: true
generated_at: "2026-08-08T08:07:26.954458+00:00"
deck_id: "01-overview"
parent_lock: "../../series/spec_lock.md"
parent_version: "2"
parent_sha256: "933cda4ec6d13936d167d19e22681161ec4c85b9e271ddf75fbcfce6775fc6cb"
deck_plan: "analysis/deck_plan.md"
deck_plan_sha256: "317385519c6e45baa82f339d007a3acc0a2c132470bbfd3172d76f80f0bb2f0c"
deck_overrides: "analysis/deck_overrides.md"
deck_overrides_sha256: "d346593e2aa1fce9d4c1e1276c97cd5c2db842d0e05e5920a0e33180f5aba061"
---

# Deck Execution Lock

Do not edit this generated snapshot. Edit the series lock, deck plan, or deck overrides, then
regenerate it with `sync_deck_spec.py --force`.

## Deck Plan

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

## Deck Overrides

# Deck Overrides

- approval_mode: automatic
- image_backend: host-imagegen
- max_generated_assets: 2
- max_candidates_per_task: 4
- max_generation_attempts_per_asset: 2
- allow_semantic_user_image_edits: false
- allow_high_risk_schematic_generation: false
- visible_ai_disclosure_for_schematic: true
- notes: End-to-end acceptance demo; generated illustration is limited to the cover.

## Inherited Series Lock

---
schema: ppt-series-lock.v2
scope: series
state: draft
version: 2
origin:
  type: context-derived
  source: NL2SQL Agent repository
  extraction_scope: local source and tests
  fidelity: designed
profile: technical
---

# NL2SQL Agent Showcase Series Lock

## Identity

- series_name: NL2SQL Agent Showcase
- audience: AI application engineers, backend engineers, and technical reviewers
- presentation_context: open-source project introduction and architecture walkthrough
- language: Simplified Chinese with English identifiers retained
- tone: precise, confident, keynote-ready

## Canvas And Grid

- aspect_ratio: 16:9
- canvas: 1280 x 720 px
- safe_margin: 42 px
- grid: 12 columns
- title_zone: top 88 px
- footer_zone: bottom 34 px
- source_layout_system: custom data-flow keynote system

## Typography

- title_font: Arial
- body_font: Arial
- cjk_fallback: Microsoft YaHei
- deck_title: 52-60 pt
- slide_title: 34-40 pt
- body: 18-24 pt
- annotation: 11-14 pt
- letter_spacing: 0

## Color Roles

- canvas: "#F7F9FC"
- ink: "#0B0F14"
- secondary_text: "#526171"
- dark_stage: "#0B0F14"
- dark_panel: "#151D27"
- rule: "#B9C2CC"
- accent: "#45D0FF"
- accent_strong: "#2E7CF6"
- success: "#42B883"
- warning: "#F5A340"
- danger: "#FF6B5E"

## Layout Families

- cover: near-black title stage and bright focal illustration
- thesis: full-width conceptual visual with editable caption rail
- process: dark-stage data-flow sequence with explicit stage labels
- comparison: full-width contrasting bands, not floating cards
- evidence: code, terminal, table, or test result as the dominant surface
- close: dark keynote synthesis with one electric-cyan statement

## Illustration System

- base_style: premium editorial 3D technical illustration with translucent data forms
- scene_profiles: conceptual, technical
- palette_binding: near-black, ice white, electric cyan, strong blue, restrained coral
- generated_image_role: conceptual comprehension aid only; never factual evidence
- editable_overlay_rule: all labels and arrows remain editable in PowerPoint
- disclosure_rule: provenance in notes; visible disclosure only if the image could be mistaken for evidence
- prohibited: embedded text, logos, fake UI, fake query results, unsupported metrics, dark gradients

## Invariants

- Alternate light analysis pages with near-black keynote stages; do not run more than three identical silhouettes consecutively.
- Use electric cyan for flow and coral only for hazards; keep status green and warning amber semantically stable.
- Keep every system label and connector editable.
- Use repository files and current test output as the factual source.
- State unverified model and benchmark boundaries explicitly.

## Allowed Variation

- Vary silhouette by narrative role.
- Use generated illustrations only on the cover and conceptual failure framing; factual architecture remains native and editable.
- Use native shapes, tables, and code blocks for architecture and evidence.
