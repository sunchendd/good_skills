#!/bin/bash
# 等待服务就绪

PORT=${1:-8000}
TIMEOUT=${2:-300}
INTERVAL=5

echo "等待服务在端口 ${PORT} 就绪 (超时: ${TIMEOUT}s)..."

ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        echo "服务已就绪!"
        exit 0
    fi

    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    echo "等待中... ${ELAPSED}s"
done

echo "服务启动超时!"
exit 1
