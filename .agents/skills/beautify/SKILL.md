---
name: beautify
description: Polish this repo's README, dothelp, and terminal presentation with clear hierarchy and restrained styling. Use when asked to beautify or improve the look of the terminal setup.
---

# Beautify

Make this small terminal setup pleasant to read and easy to use. Improve
presentation with fewer distractions and little extra code.

## Read first

- `README.md` is both the GitHub front page and dothelp's guide.
- `configs/dothelp.sh` selects its `##` headings and renders topics.
- `configs/.zshrc` defines aliases, the prompt, and the dothelp wrapper.
- Read the relevant implementation before changing command examples.

## Style

- Keep a clear title, short introduction, useful navigation, and copyable examples.
- Use consistent headings, whitespace, and short labels. Use tables for compact
  comparisons; use prose when table cells would become paragraphs.
- Keep Markdown readable on GitHub, in Glow, and as plain text. Avoid HTML,
  decorative badges, large ASCII banners, and repeated emoji.
- Let Glow and fzf supply terminal colors. Respect the user's theme; do not
  introduce a separate color system or force ANSI codes into piped output.
- Keep shortcuts and commands visible beside their explanations. Use a small
  picker header to explain searching, selection, and cancellation.
- Preserve prompt information and distinguish status through symbols as well
  as color. Do not add noise to every shell startup.

## Work

1. Identify the few changes with the largest visible benefit. Preserve the
   user's preferred reference-guide style; keep README as the single guide.
2. Edit the existing files directly. Keep `##` topic names and anchors stable;
   if renaming is necessary, update navigation, aliases, and callers together.
3. Preserve commands, exit statuses, cancellation, backups, and fallbacks.
   Keep optional tools optional. Avoid new dependencies and abstraction layers.
4. Preview the full README and a focused topic with Glow at 80 and 120 columns
   when available. Check plain text too. If the picker changes, try search,
   Enter, and Escape in a real terminal; inspect the prompt when editing it.
5. Run shell syntax checks for changed scripts. Run the existing tests when
   behavior or topic handling could change. Check documentation links for
   prose-only edits; do not add tests that assert formatting or prose.

Deliver a small PR describing the visible improvements and actual preview
checks. Follow the user's merge instructions. Do not claim a visual preview
was inspected if the environment only allowed text checks.
