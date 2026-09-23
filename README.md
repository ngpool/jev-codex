# Jev-Codex

## 現時点で作ったもの

Jev-Codex は、TypeSafe AI の Jev を Codex の判断補助として使うための、画面を持たない小さなツール一式です。Jev に設計や実装そのものを任せるのではなく、Codex がプロジェクトを確認したうえで、選択肢の比較、優先順位付け、基準に沿ったスコア付け、単純な Yes/No 判断が必要な場面で利用する想定です。

- `SKILL.md` — Jevを使う場面、質問の作り方、結果の扱い方をCodexに伝えるスキル定義です。
- `scripts/jev_decide.py` — JSON形式の判断依頼をTypeSafeのAPIに送り、構造化された結果を表示するPythonスクリプトです。
- `README.md` — このプロジェクトの説明と設定手順です。

## まだ行っていないこと

- JevのAPIキーは設定していません。
- APIへの実リクエストは行っていません。
- スクリプトの動作確認は行っていません。
- このスキルをCodexのグローバルスキル領域へインストールしていません。
- 画面やGUIは作っていません。

## 必要なもの

- Python 3.9以降
- TypeSafe AI Jev APIへのアクセスとAPIキー
- スキルに対応したCodex

## APIキーの設定

Codexを起動する環境で `TYPESAFE_API_KEY` を設定してください。APIキーをソースコードやリポジトリに書き込まないでください。

PowerShellの現在のセッションだけに設定する例:

```powershell
$env:TYPESAFE_API_KEY = "your-api-key"
```

## 判断リクエストの実行

このフォルダで、`state` と `questions` を含むJSONを標準入力から渡します。

```powershell
Get-Content request.json -Raw | python scripts/jev_decide.py
```

質問タイプは `choice`（選択肢から選ぶ）、`score`（基準に沿って採点する）、`noul`（Yes/Noの確率判断）です。質問例とCodex向けの利用方針は `SKILL.md` を参照してください。

## どのプロジェクトでも使う

現在のフォルダは `C:\Users\u11b1\jev-codex` です。全プロジェクトでCodexにスキルを認識させるには、このフォルダをCodexのグローバルスキル領域 `~/.codex/skills/jev-codex` に配置し、Codexを再起動してください。スキルの配置だけではAPIキーは設定されません。起動環境で別途 `TYPESAFE_API_KEY` を設定する必要があります。

## 判断結果の扱い

Jevは選択、スコア、確率などの構造化された判断を返します。説明文やコードは生成しません。Codexは結果を根拠の一つとして扱い、プロジェクトの実際の情報と照らし合わせて結論を説明します。確信度だけを正しさの保証として扱ったり、破壊的変更・セキュリティ上重要な操作・デプロイなどの許可に使ったりしません。

## 公式資料

- [TypeSafe AI](https://typesafe.ai/)
- [Jev Quick Start](https://docs.typesafe.ai/introduction/quickstart)
