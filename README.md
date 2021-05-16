# サーバサイド

# 必要なツール

- Python3
- Poetry
- protoc

# クローン
```
git clone https://github.com/HotODEN/server.git --recursive
poetry install
```

# ビルド

## プロトコルを更新
```
git submodule foreach git pull origin master
protoc --python_out=./ protocol/*.proto
```

## ローカルで実行
```
poetry run python server/main.py
```
