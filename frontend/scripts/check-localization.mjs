import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse } from "@babel/parser";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(frontendRoot, "..");
const violations = [];

// Preserve branding, contributor names, examples, and model identifiers that are data rather than UI copy.
const allowedUiLiterals = new Set([
  "SF",
  "Smart Farming",
  "Smart Farming Platform",
  "Prof. Rajnik Katariya",
  "Kunj Lunagariya",
  "Manthan Kuvadiya",
  "Ramesh Patel",
  "Anand, Gujarat",
  "farmer@example.com",
  "your-email@example.com",
  "e.g. 529183",
  "EfficientNet-B2",
  "ms",
  "••••••••",
  "N/A",
]);

const uiAttributes = new Set([
  "alt",
  "aria-description",
  "aria-label",
  "confirmLabel",
  "description",
  "emptyMessage",
  "error",
  "helperText",
  "hint",
  "label",
  "loadingMessage",
  "placeholder",
  "title",
]);

const feedbackCalls = new Set(["alert", "confirm"]);
const feedbackSetter = /^set[A-Z].*(?:Error|Message|Success|Status|Notice|Feedback|Warning|Info)$/;

function hasLetters(value) {
  return /[A-Za-z]{2}/.test(value);
}

function checkLiteral(value, file, line, context) {
  const text = value.replace(/\s+/g, " ").trim();
  if (!text || !hasLetters(text) || allowedUiLiterals.has(text) || /^\{[a-zA-Z]+\}$/.test(text)) return;
  violations.push(`${path.relative(repositoryRoot, file)}:${line}: ${context} contains "${text}"`);
}

function callName(node) {
  if (node?.type !== "CallExpression") return "";
  if (node.callee.type === "Identifier") return node.callee.name;
  if (node.callee.type === "MemberExpression" && node.callee.property.type === "Identifier") {
    return node.callee.property.name;
  }
  return "";
}

function inspectFeedbackExpression(node, file, line) {
  if (!node || typeof node !== "object") return;
  if (Array.isArray(node)) {
    for (const child of node) inspectFeedbackExpression(child, file, line);
    return;
  }
  if (node.type === "CallExpression" && ["t", "translate"].includes(callName(node))) return;
  if (node.type === "StringLiteral") {
    checkLiteral(node.value, file, line, "feedback message");
    return;
  }
  if (node.type === "TemplateLiteral") {
    for (const quasi of node.quasis) {
      checkLiteral(quasi.value.cooked ?? quasi.value.raw, file, line, "feedback message");
    }
    for (const expression of node.expressions) inspectFeedbackExpression(expression, file, line);
    return;
  }
  if (node.type === "ObjectProperty" && node.key.type === "Identifier" && node.key.name === "type") {
    return;
  }
  for (const [key, value] of Object.entries(node)) {
    if (["loc", "start", "end", "extra", "comments", "leadingComments", "trailingComments"].includes(key)) continue;
    if (value && typeof value === "object") inspectFeedbackExpression(value, file, line);
  }
}

function inspectRenderedExpression(node, file, line) {
  if (!node || typeof node !== "object") return;
  if (node.type === "StringLiteral") {
    checkLiteral(node.value, file, line, "rendered JSX expression");
    return;
  }
  if (node.type === "TemplateLiteral") {
    for (const quasi of node.quasis) {
      checkLiteral(quasi.value.cooked ?? quasi.value.raw, file, line, "rendered JSX expression");
    }
    return;
  }
  if (node.type === "CallExpression") {
    if (
      ["t", "translate", "translateCrop", "translateDisease", "translatePest", "translateSeverityBucket", "translateWeather"].includes(
        callName(node),
      )
    ) {
      return;
    }
    return;
  }
  if (node.type === "ConditionalExpression") {
    inspectRenderedExpression(node.consequent, file, line);
    inspectRenderedExpression(node.alternate, file, line);
    return;
  }
  if (node.type === "LogicalExpression") {
    inspectRenderedExpression(node.right, file, line);
    return;
  }
  if (node.type === "ArrayExpression" || node.type === "SequenceExpression") {
    for (const item of node.elements ?? node.expressions) inspectRenderedExpression(item, file, line);
    return;
  }
  if (node.type === "ParenthesizedExpression" || node.type === "TSAsExpression") {
    inspectRenderedExpression(node.expression, file, line);
  }
}

