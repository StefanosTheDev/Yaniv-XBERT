import { readFileSync } from "node:fs";
import { join } from "node:path";

// Server-only helper: reads a pre-extracted HTML partial from
// components/legacy/ at render time. Cached per-process by the runtime.
export function loadLegacyHtml(filename: string): string {
  const path = join(process.cwd(), "components", "legacy", filename);
  return readFileSync(path, "utf8");
}
