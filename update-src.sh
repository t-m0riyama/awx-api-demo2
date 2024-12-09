#!/bin/bash

HISTORY_FILE=$(dirname ${0})/.last_versions
UPDATE_DATE=$(date "+%Y/%m/%d %H:%M:%S")
CURRENT_COMMIT=$(git log -n 1 --date=short --format="%H @%cd")

# 最新コードをリポジトリから取得
git pull \
    && echo "${UPDATE_DATE} ${CURRENT_COMMIT}" >> ${HISTORY_FILE} \
    && git log -n 1 --oneline
    # && sudo ./fix-permissions.sh

if [ ! "${?}" == "0" ]; then
    echo "[ERROR] コードの最新化に失敗しました" >&2
    echo "[ERROR] 処理を中止します" >&2
    exit 1
fi

exit 0

