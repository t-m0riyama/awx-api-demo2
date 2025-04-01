#!/bin/bash

set -e

APP_DIR="/app"
DB_PATH="./data/iaas_requests.sqlite3"
BACKUP_DIR="./data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_IMAGE=t-m0riyama/awx-api-demo2:latest
ESC=$(printf '\033')

cat <<EOS
データベースを初期化します...

***この処理で、既存のデータは全て削除されます***

  初期化処理は、以下の流れで実行されます

    1. アプリケーションの停止
    2. 既存データベースのバックアップ（スキップ可能）
    3. 既存データベースの削除
    4. データベースの再作成（初期化）
EOS

# 既存のデータベースファイルが存在する場合
if [ -f "$DB_PATH" ]; then
    # アプリケーションの停止
    read -p $'\e[32mアプリケーションを停止します。処理を継続しますか？ (y/N):\e[m ' shutdown_confirm
    if [[ $shutdown_confirm =~ ^[Yy]$ ]]; then
        echo "アプリケーションを停止中..."
        docker compose down
	if [[ "0" == "$?" ]]; then
            echo "  >> アプリケーションを停止しました"
	else
            echo "  >> アプリケーションの停止に失敗しました"
	    echo "処理を中止しました"
	    exit 1
	fi
    else
	echo "処理を中止しました"
	exit 1
    fi

    # バックアップを取得するかどうかを確認
    read -p $'\e[32m既存データベースのバックアップを取得しますか？ (y/N):\e[m ' backup_confirm
    if [[ $backup_confirm =~ ^[Yy]$ ]]; then
        echo "バックアップを作成中..."
	mkdir -p $BACKUP_DIR
	if [[ "0" == "$?" ]]; then
            echo "  >> バックアップディレクトリの作成に成功しました"
        else
            echo "  >> バックアップディレクトリの作成に失敗しました"
            echo "処理を中止しました"
            exit 1
        fi

        cp "$DB_PATH" "$BACKUP_DIR/iaas_requests_${TIMESTAMP}.sqlite3"
	if [[ "0" == "$?" ]]; then
            echo "  >> バックアップの作成に成功しました"
        else
            echo "  >> バックアップの作成に失敗しました"
            echo "処理を中止しました"
            exit 1
        fi
        echo "  >> バックアップの作成が完了しました: $BACKUP_DIR/iaas_requests_${TIMESTAMP}.sqlite3"
    else
        echo "  >> バックアップの作成をスキップしました"
    fi

    # データベースの削除を確認
    read -p $'\e[32m既存データベースの削除と再作成を行います。処理を継続しますか？ (y/N):\e[m ' delete_confirm
    if [[ ! $delete_confirm =~ ^[Yy]$ ]]; then
        echo "処理を中止しました"
        exit 1
    fi

    /bin/rm -f "$DB_PATH"
    if [[ "0" == "$?" ]]; then
        echo "  >> 既存データベースの削除に成功しました: $DB_PATH"
    else
        echo "  >> 既存データベースの削除に失敗しました: $DB_PATH"
        echo "処理を中止しました"
        exit 1
    fi

else
    echo "  >> データベースファイルが存在しません"
    echo "処理を中止しました"
    exit 1
fi

# Alembicのマイグレーションを実行
printf "${ESC}[32m%sデータベースを再作成します: $DB_PATH${ESC}[m\n"
echo 
docker run -v ./data:/app/data ${CONTAINER_IMAGE} bash -c "cd /app; alembic upgrade head"

if [[ "0" == "$?" ]]; then
    echo "  >> データベースの再作成に成功しました"
else
    echo "  >> データベースの再作成に失敗しました"
    echo "処理を中止しました"
    exit 1
fi
echo "データベースの初期化が完了しました"

