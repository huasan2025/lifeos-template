#!/bin/bash
# wikilink-check.sh: 扫描所有 .md，验证每个 [[X]] 解析到至少一个文件
# 用法:
#   bash wikilink-check.sh             # 检查 + 对比基线，delta > 5 则失败
#   bash wikilink-check.sh --baseline  # 保存当前破链数作为基线

set -e
VAULT="${VAULT:-$HOME/Documents/${VAULT_NAME}}"
cd "$VAULT"

BASELINE_FILE="$VAULT/docs/scripts/wikilink-baseline.txt"
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# 收集所有 wikilink target（去掉 #section 和 |alias）
# Obsidian wikilink 不会以空格、$、{、@、^、* 等开头（这些一般是 bash 语法、模板变量、emoji 等）
# 也不会包含未配对的引号或 shell 操作符
links=$(grep -roh --include='*.md' \
    --exclude-dir=.obsidian --exclude-dir=.git \
    --exclude-dir=99-Archive --exclude-dir=Web-Clipper \
    --exclude-dir=06-Conversations --exclude-dir=.gstack \
    --exclude-dir=node_modules \
    '\[\[[^][:space:]$@^*{][^]]*\]\]' . 2>/dev/null | \
    sed 's/^\[\[//; s/\]\]$//; s/#.*//; s/|.*//' | \
    grep -v '^\.\./' | \
    grep -v '^[ -]' | \
    sort -u)

# 收集所有 .md 文件名（不含路径、不含 .md 后缀），用 sed 替代 basename 避免 -f 选项问题
files=$(find . -name '*.md' -type f \
    -not -path './.obsidian/*' -not -path './.git/*' \
    -not -path './99-Archive/*' -not -path './Web-Clipper/*' \
    -not -path './06-Conversations/*' -not -path './.gstack/*' \
    -not -path '*/node_modules/*' 2>/dev/null | \
    sed 's|.*/||; s|\.md$||' | sort -u)

# 检查每个 link 是否能解析
echo "$links" | while IFS= read -r link; do
    [ -z "$link" ] && continue
    base="${link##*/}"
    if ! echo "$files" | grep -Fxq "$base"; then
        echo "BROKEN: [[$link]]"
    fi
done > "$TMPFILE"

count=$(wc -l < "$TMPFILE" | tr -d ' ')

if [ "$1" = "--baseline" ]; then
    echo "$count" > "$BASELINE_FILE"
    echo "✅ 基线已保存: $count 条破链"
    echo "---破链清单 (top 30)---"
    head -30 "$TMPFILE"
    exit 0
fi

baseline=$(cat "$BASELINE_FILE" 2>/dev/null || echo 0)
delta=$((count - baseline))

echo "破链数: $count (基线: $baseline, delta: $delta)"
echo "---破链清单 (top 30)---"
head -30 "$TMPFILE"

if [ "$delta" -gt 5 ]; then
    echo "❌ delta > 5，停止"
    exit 1
fi
echo "✅ 通过"
