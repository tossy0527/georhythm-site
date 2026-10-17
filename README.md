# comolog-site

「Comolog」のアプリ紹介ページ(GitHub Pages)。ビルド工程のない静的HTML/CSSです。

- `index.html` — アプリ紹介(1ページ完結。CSS・JSはすべてこのファイルに内蔵)
- `privacy.html` — プライバシーポリシー(`<main>`の中身は原本から生成。下記「ポリシーのページを更新する」)
- `tokushoho.html` — 特定商取引法に基づく表記(同上)
- `scripts/build_policies.py` — ポリシーのページを原本から生成するスクリプト
- `sitemap.xml` — Google Search Console に送信する用
- `assets/` — アイコン・OGP画像・スクリーンショット

## スクリーンショットを実写に差し替える

ページ内の4つのスマホ画面は、今はHTML/CSSで描いたモックです。次のファイル名で画像を置くと、**HTMLを編集せずに**自動でモックの代わりに表示されます(ファイルが無いあいだはモックのまま)。

| ファイル | 表示される場所 |
|---|---|
| `assets/screenshots/home.png` | ヒーローのホーム画面 |
| `assets/screenshots/report.png` | 画面紹介のレポート |
| `assets/screenshots/place.png` | 画面紹介の場所の詳細 |
| `assets/screenshots/history.png` | 画面紹介の履歴 |

- 縦長の画面キャプチャをそのまま置けばOK(枠は縦横比 390:820。はみ出す分は下側が切れる)
- 拡張子を変える(`.webp` など)場合は、`index.html` の `<img class="shot" src="...">` を書き換える
- モック側の中身は、アプリの現行仕様(ホーム=前期間比較なし・「今日の合計 : 〜」、レポート=場所の記録帳、場所の詳細=月のドット暦、履歴=除外なし)・場所の色(浅葱・青・レモン)・アプリ内の文言に合わせてある。アプリのUIや文言を変えたら、スクショを撮り直すか、モックを直す

## 入手ボタン

`index.html` の「Google Play で入手」ボタン(ヒーローと最後の2か所。`btn-store` を検索)は、Google Play のストアページ(`https://play.google.com/store/apps/details?id=io.github.tossy0527.georhythm`)へのリンクです。リンク先を変えるときは2か所をそろえて直すこと。Google Play のバッジ画像に差し替える場合は、公式のバッジ素材とガイドラインに従うこと。

## ポリシーのページを更新する

`privacy.html`・`tokushoho.html` の `<main>` の中身は、アプリ側リポジトリ(非公開)の原本 `documents/privacy_policy.md`・`documents/tokushoho.md` から生成します。**HTMLを手で直さず**、原本を直してから生成し直してください。原本はこのリポジトリの GitHub Actions からは読めないので、手元で実行します(Python 3 の標準ライブラリだけで動きます)。

```sh
# アプリ側リポジトリを、原本が最新のブランチ(統合ブランチ)にしておく
python3 scripts/build_policies.py                       # 原本の既定の場所: ../geoben/documents/
python3 scripts/build_policies.py ~/dev/geoben/documents # 場所を指定する場合
python3 scripts/build_policies.py --check               # 書き換えずに、公開ページが原本と一致するかだけ確かめる(一致しなければ終了コード1)
```

- 実行すると、使った原本のブランチと最終コミットを表示し、書き換えたページの差分(`git diff`)を出します。内容を確かめてからコミットしてください
- `<main>` の外側(`<head>`・CSS・パンくず・フッター)は今あるHTMLをテンプレートとしてそのまま残します。見た目を変えるときは、HTMLの `<main>` の外側を直接直します
- 原本のうち、`>` で始まる引用ブロック(作業メモ)と、`privacy_policy.md` の `## 付録` 以降(データセーフティの申告メモ)は公開ページに含めません
- 外部からリンクされている見出しのid(アカウント削除の `privacy.html#deletion`。Play Console の「アカウント削除URL」に使用)は、スクリプト内の `HEADING_IDS` で見出しの文言と対応させています。原本の見出しの文言を変えたらここも直してください(直さずに実行すると、エラーで止まります)
- 原本で使えるのは、見出し・段落・箇条書き・番号付きリスト・表・太字・リンクだけです。それ以外の記法はエラーにして止めます。メールアドレスは自動でリンクにします

## お問い合わせ

フッターの「お問い合わせ」は、押すとダイアログでアドレスを表示し、「アドレスをコピー」「メールアプリで開く」を選べます(JSが使えない環境では通常の `mailto:` リンクとして動きます)。宛先は自動返信フィルタ用の `unagi.laboratory+comolog@gmail.com`。変更するときは `index.html`(フッターのリンク・ダイアログ内の表示とリンクの3か所)と、アプリ側の原本 `documents/privacy_policy.md`(8. お問い合わせ)・`documents/tokushoho.md`(連絡先)を直し、ポリシーのページを生成し直すこと。

## イラストのクレジット

フッターの「紹介画像のイラスト:Loose Drawing」は、Google Play のフィーチャーグラフィック・スクリーンショットと、このページのOGP画像(フィーチャーグラフィックと同じもの)に使ったフリー素材([Loose Drawing](https://loosedrawing.com/))へのお礼です。ページの本文とアプリ本体ではイラストを使っていません。Loose Drawing の規約ではクレジット表記は不要で、「リンクを貼って紹介してもらえると嬉しい」とあるため、リンク付きで載せています(2026-10-10)。これらの画像からイラストを外した場合は、この表記も外すこと。

## 注意

- 見た目のトークン(色・フォント)は、アプリ側 `documents/design.md` の値に揃えています。変えるときは各HTMLの `:root`(`index.html`・`privacy.html`・`tokushoho.html`)を直します。
- フォントは Google Fonts(Klee One / Shippori Mincho / Material Symbols)を読み込みます。閲覧者のIPアドレスがGoogleに送られるため、気になる場合はフォントのセルフホストを検討してください。
- `googlead…html` は Google Search Console の所有権確認用ファイルです。削除しないでください。
- `robots.txt` は置いていません。プロジェクトページ(`/comolog-site/`配下)に置いても検索エンジンに無視される(有効なのはホスト直下のみ)ためで、クロール制御は不要な方針です。
- 収益化(無料/有料の内訳)には、意図的に触れていません。
