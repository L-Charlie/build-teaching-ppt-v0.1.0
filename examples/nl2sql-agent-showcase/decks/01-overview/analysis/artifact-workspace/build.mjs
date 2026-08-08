import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const artifactEntry = process.env.CODEX_ARTIFACT_TOOL_ENTRYPOINT || path.join(
  process.env.USERPROFILE || process.env.HOME || "",
  ".cache",
  "codex-runtimes",
  "codex-primary-runtime",
  "dependencies",
  "node",
  "node_modules",
  "@oai",
  "artifact-tool",
  "dist",
  "artifact_tool.mjs",
);
if (!artifactEntry || !path.isAbsolute(artifactEntry)) {
  throw new Error("Set CODEX_ARTIFACT_TOOL_ENTRYPOINT to artifact_tool.mjs");
}
const { Presentation, PresentationFile } = await import(pathToFileURL(artifactEntry).href);

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DECK_ROOT = path.resolve(HERE, "..", "..");
const OUTPUT_DIR = path.join(DECK_ROOT, "exports");
const RENDER_DIR = path.resolve(HERE, "..", "rendered");
const LAYOUT_DIR = path.resolve(HERE, "..", "layouts");
const COVER_IMAGE = path.join(DECK_ROOT, "images", "generated", "VIS-001.png");
const FAILURE_IMAGE = path.join(DECK_ROOT, "images", "generated", "VIS-002.png");

const C = {
  canvas: "#F7F9FC",
  ink: "#0B0F14",
  secondary: "#526171",
  panel: "#E8EDF3",
  panelLight: "#F0F3F7",
  rule: "#B9C2CC",
  dark: "#0B0F14",
  darkPanel: "#151D27",
  darkRule: "#314052",
  accent: "#45D0FF",
  accentStrong: "#2E7CF6",
  success: "#42B883",
  warning: "#F5A340",
  danger: "#FF6B5E",
};
const FONT = "Microsoft YaHei";
const MONO = "Courier New";

function addText(slide, name, text, frame, size = 24, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: frame,
    fill: options.fill ?? "none",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: size,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    typeface: options.typeface ?? FONT,
    alignment: options.alignment ?? "left",
    verticalAlignment: options.verticalAlignment ?? "top",
    autoFit: options.autoFit ?? "shrinkText",
  };
  return shape;
}

function addBox(slide, name, frame, options = {}) {
  const geometry = options.geometry ?? "rect";
  const config = {
    geometry,
    name,
    position: frame,
    fill: options.fill ?? C.panel,
    line: options.line ?? { style: "solid", fill: C.rule, width: 1 },
  };
  if (["rect", "textbox", "roundRect"].includes(geometry)) {
    config.borderRadius = options.borderRadius ?? 0;
  }
  return slide.shapes.add(config);
}

function addRule(slide, name, left, top, width, color = C.rule, thickness = 1) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height: thickness },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function addTitle(slide, title, page, eyebrow = "NL2SQL AGENT", dark = false) {
  addText(slide, `eyebrow-${page}`, eyebrow, { left: 42, top: 32, width: 260, height: 26 }, 13, {
    bold: true,
    color: C.accentStrong,
  });
  addText(slide, `title-${page}`, title, { left: 42, top: 67, width: 1125, height: 74 }, 38, {
    bold: true, color: dark ? C.canvas : C.ink,
  });
  addRule(slide, `title-rule-${page}`, 42, 150, 1196, dark ? C.darkRule : C.rule, 1);
}

function addFooter(slide, page, dark = false) {
  addText(slide, `footer-brand-${page}`, "BUILD-PPT-SERIES / E2E DEMO", {
    left: 42, top: 670, width: 340, height: 18,
  }, 10, { color: dark ? "#8FA0B2" : C.secondary, verticalAlignment: "bottom" });
  addText(slide, `footer-page-${page}`, String(page).padStart(2, "0"), {
    left: 1188, top: 666, width: 50, height: 22,
  }, 12, { bold: true, color: dark ? C.canvas : C.ink, alignment: "right", verticalAlignment: "bottom" });
}

