# ドメイン移管手順：codey.bhrtaym-blog.com セットアップ

`bhrtaym-blog.com` の NS を **ConoHa → Cloudflare** に変更し、`codey.bhrtaym-blog.com` を Codey Daily の独自ドメインとして接続する手順書。

> ⚠️ 既存の WordPress (ConoHa) と Email (mail90.conoha.ne.jp) はそのまま動作させたまま、NS のみ移管する。

---

## 移管前に保全すべき既存DNS（必須）

Cloudflare のサイト追加時、自動スキャンが以下を**すべて**拾うことを必ず確認すること：

| Type | Name | Value |
|---|---|---|
| A | `@` (bhrtaym-blog.com) | `160.251.71.122` |
| A | `www` | `160.251.71.122` |
| MX | `@` | `10 mail90.conoha.ne.jp.` |
| TXT | `@` | `v=spf1 include:_spf.conoha.ne.jp ~all` |
| TXT | `default._domainkey` | `v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqXBoAMlhkbCQk7xJJ8UVV/WMW0Eo8B1CXog4Hv08n+cmAy8FGHv2ETcUn/IZFEsQUVE+oI7tuDAORXWl9E7hHGbO5QagsQEo4uGkIrXKA3gK8fDoGmZ2xlkcOLZs+vODMzwVqXaE2Rgfyn4SLJjDJUk27YqVcuiHwtkQqNToIj+7V+bl8bnnhgNmgk8szyeZ9YuhLVuco2Gi+GaDL+NMEsavpcVJLbvVbs9G92Ntgz/kTKLAY1uZAMTgoJ3JOOYQ8NipjbO1wHfUWvVJZ40abV2EV+omHkXP7HWxgo4HvSIfn/80RXG2CuXndgJXhZNTsQyLcDdVoOd9Hlw/Tk85pQIDAQAB` |

これらが**一つでも欠けると WordPress またはメールが止まる**ので注意。

---

## 手順

### Step 1. Cloudflareにサイト追加

1. https://dash.cloudflare.com にログイン
2. 「**サイトを追加**」（Add a site）→ ドメイン入力欄に `bhrtaym-blog.com`
3. プラン選択画面で **Free**（無料）を選択
4. Cloudflare が既存DNSを自動スキャン → 表示されるレコード一覧を確認
   - 上記5レコードがすべて拾われていること
   - 拾い漏れがあれば「**Add record**」で手動追加
5. 「**Continue**」で進む

### Step 2. プロキシ設定（重要）

各レコードの「Proxy status」を以下の通り設定：

| Record | Proxy status | 理由 |
|---|---|---|
| A `@` → `160.251.71.122` | **🟠 Proxied** | Cloudflareが前段に立つ＝WAF/キャッシュ恩恵 |
| A `www` → `160.251.71.122` | 🟠 Proxied | 同上 |
| MX `@` → `mail90.conoha.ne.jp` | **🔘 DNS only** | メールはプロキシ不可 |
| TXT (SPF, DKIM) | （Proxyボタンなし） | TXTは設定不要 |

> Proxied (🟠) にすると Cloudflare の SSL/CDN を経由するが、WordPressが「Cloudflare経由のリクエストか判定」する設定が必要な場合は最初は DNS only (🔘) にして動作確認してから Proxied 化する選択肢もあり。

### Step 3. ネームサーバー（NS）を取得

セットアップ画面の最後に「Cloudflare のネームサーバー」が表示される。例：

```
yyy.ns.cloudflare.com
zzz.ns.cloudflare.com
```

**この2つを必ずメモ**しておく。

### Step 4. ConoHa側でNSを変更

1. https://manage.conoha.jp/ にログイン
2. メニュー「**DNS**」→ ドメイン一覧から `bhrtaym-blog.com`
3. **ネームサーバー変更**画面で、上記の2つのCloudflareのNSに置き換え
   - 既存の `ns-a1.conoha.io` `ns-a2.conoha.io` `ns-a3.conoha.io` を上書き
4. 保存
5. **TTL を低めに設定**（300秒程度）すると伝播が早い（ConoHa側で可能なら）

### Step 5. 伝播待ち（最大24時間、通常1〜数時間）

Cloudflareダッシュボードを確認：
- 「**Active**」ステータスになるまで待つ
- メールで「Your domain is now active on Cloudflare」が届く

進行確認コマンド（ローカル）：
```bash
dig +short NS bhrtaym-blog.com
# → cloudflare.com のNSが返れば完了
```

