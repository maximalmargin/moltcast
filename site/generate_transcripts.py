#!/usr/bin/env python3
"""Generate transcript HTML pages from markdown files."""
import re
import html
from pathlib import Path

EPISODES_DIR = Path(__file__).parent.parent / "episodes"
OUTPUT_DIR = Path(__file__).parent / "transcript"

TRANSCRIPTS = [
    ("ep001", "en", "The Democratization of Power", "Episode 1"),
    ("ep002", "en", "Taste Is a Class War", "Episode 2"),
    ("ep003", "en", "The Lobster Problem", "Episode 3"),
    ("ep004", "en", "La Distinction", "Episode 4"),
    ("ep005", "en", "The Lobster (2015)", "Episode 5"),
    ("ep006", "en", "Laid Off — The Iron Rice Bowl in the Age of AI", "Episode 6"),
    ("ep007", "en", "The Slot Machine", "Episode 7"),
    ("ep001", "cn", "权力的民主化", "第一集"),
    ("ep002", "cn", "品味是一场阶级战争", "第二集"),
    ("ep003", "cn", "龙虾问题", "第三集"),
    ("ep004", "cn", "La Distinction（区隔）", "第四集"),
    ("ep005", "cn", "The Lobster (Yorgos Lanthimos, 2015)", "第五集"),
    ("ep006", "cn", "铁饭碗 — AI时代的下岗潮", "第六集"),
    ("ep007", "cn", "老虎机 — 为什么AI让你停不下来", "第七集"),
]

def md_to_html_body(md_text: str) -> str:
    """Convert transcript markdown to HTML paragraphs."""
    lines = md_text.strip().split("\n")
    parts = []
    skip_header = True

    for line in lines:
        line = line.strip()

        # Skip the title line and topic line and separator
        if skip_header:
            if line.startswith("# ") or line.startswith("*Recorded") or line.startswith("*录制") or line == "---" or line.startswith("**Topic:") or line.startswith("**话题") or line.startswith("**主题") or not line:
                if line == "---" and parts:
                    skip_header = False  # second --- means end of header
                elif line == "---":
                    continue
                continue
            skip_header = False

        if not line:
            continue

        # Footer
        if line.startswith("*A Maximal Margin") or line.startswith("*一个 Maximal Margin") or line.startswith("*Maximal Margin"):
            break
        if line == "---":
            continue

        # Convert **Name:** or **Name** (Role): patterns to speaker paragraphs
        escaped = html.escape(line)
        # Bold patterns: **text**
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
        # Italic patterns: *text*
        escaped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', escaped)

        # Detect speaker lines
        if escaped.startswith("<strong>"):
            # Extract speaker name
            m = re.match(r'<strong>(.+?)</strong>\s*(?:（.+?）\s*)?[：:]?\s*(.*)', escaped)
            if m:
                speaker = m.group(1).rstrip("：:").strip()
                # Remove role annotations like (The Host)
                speaker = re.sub(r'\s*\(.+?\)\s*', '', speaker)
                text = m.group(2)
                parts.append(f'<p class="speaker"><span class="speaker-name">{speaker}</span></p>')
                if text:
                    parts.append(f'<p>{text}</p>')
                continue

        parts.append(f'<p>{escaped}</p>')

    return "\n          ".join(parts)


TEMPLATE = """\
<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ep_label}: {title} — MoltCast</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
    :root {{
      --black: #111;
      --gray: #666;
      --light-gray: #e5e5e5;
    }}
    body {{
      font-family: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
      color: var(--black);
      background: #fff;
      line-height: 1.7;
      -webkit-font-smoothing: antialiased;
    }}
    nav {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(255,255,255,0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--light-gray);
      padding: 0 24px;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .nav-wordmark {{
      font-size: 16px;
      font-weight: 500;
      letter-spacing: -0.5px;
      color: var(--black);
      text-decoration: none;
    }}
    .back-link {{
      font-size: 13px;
      color: var(--gray);
      text-decoration: none;
      border-bottom: 1px solid var(--light-gray);
    }}
    .back-link:hover {{
      color: var(--black);
      border-color: var(--black);
    }}
    .transcript-header {{
      max-width: 640px;
      margin: 0 auto;
      padding: 80px 24px 40px;
    }}
    .transcript-header .ep-label {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--gray);
      margin-bottom: 12px;
    }}
    .transcript-header h1 {{
      font-size: 28px;
      font-weight: 600;
      letter-spacing: -0.5px;
      line-height: 1.3;
    }}
    .transcript-body {{
      max-width: 640px;
      margin: 0 auto;
      padding: 0 24px 80px;
    }}
    .transcript-body p {{
      font-size: 15px;
      line-height: 1.8;
      color: #333;
      margin-bottom: 16px;
    }}
    .transcript-body .speaker {{
      margin-top: 28px;
      margin-bottom: 4px;
    }}
    .transcript-body .speaker-name {{
      font-weight: 600;
      font-size: 13px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--black);
    }}
    footer {{
      padding: 48px 24px;
      border-top: 1px solid var(--light-gray);
      text-align: center;
      font-size: 13px;
      color: var(--gray);
    }}
    footer a {{
      color: var(--gray);
      text-decoration: underline;
      text-underline-offset: 2px;
    }}
  </style>
</head>
<body>

  <nav>
    <a href="/" class="nav-wordmark">MoltCast</a>
    <a href="/#episodes" class="back-link">{back_text}</a>
  </nav>

  <div class="transcript-header">
    <p class="ep-label">{ep_label} — {transcript_word}</p>
    <h1>{title}</h1>
  </div>

  <div class="transcript-body">
    {body}
  </div>

  <footer>
    <p>A <a href="https://maximalmargin.com">Maximal Margin</a> production</p>
  </footer>

</body>
</html>
"""

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for ep_id, lang, title, ep_label in TRANSCRIPTS:
        md_path = EPISODES_DIR / ep_id / f"transcript-{lang}.md"
        if not md_path.exists():
            print(f"SKIP: {md_path} not found")
            continue

        md_text = md_path.read_text(encoding="utf-8")
        body = md_to_html_body(md_text)

        lang_attr = "en" if lang == "en" else "zh-CN"
        back_text = "Back to episodes" if lang == "en" else "返回单集列表"
        transcript_word = "Transcript" if lang == "en" else "文字稿"

        out_html = TEMPLATE.format(
            lang_attr=lang_attr,
            title=html.escape(title),
            ep_label=ep_label,
            back_text=back_text,
            transcript_word=transcript_word,
            body=body,
        )

        out_path = OUTPUT_DIR / f"{ep_id}-{lang}.html"
        out_path.write_text(out_html, encoding="utf-8")
        print(f"OK: {out_path.name}")

if __name__ == "__main__":
    main()
