# 使い方
---

## スクリプトの実行
### `src/__main__.py`
```
poetry run python -m src
```

引数は自由に追加

---
## Set up
`poetry` を使用するためインストールが必要

### パッケージインストール
#### プロジェクトのディレクトリ配下に仮想環境を作成するようにする
```
poetry config virtualenvs.in-project true
```

プロジェクトの root 配下に `.venv` ディレクトリが作成され, 仮想環境にかかわるファイルはそこへ格納されるようになる

#### 開発環境
```
poetry install
```

#### 本番環境
```
poetry install --no-dev
```

## テスト
```
poetry run pytest
```

### テストの対象関数
`test_*.py` のファイルにある `test_*`という形式のメソッド.
テストを追加する際は上記の形式

### 処理の遅いテストを実行する場合
```
poetry run pytest -m slow
```

### すべてのテストを実行し, カバレッジを測定する
```
poetry run pytest -v --cov=src/ -m ' '
```

## 文書の build
### set up
```
poetry run sphinx-apidoc -f -o ./docs .
```

以下の条件に適合した場合、上記 set up コマンドをうつ必要がある

- 初めてローカルに `git clone` した
- フォルダの構成を変更した
- 新しく文書化対象のコードを追加した（`index.rst` も変更する必要あり）

### 最新のコードを文書に反映
```
poetry run sphinx-build -b singlehtml ./docs ./docs/_build
```

文書は `docs/_build/index.html` に格納される. webブラウザで開けばHTML形式で確認可能.


## クラス図の作成
```
poetry run pyreverse -o png src/
```

## jupyter の起動
いずれも localhost で起動する

### jupyter notebook
```
poetry run jupyter notebook --allow-root
```

### jupyter lab
```
poetry run jupyter lab --allow-root
```

---

## 仮想環境関連
### パッケージインストール
```
poetry add <module> {--dev}
```

`pyproject.toml` に書き込みが行われるので, commit すること

### 現在の `pyprofect.toml` もとに更新
```
poetry update --no-dev
```

開発環境であれば `--no-dev` を消す

### 削除
```
poetry env remove .venv
```

install で原因不明のエラーが起きたときとかに再セットアップするため
