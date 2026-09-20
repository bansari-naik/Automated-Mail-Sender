// Parse + validate the pasted recruiter emails.
// Handles blank lines, duplicates (case-insensitive) and invalid formats.

const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

export function parseEmails(rawText) {
  const lines = rawText.split(/[\n,;]+/).map((s) => s.trim()).filter(Boolean);
  const seen = new Set();
  const valid = [];
  let duplicates = 0;
  let invalid = 0;

  for (const line of lines) {
    const lower = line.toLowerCase();
    if (!EMAIL_RE.test(line)) {
      invalid += 1;
      continue;
    }
    if (seen.has(lower)) {
      duplicates += 1;
      continue;
    }
    seen.add(lower);
    valid.push(lower);
  }
  return { valid, duplicates, invalid };
}