function checkWebSources() {
  const files = [];
  const visitDirectory = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) visitDirectory(file);
      else if (file.endsWith(".tsx")) files.push(file);
    }
  };
  visitDirectory(path.join(frontendRoot, "src"));

  for (const file of files) {
    const source = parse(fs.readFileSync(file, "utf8"), {
      sourceType: "module",
      plugins: ["jsx", "typescript"],
      errorRecovery: false,
    });

    const inspect = (node, parent = null) => {
      if (!node || typeof node !== "object") return;
      if (Array.isArray(node)) {
        node.forEach(inspect);
        return;
      }
      const line = node.loc?.start.line ?? 1;
      if (node.type === "JSXText") {
        checkLiteral(node.value, file, line, "JSX text");
      }
      if (node.type === "JSXExpressionContainer" && node.expression.type !== "JSXEmptyExpression") {
        const attributeName = parent?.type === "JSXAttribute" ? parent.name.name : "";
        if (!parent || parent.type !== "JSXAttribute" || uiAttributes.has(attributeName)) {
          inspectRenderedExpression(node.expression, file, line);
        }
      }
      if (node.type === "JSXAttribute" && uiAttributes.has(node.name.name) && node.value?.type === "StringLiteral") {
        checkLiteral(node.value.value, file, line, node.name.name);
      }
      if (node.type === "CallExpression") {
        const name = callName(node);
        if (feedbackCalls.has(name) || feedbackSetter.test(name)) {
          for (const arg of node.arguments) inspectFeedbackExpression(arg, file, line);
        }
      }
      for (const [key, value] of Object.entries(node)) {
        if (["loc", "start", "end", "extra", "comments", "leadingComments", "trailingComments"].includes(key)) continue;
        if (value && typeof value === "object") {
          if (Array.isArray(value)) value.forEach((child) => inspect(child, node));
          else inspect(value, node);
        }
      }
    };
    inspect(source);
  }
}

function checkFlutterSources() {
  const patterns = [
    /\b(?:Text|SelectableText)\s*\(\s*(?:const\s+)?(['"])([^'"\n]*)\1/g,
    /\b(?:tooltip|labelText|hintText|semanticLabel|errorText|title|content|subtitle|helperText)\s*:\s*(?:const\s+)?(?:Text\s*\(\s*)?(['"])([^'"\n]*)\1/g,
  ];
  const allowedFlutterLiterals = new Set([
    "English",
    "Gujarati",
    "Hindi",
    "ગુજરાતી (Gujarati)",
    "हिन्दी (Hindi)",
    "Indian English",
    "Crop disease diagnosis and expert guidance",
    "Smart Farm AI",
    "તમારી ભાષા પસંદ કરો • अपनी भाषा चुनें • Select Language",
    "$value%",
    "$areaAcres ac ($areaHectares ha)",
    "${parentSev.toStringAsFixed(1)}%",
    "${currSev.toStringAsFixed(1)}%",
    "$unreadCount",
    "$location · $area",
    "$number",
    "$number. $title",
    "$severityPercent% $label",
    "${(item.confidence * 100).round()}%",
    "$acres ac",
    "$hectares ha",
    "${perimeterM.round()} m",
    "$label ($pct%)",
    "${_pred.severity}% $severityLevel",
    "$farmName · $location",
    "${_alerts.where((a) => a[",
    "($transliterated)",
    "$areaAcres ac ($areaHectares ha)",
    "${parentSev.toStringAsFixed(1)}%",
    "${currSev.toStringAsFixed(1)}%",
  ]);
  const root = path.join(repositoryRoot, "mobile", "lib");
  const scan = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) scan(file);
      else if (file.endsWith(".dart")) {
        const source = fs.readFileSync(file, "utf8");
        for (const pattern of patterns) {
          for (const match of source.matchAll(pattern)) {
            const value = match[2];
            if (
              !value ||
              !hasLetters(value) ||
              allowedFlutterLiterals.has(value.trim()) ||
              value.includes("${context.tr") ||
              value.includes("${context.loc.")
            ) {
              continue;
            }
            const line = source.slice(0, match.index).split("\n").length;
            violations.push(
              `${path.relative(repositoryRoot, file)}:${line}: Flutter UI literal contains "${value.trim()}"`,
            );
          }
        }
      }
    }
  };
  scan(root);

  const catalogPath = path.join(root, "i18n", "app_translations.dart");
  const catalog = fs.readFileSync(catalogPath, "utf8");
  const catalogKeys = new Set(
    [...catalog.matchAll(/^\s*'([^']+)':\s*\{/gm)].map((match) => match[1]),
  );
  const checkTranslationReferences = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) checkTranslationReferences(file);
      else if (file.endsWith(".dart") && file !== catalogPath) {
        const source = fs
          .readFileSync(file, "utf8")
          .replace(/\/\*[\s\S]*?\*\/|^\s*\/\/.*$/gm, (comment) =>
            comment.replace(/[^\n]/g, " "),
          );
        const references = /\.tr\(\s*'([^']+)'\s*\)/g;
        for (const match of source.matchAll(references)) {
          if (!catalogKeys.has(match[1])) {
            const line = source.slice(0, match.index).split("\n").length;
            violations.push(
              `${path.relative(repositoryRoot, file)}:${line}: unknown mobile translation key "${match[1]}"`,
            );
          }
        }
      }
    }
  };
  checkTranslationReferences(root);
}

