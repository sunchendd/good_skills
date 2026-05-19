# OpenCode + Langfuse + DeepSeek 部署指南

## 环境变量 (追加到 `~/.zshrc` 或 `~/.bashrc`)

```bash
# Langfuse
export LANGFUSE_PUBLIC_KEY="pk-lf-39307282-75cc-4cbe-a5a8-81ad556bccb6"
export LANGFUSE_SECRET_KEY="sk-lf-d45386cb-4937-4e83-aadf-b01d11489646"
export LANGFUSE_HOST="http://www.sunchendong.com:3000"
export LANGFUSE_BASE_URL="http://www.sunchendong.com:3000"
export LANGFUSE_BASEURL="http://www.sunchendong.com:3000"
```

```bash
source ~/.zshrc
```

## 安装 OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

## 安装 Langfuse 插件

```bash
npm install -g opencode-plugin-langfuse
```


## 配置文件 `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "deepseek/deepseek-v4-pro",
  "small_model": "deepseek/deepseek-v4-flash",
  "provider": {
    "deepseek": {
      "options": {
        "baseURL": "https://api.deepseek.com/v1"
      }
    }
  },
  "experimental": {
    "openTelemetry": true
  },
  "plugin": [
    "opencode-plugin-langfuse"
  ],
  "permission": {
    "bash": {
      "*": "allow"
    }
  }
}
```

## 本地 `.opencode/package.json` (项目根目录或 home 目录)

```bash
mkdir -p ~/.opencode
cd ~/.opencode
npm init -y
npm install opencode-plugin-langfuse
```

最终 `~/.opencode/package.json` 内容：
```json
{
  "dependencies": {
    "@opencode-ai/plugin": "1.4.0",
    "opencode-plugin-langfuse": "^0.1.8"
  }
}
```

## 验证

```bash
# 检查 Langfuse 健康
curl http://www.sunchendong.com:3000/api/public/health

# 启动 OpenCode
source ~/.zshrc
opencode
```

## 架构

```
DeepSeek API ──→ OpenCode ──→ OpenTelemetry ──→ Langfuse Plugin ──→ http://www.sunchendong.com:3000
```

所有 LLM 调用、工具执行、token 用量自动上报到 Langfuse 项目 `sunchendd`。
