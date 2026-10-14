#!/usr/bin/env python3
"""ポリシーの原本(Markdown)から、公開ページ(privacy.html・tokushoho.html)の<main>の中身を生成する。

原本はアプリのリポジトリ(非公開)の documents/ にあるため、手元で実行する。
<main>の外側(<head>・CSS・パンくず・フッター)は、今あるHTMLをテンプレートとしてそのまま残す。

使い方:
    python3 scripts/build_policies.py [原本のフォルダ]   # 既定: ../geoben/documents/
    python3 scripts/build_policies.py --check            # 書き換えずに、公開ページが原本と一致するかだけ確かめる

原本の書き方の決まり(これ以外の記法はエラーにする):
    - `# 見出し` → <h1>。`##` → <h2>、`###` → <h3>
    - `>` で始まる引用ブロックは作業メモとして扱い、公開ページに含めない
    - `## 付録` 以降は公開ページに含めない
    - 本文の最初の段落が「制定日:」「最終改定日:」「最終更新日:」の行だけなら日付として表示する
    - `- ` の箇条書き、`1. ` の番号付きリスト、表、**太字**、[リンク](URL)、メールアドレス(自動でリンクにする)
"""

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT.parent / "geoben" / "documents"

# table: header=表の1行目を見出し行にする。key_value=見出し行を出さず、各行の1列目を<th>にする(項目と内容の表)
PAGES = [
    {"src": "privacy_policy.md", "out": "privacy.html", "table": "header"},
    {"src": "tokushoho.md", "out": "tokushoho.html", "table": "key_value"},
]

# 外部からリンクされている見出しのid。公開済みのURLを壊さないよう、見出しの文言を変えたらここも直す
HEADING_IDS = {
    "privacy.html": {"5. データの保存期間と削除": "deletion"},
}

