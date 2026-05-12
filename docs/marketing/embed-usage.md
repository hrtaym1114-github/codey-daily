# Codey Daily 埋め込みウィジェット

ブログ・README・社内ドキュメントに「今日のClaude Code機能」カードを埋め込めます。

## iframe 埋め込み（最も簡単）

```html
<iframe
  src="https://codey.bhrtaym-blog.com/embed/today/"
  width="500"
  height="220"
  frameborder="0"
  style="border:0; max-width:100%;"
  title="今日のClaude Code機能 — Codey Daily">
</iframe>
```

## GitHub README 用（画像のみ）

iframe非対応のmarkdown環境では、リンク付き画像で代替：

```markdown
[![今日のClaude Code機能](https://codey.bhrtaym-blog.com/og.png)](https://codey.bhrtaym-blog.com)
```

## ダーク/ライトモード自動対応

`prefers-color-scheme` に基づき自動切替されます。親ページのテーマに馴染みます。

## カスタマイズ

カードは1日1回更新（UTC基準）。背景は透過なので、親ページのスタイルが透けます。