async function checkWebCatalogsAndRendering() {
  const vite = await createServer({
    configFile: path.join(frontendRoot, "vite.config.ts"),
    server: { middlewareMode: true },
    appType: "custom",
    logLevel: "error",
  });
  try {
    const { en } = await vite.ssrLoadModule("/src/i18n/en.ts");
    const { gu } = await vite.ssrLoadModule("/src/i18n/gu.ts");
    const { hi } = await vite.ssrLoadModule("/src/i18n/hi.ts");
    const { t } = await vite.ssrLoadModule("/src/i18n/index.ts");
    const {
      translateAlertTitle,
      translateCrop,
      translateDisease,
      translatePest,
      translateSeverityBucket,
      translateWeather,
    } = await vite.ssrLoadModule("/src/i18n/domain.ts");
    const keys = Object.keys(en).sort();
    for (const [language, catalog] of Object.entries({ Gujarati: gu, Hindi: hi })) {
      assert.deepEqual(Object.keys(catalog).sort(), keys, `${language} catalog key parity`);
      for (const key of keys) {
        assert.equal(typeof catalog[key], "string", `${language}.${key} must be a string`);
        assert.ok(catalog[key].trim(), `${language}.${key} must not be empty`);
      }
    }

    const rendered = {
      English: renderToStaticMarkup(React.createElement("p", null, t("scanCtaCopy", "English"))),
      Gujarati: renderToStaticMarkup(React.createElement("p", null, t("scanCtaCopy", "Gujarati"))),
      Hindi: renderToStaticMarkup(React.createElement("p", null, t("scanCtaCopy", "Hindi"))),
    };
    assert.notEqual(rendered.English, rendered.Gujarati, "English and Gujarati UI should render differently");
    assert.notEqual(rendered.English, rendered.Hindi, "English and Hindi UI should render differently");
    assert.notEqual(rendered.Gujarati, rendered.Hindi, "Gujarati and Hindi UI should render differently");
    assert.match(rendered.Gujarati, /સ્થાનિક હવામાન/);
    assert.match(rendered.Hindi, /स्थानीय मौसम/);
    assert.equal(
      t("scanCtaCopy", "French"),
      t("scanCtaCopy", "English"),
      "unsupported web languages should fall back to English",
    );
    assert.equal(t("missingLocalizationKey", "Gujarati"), "missingLocalizationKey");
    assert.equal(translateCrop(null, "Hindi"), "अज्ञात फसल");
    assert.equal(translateDisease(null, "Gujarati"), "અનિર્ધારિત સ્થિતિ");
    assert.equal(translateDisease("Unidentified Condition", "Hindi"), "अज्ञात स्थिति");
    assert.equal(translatePest(null, "Gujarati"), "જીવાત");
    assert.equal(translateSeverityBucket(null, "Hindi"), "लागू नहीं");
    assert.equal(translateSeverityBucket("Unknown", "Gujarati"), "અજ્ઞાત");
    assert.equal(translateWeather(null, "Hindi"), "साफ आसमान");
    assert.equal(translateAlertTitle(null, "Gujarati"), "ચેતવણી");
  } finally {
    await vite.close();
  }
}

checkWebSources();
checkFlutterSources();
if (violations.length > 0) {
  console.error(violations.join("\n"));
  process.exitCode = 1;
} else {
  await checkWebCatalogsAndRendering();
  console.log("Localization literal checks, EN/GU/HI catalog parity, rendered-language checks, and fallback checks passed.");
}
