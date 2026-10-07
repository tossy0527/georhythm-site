# georhythm-site

「ジオリズム」のアプリ紹介ページ(GitHub Pages)。ビルド工程のない、手書きの静的HTML/CSSです。

- `index.html` — アプリ紹介(1ページ完結。CSS・JSはすべてこのファイルに内蔵)
- `privacy.html` — プライバシーポリシー(原本はアプリ側リポジトリの `documents/privacy_policy.md`)
- `sitemap.xml` — Google Search Console に送信する用
- `assets/` — アイコン・OGP画像・スクリーンショット

## スクリーンショットを実写に差し替える

ページ内の4つのスマホ画面は、今はHTML/CSSで描いたモックです。次のファイル名で画像を置くと、**HTMLを編集せずに**自動でモックの代わりに表示されます(ファイルが無いあいだはモックのまま)。

| ファイル | 表示される場所 |
|---|---|
| `assets/screenshots/home.png` | ヒーローのホーム画面 |
| `assets/screenshots/report.png` | 画面紹介のレポート |
| `assets/screenshots/place.png` | 画面紹介の場所の詳細 |
| `assets/screenshots/history.png` | 画面紹介のあしあと |

- 縦長の画面キャプチャをそのまま置けばOK(枠は縦横比 390:820。はみ出す分は下側が切れる)
- 拡張子を変える(`.webp` など)場合は、`index.html` の `<img class="shot" src="...">` を書き換える
- モック側の中身は、アプリの現行仕様(ホーム=前期間比較なし・「今日の合計 : 〜」、レポート=場所の記録帳、場所の詳細=月のドット暦、あしあと=除外なし)と場所の色(浅葱・青・レモン)に合わせてある(2026-10-06時点)。アプリのUIを変えたら、スクショを撮り直すか、モックを直す

## 入手ボタン

`index.html` の「Google Play で入手」ボタン(ヒーローと最後の2か所。`btn-store` を検索)は、Google Play のストアページ(`https://play.google.com/store/apps/details?id=io.github.tossy0527.georhythm`)へのリンクです。リンク先を変えるときは2か所をそろえて直すこと。Google Play のバッジ画像に差し替える場合は、公式のバッジ素材とガイドラインに従うこと。

## お問い合わせ

フッターの「お問い合わせ」は、押すとダイアログでアドレスを表示し、「アドレスをコピー」「メールアプリで開く」を選べます(JSが使えない環境では通常の `mailto:` リンクとして動きます)。宛先は自動返信フィルタ用の `unagi.laboratory+georhythm@gmail.com`。変更するときは `index.html`(フッターのリンク・ダイアログ内の表示とリンクの3か所)と `privacy.html`(8. お問い合わせ)、アプリ側原本 `documents/privacy_policy.md` をそろえて直すこと。

## 注意

- 見た目のトークン(色・フォント)は、アプリ側 `documents/design.md` / `documents/design_handsoff` の値に揃えています。変えるときは `index.html` の `:root` だけを直します。
- フォントは Google Fonts(Klee One / Shippori Mincho / Material Symbols)を読み込みます。閲覧者のIPアドレスがGoogleに送られるため、気になる場合はフォントのセルフホストを検討してください。
- `googlead…html` は Google Search Console の所有権確認用ファイルです。削除しないでください。
- `robots.txt` は置いていません。プロジェクトページ(`/georhythm-site/`配下)に置いても検索エンジンに無視される(有効なのはホスト直下のみ)ためで、クロール制御は不要な方針です。
- 収益化(無料/有料の内訳)には、意図的に触れていません。