function addNotes(slide, sources, note = "") {
  const lines = ["[Sources]", ...sources.map((source) => `- ${source}`)];
  if (note) lines.push("", note);
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function stageNode(slide, x, y, w, h, title, detail, index, accent = false, dark = false, titleSize = 20) {
  addBox(slide, `stage-${index}`, { left: x, top: y, width: w, height: h }, {
    fill: accent ? "#102C42" : (dark ? C.darkPanel : C.panelLight),
    line: { style: "solid", fill: accent ? C.accent : (dark ? C.darkRule : C.rule), width: accent ? 2 : 1 },
    borderRadius: 8,
  });
  addText(slide, `stage-num-${index}`, String(index).padStart(2, "0"), {
    left: x + 14, top: y + 12, width: 40, height: 22,
  }, 12, { bold: true, color: accent ? C.accent : (dark ? "#8FA0B2" : C.secondary) });
  addText(slide, `stage-title-${index}`, title, {
    left: x + 14, top: y + 42, width: w - 28, height: 34,
  }, titleSize, { bold: true, color: dark ? C.canvas : C.ink });
  addText(slide, `stage-detail-${index}`, detail, {
    left: x + 14, top: y + 82, width: w - 28, height: h - 94,
  }, 13, { color: dark ? "#A9B6C4" : C.secondary });
}

function addArrow(slide, name, x, y, width, color = C.accentStrong) {
  return slide.shapes.add({
    geometry: "rightArrow",
    name,
    position: { left: x, top: y, width, height: 18 },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function addBulletList(slide, name, items, frame, options = {}) {
  const text = items.map((item) => `• ${item}`).join("\n");
  return addText(slide, name, text, frame, options.size ?? 20, {
    color: options.color ?? C.ink,
    bold: options.bold ?? false,
  });
}

function createSlide(presentation, dark = false) {
  const slide = presentation.slides.add();
  slide.background.fill = dark ? C.dark : C.canvas;
  return slide;
}

async function buildDeck() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.mkdir(RENDER_DIR, { recursive: true });
  await fs.mkdir(LAYOUT_DIR, { recursive: true });
  const coverBytes = await fs.readFile(COVER_IMAGE);
  const failureBytes = await fs.readFile(FAILURE_IMAGE);
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 01 Cover: technical keynote split stage with a concrete generated asset.
  {
    const slide = createSlide(presentation);
    addBox(slide, "cover-dark-stage", { left: 0, top: 0, width: 610, height: 720 }, {
      fill: C.dark, line: { style: "solid", fill: C.dark, width: 0 },
    });
    addRule(slide, "cover-stage-edge", 607, 0, 5, C.accent, 720);
    addText(slide, "cover-kicker", "NL2SQL AGENT / ARCHITECTURE OVERVIEW", {
      left: 42, top: 42, width: 520, height: 28,
    }, 13, { bold: true, color: C.accent });
    addText(slide, "cover-title", "从自然语言\n到可信 SQL", {
      left: 42, top: 155, width: 560, height: 180,
    }, 56, { bold: true, color: C.canvas, verticalAlignment: "bottom" });
    addText(slide, "cover-subtitle", "确定性安全 Gate\n+ 有界 Judge / Refiner 修复闭环", {
      left: 42, top: 380, width: 500, height: 100,
    }, 24, { color: "#A9B6C4" });
    addRule(slide, "cover-accent-rule", 42, 522, 116, C.danger, 5);
    addText(slide, "cover-meta", "Open-source project showcase · Technical profile", {
      left: 42, top: 548, width: 520, height: 32,
    }, 13, { color: "#8FA0B2" });
    slide.images.add({
      blob: coverBytes,
      contentType: "image/png",
      alt: "Conceptual illustration of language passing through a gate into a database",
      fit: "contain",
      position: { left: 636, top: 40, width: 602, height: 610 },
    });
    addFooter(slide, 1);
    addNotes(slide, ["README.md", "Generated asset VIS-001; prompt recorded in analysis/prompts/VIS-001.txt"]);
  }

  // 02 Three failure zones.
  {
    const slide = createSlide(presentation, true);
    addTitle(slide, "单次生成解决不了“可信”问题", 2, "WHY A STATE MACHINE", true);
    slide.images.add({
      blob: failureBytes,
      contentType: "image/png",
      alt: "Conceptual illustration of intent drift, execution risk, and semantic mismatch",
      fit: "cover",
      position: { left: 42, top: 178, width: 1196, height: 360 },
    });
    addBox(slide, "failure-caption-band", { left: 42, top: 530, width: 1196, height: 96 }, {
      fill: "#101722", line: { style: "solid", fill: C.darkRule, width: 1 },
    });
    const items = [
      ["01", "意图偏差", "问题理解错，SQL 却自洽"],
      ["02", "执行风险", "危险查询必须在库前拦截"],
      ["03", "语义错误", "可执行仍不等于答对"],
    ];
    items.forEach(([num, title, body], i) => {
      const x = 62 + i * 392;
      addText(slide, `failure-num-${i}`, num, { left: x, top: 550, width: 44, height: 24 }, 13, {
        bold: true, color: i === 1 ? C.danger : C.accent,
      });
      addText(slide, `failure-title-${i}`, title, { left: x + 48, top: 545, width: 120, height: 34 }, 22, {
        bold: true, color: C.canvas,
      });
      addText(slide, `failure-body-${i}`, body, { left: x + 48, top: 582, width: 300, height: 28 }, 15, {
        color: "#A9B6C4",
      });
    });
    addFooter(slide, 2, true);
    addNotes(slide, [
      "README.md",
      "SafeExecutor_Gate_implementation_plan.md",
      "Generated asset VIS-002; prompt recorded in analysis/prompts/VIS-002.txt",
    ]);
  }

  // 03 End-to-end architecture.
  {
    const slide = createSlide(presentation, true);
    addTitle(slide, "系统把生成拆成一条可追踪流水线", 3, "SYSTEM OVERVIEW", true);
    addText(slide, "flow-backdrop-index", "06 STAGES / 01 EXECUTION ENVELOPE", {
      left: 44, top: 190, width: 520, height: 32,
    }, 16, { bold: true, color: "#8FA0B2" });
    const xs = [44, 245, 446, 647, 848, 1049];
    for (let i = 0; i < xs.length - 1; i += 1) {
      addArrow(slide, `flow-arrow-${i + 1}`, xs[i] + 165, 344, 28);
    }
    const stages = [
      ["SchemaLinker", "检索表、列与 FK"],
      ["DataSampler", "探查真实列值"],
      ["Builder", "SQLArtifact + DraftIntent"],
      ["SafeExecutor", "Gate → 只读执行"],
      ["Judge", "确定性 / 语义核查"],
      ["Refiner", "分阶段有界修复"],
    ];
    stages.forEach(([title, detail], i) => {
      stageNode(slide, xs[i], 255, 165, 205, title, detail, i + 1, i === 3, true, i === 1 ? 17 : 20);
    });
    addText(slide, "flow-loop-label", "任何修复后的 SQL 都重新进入 SafeExecutor", {
      left: 420, top: 520, width: 440, height: 42,
    }, 18, { bold: true, alignment: "center", color: C.accentStrong });
    addRule(slide, "flow-loop-line", 305, 580, 670, C.accentStrong, 3);
    addFooter(slide, 3, true);
    addNotes(slide, ["README.md", "agent_team/orchestrator.py"]);
  }

  // 04 SQLArtifact contract.
  {
    const slide = createSlide(presentation);
    addTitle(slide, "Builder 输出的是可质疑的合同", 4, "CHALLENGEABLE CONTRACT");
    addBox(slide, "contract-code-panel", { left: 42, top: 190, width: 600, height: 420 }, {
      fill: "#11181F",
      line: { style: "solid", fill: "#11181F", width: 0 },
      borderRadius: 8,
    });
    const code = [
      "SQLArtifact(",
      "  sql = \"SELECT ...\",",
      "  draft_intent = DraftIntent(",
      "    metrics = [...],",
      "    filters = [...],",
      "    aggregation_grain = \"...\"",
      "  ),",
      "  intent_version = 1",
      ")",
    ].join("\n");
    addText(slide, "contract-code", code, { left: 72, top: 222, width: 540, height: 350 }, 18, {
      typeface: MONO, color: "#EAF5FB",
    });
    addText(slide, "contract-right-title", "为什么不是“真值”", {
      left: 700, top: 214, width: 480, height: 48,
    }, 28, { bold: true });
    addBulletList(slide, "contract-bullets", [
      "原问题与证据仍是根约束",
      "Judge 可以质疑 DraftIntent",
      "Refiner 修订意图时必须升级版本",
      "修订理由被记录，不能静默覆盖",
    ], { left: 700, top: 294, width: 490, height: 230 }, { size: 20 });
    addText(slide, "contract-takeaway", "合同让“理解错了什么”也能被定位。", {
      left: 700, top: 548, width: 480, height: 48,
    }, 21, { bold: true, color: C.accentStrong });
    addFooter(slide, 4);
    addNotes(slide, ["agent_team/contracts.py", "agent_team/builder.py", "SafeExecutor_Gate_implementation_plan.md"]);
  }

  // 05 Gate boundary.
  {
    const slide = createSlide(presentation);
    addTitle(slide, "Gate 只阻断高确定性风险", 5, "DETERMINISTIC PRE-EXECUTION");
    addText(slide, "gate-subtitle", "能确定“不安全或不可执行”的才阻断；语义好坏留给执行后的 Judge。", {
      left: 42, top: 180, width: 1120, height: 50,
    }, 22, { color: C.secondary });
    addBox(slide, "gate-block-panel", { left: 42, top: 270, width: 560, height: 330 }, {
      fill: "#EAF5FB", line: { style: "solid", fill: C.accentStrong, width: 2 }, borderRadius: 8,
    });
    addText(slide, "gate-block-title", "BLOCK", { left: 72, top: 294, width: 180, height: 38 }, 18, {
      bold: true, color: C.accentStrong,
    });
    addBulletList(slide, "gate-block-list", [
      "非只读或多语句 SQL",
      "AST 解析失败",
      "未解析的模板占位符",
      "引用授权 Schema 之外的表",
      "高确定性不存在的列",
    ], { left: 72, top: 350, width: 480, height: 210 }, { size: 20 });
    addBox(slide, "gate-observe-panel", { left: 638, top: 270, width: 600, height: 330 }, {
      fill: C.panelLight, line: { style: "solid", fill: C.rule, width: 1 }, borderRadius: 8,
    });
    addText(slide, "gate-observe-title", "OBSERVE → JUDGE", { left: 670, top: 294, width: 260, height: 38 }, 18, {
      bold: true, color: C.secondary,
    });
    addBulletList(slide, "gate-observe-list", [
      "聚合函数与结果粒度",
      "JOIN 结构与过滤条件",
      "时间范围与排序",
      "Top-N 与 required concepts",
      "SQL signature 作为语义证据",
    ], { left: 670, top: 350, width: 510, height: 210 }, { size: 20, color: C.secondary });
    addFooter(slide, 5);
    addNotes(slide, ["agent_team/pre_execution_gate.py", "SafeExecutor_Gate_implementation_plan.md"]);
  }

  // 06 SafeExecutor paths.
  {
    const slide = createSlide(presentation, true);
    addTitle(slide, "SafeExecutor 先分清“没执行”和“执行失败”", 6, "ONE EXECUTION ENVELOPE", true);
    addText(slide, "executor-input", "SQLArtifact", { left: 520, top: 190, width: 240, height: 54 }, 26, {
      bold: true, color: C.canvas, alignment: "center", fill: "#102C42",
      line: { style: "solid", fill: C.accent, width: 2 },
    });
    addRule(slide, "executor-stem", 638, 244, 4, C.accentStrong, 112);
    addRule(slide, "executor-branch", 210, 354, 860, C.accentStrong, 3);
    [210, 638, 1068].forEach((x, i) => addRule(slide, `executor-drop-${i}`, x, 354, 4, C.accentStrong, 48));
    const paths = [
      ["Gate blocked", "attempted = false", "数据库从未接触 SQL", C.danger],
      ["DB failed", "attempted = true", "确定性数据库错误反馈", C.warning],
      ["DB succeeded", "ok = true", "进入语义 Judge", C.success],
    ];
    paths.forEach(([title, state, detail, color], i) => {
      const x = 62 + i * 426;
      addBox(slide, `executor-path-${i}`, { left: x, top: 402, width: 360, height: 170 }, {
        fill: C.darkPanel, line: { style: "solid", fill: color, width: 2 }, borderRadius: 8,
      });
      addText(slide, `executor-path-title-${i}`, title, { left: x + 24, top: 424, width: 310, height: 34 }, 23, {
        bold: true, color,
      });
      addText(slide, `executor-path-state-${i}`, state, { left: x + 24, top: 474, width: 310, height: 28 }, 16, {
        typeface: MONO, color: "#A9B6C4",
      });
      addText(slide, `executor-path-detail-${i}`, detail, { left: x + 24, top: 522, width: 310, height: 30 }, 16, {
        color: C.canvas,
      });
    });
    addFooter(slide, 6, true);
    addNotes(slide, ["agent_team/executor.py", "agent_team/contracts.py"]);
  }

  // 07 Judge routing table.
  {
    const slide = createSlide(presentation);
    addTitle(slide, "Judge 只在执行成功后使用语义 LLM", 7, "JUDGE MODES");
    const columns = [42, 320, 515, 690, 880, 1238];
    const headers = ["输入状态", "mode", "Judge LLM", "核心输出", "下一步"];
    headers.forEach((header, i) => {
      addBox(slide, `judge-head-${i}`, {
        left: columns[i], top: 210, width: columns[i + 1] - columns[i], height: 58,
      }, { fill: C.ink, line: { style: "solid", fill: C.canvas, width: 1 } });
      addText(slide, `judge-head-text-${i}`, header, {
        left: columns[i] + 12, top: 226, width: columns[i + 1] - columns[i] - 24, height: 26,
      }, 15, { bold: true, color: C.canvas });
    });
    const rows = [
      ["Gate 失败", "gate", "0 次", "blockers + fingerprint", "Gate repair"],
      ["数据库失败", "database", "0 次", "DB error + signature", "Execution repair"],
      ["执行成功", "semantic", "按需", "intent comparison", "PASS / Semantic repair"],
    ];
    rows.forEach((row, r) => {
      const y = 268 + r * 102;
      row.forEach((value, i) => {
        addBox(slide, `judge-cell-${r}-${i}`, {
          left: columns[i], top: y, width: columns[i + 1] - columns[i], height: 102,
        }, { fill: r === 2 ? "#EAF5FB" : C.panelLight, line: { style: "solid", fill: C.rule, width: 1 } });
        addText(slide, `judge-cell-text-${r}-${i}`, value, {
          left: columns[i] + 12, top: y + 29, width: columns[i + 1] - columns[i] - 24, height: 46,
        }, i === 1 ? 15 : 16, { bold: i === 0, typeface: i === 1 ? MONO : FONT });
      });
    });
    addText(slide, "judge-takeaway", "确定性问题不消耗 Judge LLM；语义成本只花在已经可执行的 SQL 上。", {
      left: 42, top: 604, width: 1120, height: 38,
    }, 20, { bold: true, color: C.accentStrong });
    addFooter(slide, 7);
    addNotes(slide, ["agent_team/nl2sql_judge.py", "SafeExecutor_Gate_implementation_plan.md"]);
  }

  // 08 Repair budgets.
  {
    const slide = createSlide(presentation, true);
    addTitle(slide, "Refiner 的修复循环有明确上限", 8, "BOUNDED REPAIR", true);
    addText(slide, "budget-subtitle", "三类失败分别计数，同时受总 SQL 尝试次数约束。", {
      left: 42, top: 174, width: 900, height: 42,
    }, 21, { color: "#A9B6C4" });
    const budgets = [
      ["2", "Gate repairs", "语法、安全与授权"],
      ["2", "Database repairs", "执行期数据库错误"],
      ["5", "Semantic repairs", "口径、粒度与意图"],
    ];
    budgets.forEach(([stat, title, detail], i) => {
      const x = 42 + i * 410;
      addBox(slide, `budget-card-${i}`, { left: x, top: 270, width: 366, height: 230 }, {
        fill: i === 2 ? "#102C42" : C.darkPanel,
        line: { style: "solid", fill: i === 2 ? C.accent : C.darkRule, width: i === 2 ? 2 : 1 },
        borderRadius: 8,
      });
      addText(slide, `budget-stat-${i}`, stat, { left: x + 28, top: 296, width: 120, height: 88 }, 56, {
        bold: true, color: i === 2 ? C.accent : C.canvas,
      });
      addText(slide, `budget-title-${i}`, title, { left: x + 28, top: 402, width: 300, height: 34 }, 21, { bold: true, color: C.canvas });
      addText(slide, `budget-detail-${i}`, detail, { left: x + 28, top: 450, width: 300, height: 28 }, 16, { color: "#A9B6C4" });
    });
    addText(slide, "budget-total", "MAX_TOTAL_SQL_ATTEMPTS = 10", {
      left: 42, top: 548, width: 500, height: 42,
    }, 21, { bold: true, typeface: MONO, color: C.canvas });
    addText(slide, "budget-reschema", "受限补 Schema：最多 1 次 / 最多新增 2 张表", {
      left: 670, top: 548, width: 568, height: 42,
    }, 20, { bold: true, alignment: "right", color: C.accentStrong });
    addFooter(slide, 8, true);
    addNotes(slide, ["agent_team/orchestrator.py", "agent_team/refiner.py", "tests/test_judge_closed_loop.py"]);
  }

  // 09 Stop conditions.
  {
    const slide = createSlide(presentation, true);
    addTitle(slide, "停止条件比“多试几次”更重要", 9, "LOOP TERMINATION", true);
    addRule(slide, "stop-line", 82, 336, 1110, C.darkRule, 2);
    const stops = [
      ["01", "重复 SQL", "同一 SQL 再次出现，立即停止。"],
      ["02", "重复 fingerprint", "同类失败连续出现两次，终止无效循环。"],
      ["03", "预算耗尽", "单类预算或总 10 次尝试触发退出。"],
    ];
    stops.forEach(([num, title, body], i) => {
      const x = 82 + i * 410;
      addBox(slide, `stop-dot-${i}`, { left: x, top: 324, width: 26, height: 26 }, {
        geometry: "ellipse", fill: i === 2 ? C.danger : C.accentStrong,
        line: { style: "solid", fill: C.dark, width: 3 },
      });
      addText(slide, `stop-num-${i}`, num, { left: x, top: 265, width: 70, height: 30 }, 14, {
        bold: true, color: "#8FA0B2",
      });
      addText(slide, `stop-title-${i}`, title, { left: x, top: 390, width: 330, height: 42 }, 26, { bold: true, color: C.canvas });
      addText(slide, `stop-body-${i}`, body, { left: x, top: 458, width: 330, height: 88 }, 18, { color: "#A9B6C4" });
    });
    addText(slide, "stop-takeaway", "系统宁可诚实停止，也不把重复尝试包装成“智能修复”。", {
      left: 42, top: 594, width: 1120, height: 40,
    }, 21, { bold: true, color: C.accentStrong });
    addFooter(slide, 9, true);
    addNotes(slide, ["agent_team/orchestrator.py", "tests/test_retry_routing.py"]);
  }

  // 10 Trust states.
  {
    const slide = createSlide(presentation);
    addTitle(slide, "没有执行器时，结果只能叫 generated_unverified", 10, "TRUST STATES");
    addBox(slide, "state-unverified", { left: 0, top: 190, width: 620, height: 440 }, {
      fill: "#FFF1DF", line: { style: "solid", fill: "#FFF1DF", width: 0 },
    });
    addRule(slide, "state-unverified-rail", 0, 190, 620, C.warning, 8);
    addText(slide, "state-unverified-label", "NO EXECUTOR", { left: 72, top: 238, width: 220, height: 28 }, 15, {
      bold: true, color: C.warning,
    });
    addText(slide, "state-unverified-title", "generated_\nunverified", { left: 72, top: 304, width: 490, height: 94 }, 34, {
      bold: true, typeface: MONO,
    });
    addBulletList(slide, "state-unverified-list", [
      "success = false",
      "SQL 可供人工查看",
      "不能声称已验证",
    ], { left: 72, top: 445, width: 460, height: 130 }, { size: 19, color: C.secondary });
    addBox(slide, "state-verified", { left: 660, top: 190, width: 620, height: 440 }, {
      fill: "#E5F6EE", line: { style: "solid", fill: "#E5F6EE", width: 0 },
    });
    addRule(slide, "state-verified-rail", 660, 190, 620, C.success, 8);
    addText(slide, "state-verified-label", "SAFE EXECUTION + SEMANTIC PASS", {
      left: 704, top: 238, width: 430, height: 28,
    }, 15, { bold: true, color: C.success });
    addText(slide, "state-verified-title", "verified\nsuccess", { left: 704, top: 304, width: 520, height: 94 }, 38, {
      bold: true,
    });
    addBulletList(slide, "state-verified-list", [
      "Gate 通过",
      "数据库执行成功",
      "Judge semantic PASS",
    ], { left: 704, top: 445, width: 500, height: 130 }, { size: 19 });
    addFooter(slide, 10);
    addNotes(slide, ["README.md", "agent_team/orchestrator.py", "tests/test_retry_routing.py"]);
  }

  // 11 Current test evidence.
  {
    const slide = createSlide(presentation);
    addTitle(slide, "当前回归集验证了关键边界", 11, "CURRENT WSL VERIFICATION");
    addBox(slide, "tests-stat-panel", { left: 42, top: 200, width: 430, height: 390 }, {
      fill: "#102C42", line: { style: "solid", fill: C.accent, width: 2 }, borderRadius: 0,
    });
    addText(slide, "tests-stat", "25 / 25", { left: 78, top: 260, width: 360, height: 110 }, 60, {
      bold: true, color: C.accent, alignment: "center",
    });
    addText(slide, "tests-passed", "tests passed", { left: 78, top: 390, width: 360, height: 44 }, 24, {
      bold: true, color: C.canvas, alignment: "center",
    });
    addText(slide, "tests-time", "WSL isolated dependencies · 29.36s", {
      left: 78, top: 470, width: 360, height: 34,
    }, 15, { alignment: "center", color: "#A9B6C4" });
    addBox(slide, "tests-terminal-panel", { left: 510, top: 200, width: 728, height: 390 }, {
      fill: C.dark, line: { style: "solid", fill: C.darkRule, width: 1 },
    });
    addText(slide, "tests-command", "$ pytest tests -q", { left: 548, top: 228, width: 400, height: 34 }, 18, {
      bold: true, typeface: MONO, color: C.accent,
    });
    addText(slide, "tests-right-title", "覆盖的合同", { left: 548, top: 278, width: 300, height: 42 }, 26, { bold: true, color: C.canvas });
    addBulletList(slide, "tests-list", [
      "PreExecutionGate",
      "SafeExecutor 与 SQLite 只读层",
      "Judge / Refiner 闭环",
      "重试路由与停止条件",
      "SQLArtifact / DraftIntent",
    ], { left: 548, top: 332, width: 610, height: 190 }, { size: 19, color: "#DDE5EC" });
    addText(slide, "tests-boundary", "未验证：真实模型调用与 BIRD benchmark", {
      left: 548, top: 536, width: 650, height: 40,
    }, 19, { bold: true, color: C.warning });
    addFooter(slide, 11);
    addNotes(slide, [
      "Current command: env PYTHONPATH=<isolated-wsl-deps>:. python3 -m pytest tests -q",
      "tests/test_pre_execution_gate.py",
      "tests/test_safe_executor.py",
      "tests/test_judge_closed_loop.py",
      "tests/test_retry_routing.py",
      "tests/test_sql_artifact.py",
    ], "Observed result: 25 passed in 29.36s. Real model and BIRD benchmark were not run.");
  }

  // 12 Close: dark keynote synthesis.
  {
    const slide = createSlide(presentation, true);
    addText(slide, "close-kicker", "THE CORE IDEA", { left: 42, top: 42, width: 260, height: 30 }, 15, {
      bold: true, color: C.accent,
    });
    addText(slide, "close-index", "01 / 06 / 10", { left: 980, top: 42, width: 258, height: 30 }, 15, {
      bold: true, color: "#8FA0B2", alignment: "right",
    });
    addText(slide, "close-title", "可信 SQL 不是\n“生成出来”", {
      left: 42, top: 142, width: 760, height: 180,
    }, 54, { bold: true, color: C.canvas, verticalAlignment: "bottom" });
    addText(slide, "close-accent-title", "而是“验证出来”", {
      left: 42, top: 350, width: 1040, height: 92,
    }, 64, { bold: true, color: C.accent });
    addRule(slide, "close-rule", 42, 500, 1196, C.darkRule, 2);
    addText(slide, "close-line-1", "确定性 Gate 阻断高置信风险", {
      left: 42, top: 542, width: 360, height: 38,
    }, 17, { bold: true, color: C.canvas });
    addText(slide, "close-line-2", "SafeExecutor 统一执行反馈", {
      left: 454, top: 542, width: 360, height: 38,
    }, 17, { bold: true, color: C.canvas });
    addText(slide, "close-line-3", "Judge / Refiner 有界修复语义", {
      left: 866, top: 542, width: 372, height: 38,
    }, 17, { bold: true, color: C.canvas });
    addText(slide, "close-boundary", "当前边界：回归测试已验证；真实模型效果仍待 benchmark。", {
      left: 42, top: 620, width: 900, height: 34,
    }, 15, { color: "#8FA0B2" });
    addFooter(slide, 12, true);
    addNotes(slide, ["README.md", "SafeExecutor_Gate_implementation_plan.md", "Current WSL pytest run"]);
  }

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(path.join(RENDER_DIR, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(LAYOUT_DIR, `${stem}.layout.json`), await layout.text(), "utf8");
  }

  const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(path.join(RENDER_DIR, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));
  const inspect = await presentation.inspect({
    kind: "slide,textbox,shape,image,table,chart,notes",
    maxChars: 50000,
  });
  await fs.writeFile(path.resolve(HERE, "..", "artifact-inspect.ndjson"), inspect.ndjson, "utf8");

  const pptx = await PresentationFile.exportPptx(presentation);
  const pptxPath = path.join(OUTPUT_DIR, "NL2SQL_Agent_Overview.pptx");
  await pptx.save(pptxPath);
  console.log(JSON.stringify({ pptxPath, slideCount: presentation.slides.items.length, renderDir: RENDER_DIR }));
}

buildDeck().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
