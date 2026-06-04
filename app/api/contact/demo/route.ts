import { NextResponse } from "next/server";
import nodemailer from "nodemailer";

/**
 * POST /api/contact/demo
 *
 * Accepts a JSON payload from the /demo lead-capture form and emails it
 * to the configured recipient (defaults to gorny@nextiva.com). When SMTP
 * env vars aren't configured, the route logs the submission to the server
 * console and still returns 200 with `dev_mode: true` so local dev works
 * without credentials.
 *
 * Required production env vars (e.g. .env.production / Vercel secrets):
 *   SMTP_HOST       — e.g. smtp.sendgrid.net, smtp.gmail.com, smtp.nextiva.com
 *   SMTP_PORT       — usually 465 (SSL) or 587 (STARTTLS)
 *   SMTP_USER       — SMTP username
 *   SMTP_PASSWORD   — SMTP password / API key
 *   SMTP_FROM       — verified "From" address ("XBert Demo <demo@xbert.ai>")
 *   DEMO_TO_EMAIL   — optional, defaults to gorny@nextiva.com
 */

export const runtime = "nodejs";

type DemoPayload = {
  firstname?: string;
  lastname?: string;
  email?: string;
  phone?: string;
  company?: string;
  role?: string;
  industry?: string;
  size?: string;
  notes?: string;
  // Anti-spam honeypot field (legitimate browsers leave this empty)
  website?: string;
};

const DEFAULT_TO = "gorny@nextiva.com";

function escapeHtml(input: string): string {
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export async function POST(req: Request) {
  let payload: DemoPayload;
  try {
    payload = (await req.json()) as DemoPayload;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body." },
      { status: 400 },
    );
  }

  // Honeypot — silently accept and discard if filled.
  if (payload.website && payload.website.trim().length > 0) {
    return NextResponse.json({ ok: true, dev_mode: false });
  }

  const firstname = (payload.firstname ?? "").trim();
  const lastname = (payload.lastname ?? "").trim();
  const email = (payload.email ?? "").trim();
  const phone = (payload.phone ?? "").trim();
  const company = (payload.company ?? "").trim();
  const role = (payload.role ?? "").trim();
  const industry = (payload.industry ?? "").trim();
  const size = (payload.size ?? "").trim();
  const notes = (payload.notes ?? "").trim();

  const missing: string[] = [];
  if (!firstname) missing.push("firstname");
  if (!lastname) missing.push("lastname");
  if (!email) missing.push("email");
  if (!company) missing.push("company");
  if (missing.length > 0) {
    return NextResponse.json(
      { ok: false, error: `Missing required fields: ${missing.join(", ")}.` },
      { status: 400 },
    );
  }
  if (!isEmail(email)) {
    return NextResponse.json(
      { ok: false, error: "Please enter a valid email address." },
      { status: 400 },
    );
  }

  const fullName = `${firstname} ${lastname}`.trim();
  const to = process.env.DEMO_TO_EMAIL ?? DEFAULT_TO;
  const submittedAt = new Date().toISOString();

  const summaryRows: Array<[string, string]> = [
    ["Name", fullName],
    ["Email", email],
    ["Phone", phone],
    ["Company", company],
    ["Role", role],
    ["Industry", industry],
    ["Business size", size],
    ["What they want to see", notes],
    ["Submitted", submittedAt],
  ];

  const textBody = summaryRows
    .filter(([, value]) => value && value.length > 0)
    .map(([label, value]) => `${label}: ${value}`)
    .join("\n");

  const htmlRows = summaryRows
    .filter(([, value]) => value && value.length > 0)
    .map(
      ([label, value]) =>
        `<tr><td style="padding:6px 12px 6px 0;font-family:sans-serif;font-size:13px;color:#7A756F;text-transform:uppercase;letter-spacing:.08em;vertical-align:top;white-space:nowrap;">${escapeHtml(label)}</td><td style="padding:6px 0;font-family:sans-serif;font-size:14px;color:#101A33;">${escapeHtml(value).replace(/\n/g, "<br>")}</td></tr>`,
    )
    .join("");

  const htmlBody = `
<!doctype html>
<html><body style="margin:0;background:#f4f3ef;padding:24px;">
  <table role="presentation" style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #e3dfd6;border-radius:12px;padding:24px;">
    <tr><td>
      <h2 style="margin:0 0 6px;font-family:Georgia,serif;font-size:22px;color:#0B1428;">New XBert demo request</h2>
      <p style="margin:0 0 18px;font-family:sans-serif;font-size:13px;color:#7A756F;">From the /demo form on the XBert site.</p>
      <table role="presentation" style="width:100%;border-collapse:collapse;">${htmlRows}</table>
    </td></tr>
  </table>
</body></html>`;

  const subject = `[XBert demo] ${fullName} · ${company}${industry ? ` · ${industry}` : ""}`;

  // Dev fallback — no SMTP configured.
  const smtpHost = process.env.SMTP_HOST;
  const smtpUser = process.env.SMTP_USER;
  const smtpPass = process.env.SMTP_PASSWORD;
  const smtpFrom = process.env.SMTP_FROM ?? smtpUser ?? "noreply@xbert.local";

  if (!smtpHost || !smtpUser || !smtpPass) {
    console.warn(
      "[/api/contact/demo] SMTP not configured — logging submission only.\n" +
        `  → would send to: ${to}\n` +
        `  → subject: ${subject}\n` +
        `  → body:\n${textBody.replace(/^/gm, "    ")}`,
    );
    return NextResponse.json({ ok: true, dev_mode: true });
  }

  try {
    const transporter = nodemailer.createTransport({
      host: smtpHost,
      port: Number(process.env.SMTP_PORT ?? 587),
      secure: Number(process.env.SMTP_PORT ?? 587) === 465,
      auth: { user: smtpUser, pass: smtpPass },
    });

    await transporter.sendMail({
      from: smtpFrom,
      to,
      replyTo: email,
      subject,
      text: textBody,
      html: htmlBody,
    });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown SMTP error.";
    console.error("[/api/contact/demo] SMTP error:", message);
    return NextResponse.json(
      { ok: false, error: "We couldn't send your request right now." },
      { status: 502 },
    );
  }

  return NextResponse.json({ ok: true, dev_mode: false });
}