### Step 6. Workers Custom Domain 設定

1. Cloudflare Dashboard → **Workers & Pages** → **codey-daily** Worker を選択
2. **Settings** タブ → **Domains & Routes** → **Add** → **Custom Domain**
3. ドメイン入力：`codey.bhrtaym-blog.com`
4. 「**Add Domain**」
5. Cloudflareが自動で：
   - `codey` の CNAME 風AAAAレコードを作成
   - SSL証明書発行（数秒〜数分）

### Step 7. 動作確認

```bash
curl -I https://codey.bhrtaym-blog.com
# → HTTP/2 200 が返ればOK
```

ブラウザで `https://codey.bhrtaym-blog.com` を開いて Codey Daily のトップページが表示されることを確認。

### Step 8. コード側を新ドメインに切替

Codey Daily のリポジトリで以下3ファイルを更新（私が即対応可）：

```diff
- # src/lib/site-config.ts
- export const SITE_URL = 'https://codey-daily.hrtaym1114.workers.dev';
+ export const SITE_URL = 'https://codey.bhrtaym-blog.com';

- # astro.config.mjs
- site: 'https://codey-daily.hrtaym1114.workers.dev',
+ site: 'https://codey.bhrtaym-blog.com',

- # public/robots.txt
- Sitemap: https://codey-daily.hrtaym1114.workers.dev/sitemap-index.xml
+ Sitemap: https://codey.bhrtaym-blog.com/sitemap-index.xml
```

ビルド＆デプロイ → 全OG画像URL・sitemap・hreflangが新ドメインに反映。

### Step 9. workers.dev からのリダイレクト（推奨）

旧URL（workers.dev）にアクセスされた場合は新URLにリダイレクトする：

`src/server.ts` に簡易リダイレクト追加（Hono middleware）：

```typescript
app.use('*', async (c, next) => {
  if (c.req.header('host') === 'codey-daily.hrtaym1114.workers.dev') {
    const newUrl = `https://codey.bhrtaym-blog.com${c.req.path}${c.req.url.split('?')[1] ? '?' + c.req.url.split('?')[1] : ''}`;
    return c.redirect(newUrl, 301);
  }
  await next();
});
```

これでSEOの旧URL評価が新URLに引き継がれる。

### Step 10. Search Console 登録（タスク #4）

新ドメインで Google Search Console に登録 → sitemap送信 → インデックス申請。

---

## ロールバック手順（万が一既存ブログが落ちた場合）

1. ConoHa の DNS設定画面で **NSを元に戻す**（`ns-a*.conoha.io`）
2. 数時間〜24時間で旧NSに復帰
3. その間メールが届かない可能性はあるが、SMTP送信元は通常リトライするので致命的損失は最小

---

## チェックリスト

- [ ] Step 1: Cloudflareにbhrtaym-blog.com追加完了
- [ ] Step 2: 5つの既存DNSレコードがCloudflare上に存在することを確認
- [ ] Step 3: Cloudflare NS をメモ
- [ ] Step 4: ConoHaでNS変更
- [ ] Step 5: Cloudflare「Active」確認 ＋ `dig` で確認
- [ ] Step 6: codey.bhrtaym-blog.com を Workers Custom Domain 追加
- [ ] Step 7: ブラウザで動作確認
- [ ] Step 8: コード側を新ドメインに更新（Claude側で対応可）
- [ ] Step 9: workers.dev リダイレクト追加（Claude側で対応可）
- [ ] Step 10: Search Console 登録（タスク #4）
- [ ] **Step 11: Google OAuth クライアント設定を新ドメインに更新** ⚠️ 忘れがち
  - Google Cloud Console → APIs & Services → 認証情報
  - OAuth 2.0 クライアント ID（`663283652105-...`）を編集
  - 承認済みJavaScript生成元に `https://codey.bhrtaym-blog.com` 追加
  - 承認済みリダイレクトURIに `https://codey.bhrtaym-blog.com/api/auth/google/callback` 追加
  - 既存の workers.dev エントリは残したまま追加（並存OK）
  - 反映に最大5分かかる
- [ ] **Step 12: 他の3rd-party callback URL更新確認**
  - Stripe / SendGrid / GitHub App など、サードパーティ連携でcallback URLを使うものがあれば全て更新
  - 該当無ければスキップ
- [ ] 1週間後: WordPress（既存ブログ）が問題なく動いているか確認
- [ ] 1週間後: メール送受信が問題ないか確認