APPENDIX = re.compile(r"^## 付録")
DATE_LINE = re.compile(r"^(制定日|最終改定日|最終更新日):")
UL_ITEM = re.compile(r"^- (.*)$")
OL_ITEM = re.compile(r"^\d+\. (.*)$")
TABLE_SEP = re.compile(r"^\|(\s*:?-+:?\s*\|)+$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
MAIN = re.compile(r"(<main>\n)(.*?)(</main>)", re.S)
GENERATED_NOTE = "  <!-- <main>の中身は scripts/build_policies.py で原本({src})から生成している。手で直さない -->\n"


class SourceError(Exception):
    pass


def inline(text):
    """1行ぶんの本文をHTMLにする。エスケープしてから、リンク・メールアドレス・太字を変換する。"""
    if "`" in text or "<" in text:
        # 原本はHTMLの断片やコードの記法を使わない前提。黙って崩れないよう止める
        raise SourceError(f"対応していない記法があります: {text}")
    out = []
    pos = 0
    # リンクとメールアドレスを先に取り出し、残りの部分だけをエスケープ・太字の変換にかける
    tokens = sorted(
        [(m.start(), m.end(), "link", m) for m in LINK.finditer(text)]
        + [(m.start(), m.end(), "email", m) for m in EMAIL.finditer(text)],
        key=lambda t: t[0],
    )
    for start, end, kind, m in tokens:
        if start < pos:
            continue  # リンクの中のメールアドレスなど、重なったもの
        out.append(plain(text[pos:start]))
        if kind == "link":
            out.append(f'<a href="{html.escape(m.group(2))}" rel="noopener">{plain(m.group(1))}</a>')
        else:
            addr = html.escape(m.group(0))
            out.append(f'<a href="mailto:{addr}">{addr}</a>')
        pos = end
    out.append(plain(text[pos:]))
    return "".join(out)


def plain(text):
    return BOLD.sub(r"<strong>\1</strong>", html.escape(text, quote=False))


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render(md, table_style, heading_ids):
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if APPENDIX.match(line):
            lines = lines[:i]
            break
    while lines and lines[-1].strip() in ("", "---"):
        lines.pop()

    out = []
    used_ids = set()
    seen_h1 = False
    seen_h2 = False
    first_para = True
    seen_lead = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.startswith(">"):
            while i < len(lines) and lines[i].startswith(">"):
                i += 1
            continue

        m = re.match(r"^(#{1,3}) (.+)$", line)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                if seen_h1:
                    raise SourceError("# 見出しが2つあります")
                seen_h1 = True
            if level == 2:
                seen_h2 = True
            hid = heading_ids.get(text)
            attr = f' id="{hid}"' if hid else ""
            if hid:
                used_ids.add(text)
            if level > 1 and out and out[-1]:
                out.append("")
            out.append(f"  <h{level}{attr}>{inline(text)}</h{level}>")
            i += 1
            continue

        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            if len(block) < 2 or not TABLE_SEP.match(block[1].strip()):
                raise SourceError(f"表の2行目が区切り行ではありません: {block[0]}")
            header, rows = split_row(block[0]), [split_row(r) for r in block[2:]]
            out.append('  <div class="table-wrap">')
            out.append("    <table>")
            if table_style == "header":
                out.append("      <tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>")
                for r in rows:
                    out.append("      <tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            else:
                for r in rows:
                    if len(r) != 2:
                        raise SourceError(f"項目と内容の表は2列にしてください: {r}")
                    out.append(f"      <tr><th>{inline(r[0])}</th><td>{inline(r[1])}</td></tr>")
            out.append("    </table>")
            out.append("  </div>")
            continue

        for pattern, tag in ((UL_ITEM, "ul"), (OL_ITEM, "ol")):
            if pattern.match(line):
                out.append(f"  <{tag}>")
                while i < len(lines) and pattern.match(lines[i]):
                    out.append(f"    <li>{inline(pattern.match(lines[i]).group(1))}</li>")
                    i += 1
                if i < len(lines) and lines[i].strip():
                    raise SourceError(f"リストの直後に空行がありません: {lines[i]}")
                out.append(f"  </{tag}>")
                break
        else:
            if line.startswith(("#", "---", "*", "+", " ", "\t")):
                raise SourceError(f"対応していない記法があります: {line}")
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", ">", "#", "- ")):
                para.append(lines[i].strip())
                i += 1
            if first_para and all(DATE_LINE.match(p) for p in para):
                out.append(f'  <p class="date">{"<br>".join(inline(p) for p in para)}</p>')
                out.append("")
            elif seen_h1 and not seen_h2 and not seen_lead:
                seen_lead = True
                out.append(f'  <p class="lead">{"".join(inline(p) for p in para)}</p>')
            else:
                out.append(f"  <p>{''.join(inline(p) for p in para)}</p>")
            first_para = False
            continue

    missing = set(heading_ids) - used_ids
    if missing:
        raise SourceError(f"idを付ける見出しが原本にありません(HEADING_IDSを直す): {', '.join(sorted(missing))}")
    if not seen_h1:
        raise SourceError("# 見出しがありません")
    return "\n".join(out) + "\n"


def build(page, src_dir):
    src = src_dir / page["src"]
    out_path = ROOT / page["out"]
    template = out_path.read_text(encoding="utf-8")
    if len(MAIN.findall(template)) != 1:
        raise SourceError(f"{page['out']} に <main> がちょうど1つありません")

    body = GENERATED_NOTE.format(src=page["src"]) + render(
        src.read_text(encoding="utf-8"), page["table"], HEADING_IDS.get(page["out"], {})
    )
    result = MAIN.sub(lambda m: m.group(1) + body + m.group(3), template)

    old_ids = set(re.findall(r'<h\d id="([^"]+)"', template))
    new_ids = set(re.findall(r'<h\d id="([^"]+)"', result))
    if old_ids - new_ids:
        raise SourceError(f"{page['out']} の見出しのidが消えます(公開URLが壊れる): {', '.join(sorted(old_ids - new_ids))}")
    return out_path, template, result


def describe_source(src_dir):
    try:
        info = subprocess.run(
            ["git", "-C", str(src_dir), "log", "-1", "--format=%h %cd %s", "--date=short", "--", "."],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", str(src_dir), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(src_dir), "status", "--porcelain", "--", "."],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return f"{branch} / {info}" + (" (コミットしていない変更あり)" if dirty else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "(gitの情報を取れませんでした)"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("src", nargs="?", default=str(DEFAULT_SRC), help="原本のフォルダ(既定: ../geoben/documents/)")
    parser.add_argument("--check", action="store_true", help="書き換えずに、公開ページが原本と一致するかだけ確かめる")
    args = parser.parse_args()

    src_dir = Path(args.src).expanduser().resolve()
    if not src_dir.is_dir():
        sys.exit(f"原本のフォルダが見つかりません: {src_dir}")
    print(f"原本: {src_dir}")
    print(f"      {describe_source(src_dir)}")

    try:
        results = [build(page, src_dir) for page in PAGES]
    except SourceError as e:
        sys.exit(f"エラー: {e}")

    changed = [path for path, old, new in results if old != new]
    if args.check:
        for path in changed:
            print(f"原本と食い違っています: {path.name}(python3 scripts/build_policies.py で生成し直す)")
        sys.exit(1 if changed else 0)

    for path, old, new in results:
        if old != new:
            path.write_text(new, encoding="utf-8")
    if not changed:
        print("変更なし(公開ページは原本と一致しています)")
        return
    print(f"更新しました: {', '.join(p.name for p in changed)}\n", flush=True)
    subprocess.run(["git", "-C", str(ROOT), "--no-pager", "diff", "--", *[p.name for p in changed]])


if __name__ == "__main__":
    main()
