#!/bin/bash

HISTORY_FILE=$(dirname ${0})/.last_versions
UPDATE_DATE=$(date "+%Y/%m/%d %H:%M:%S")

if [ ! -f ${HISTORY_FILE} ]; then
    echo "[ERROR] バージョン情報の履歴ファイルが見つかりません" >&2
    echo "[ERROR] 処理を中止します" >&2
    exit 1
fi

LAST_COMMIT=$(tail -1 ${HISTORY_FILE} | awk '{ print $3; }')

if [ "${LAST_COMMIT}" == "" ]; then
    echo "[ERROR] ロールバック対象のバージョン情報を判定できません" >&2
    echo "[ERROR] 処理を中止します" >&2
    exit 1
fi

# アップデート前のコミットにロールバック
git reset --hard ${LAST_COMMIT}
# && sudo ./fix-permissions.sh

if [ ! "${?}" == "0" ]; then
    echo "[ERROR] コードの最新化に失敗しました" >&2
    echo "[ERROR] 処理を中止します" >&2
    exit 1
fi

exit 0

