import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import test from "node:test";

const projectUrl = "/northstar-merchandise-intelligence/";

test("GitHub Pages build is complete and project-relative", async () => {
  const html = await readFile(new URL("../docs/index.html", import.meta.url), "utf8");
  assert.match(html, /Northstar \| Merchandise Planning/);
  assert.match(html, new RegExp(`${projectUrl}assets/index-[^\"']+\\.js`));
  assert.match(html, new RegExp(`${projectUrl}assets/index-[^\"']+\\.css`));

  const scriptPath = html.match(/src="([^"]+\.js)"/)?.[1];
  assert.ok(scriptPath, "The generated JavaScript bundle is linked.");
  const bundle = await readFile(new URL(`../docs/${scriptPath.replace(projectUrl, "")}`, import.meta.url), "utf8");
  assert.match(bundle, /Merchandise Trading Overview/);
  assert.match(bundle, /downloads\/Merchandise_Planning_Model\.xlsx/);

  for (const file of [
    "Merchandise_Planning_Model.xlsx",
    "Weekly_Merchandise_Trading_Report.pdf",
    "Data_Dictionary.pdf",
  ]) {
    const details = await stat(new URL(`../docs/downloads/${file}`, import.meta.url));
    assert.ok(details.size > 1_000, `${file} should be a real downloadable artifact.`);
  }
});
