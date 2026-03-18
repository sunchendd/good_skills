# Open Source Skills

这个目录只管理第三方开源 skill 的安装来源，不存放它们的源码副本。

## 约定

- 仓库根目录：保留自研 skill、共享代码和发布相关内容
- `opensource/`：保存开源 skill 的安装清单和批量安装脚本

## 文件说明

- [sources.txt](./sources.txt)：一行一个 `npx skills add ...` 命令
- [install.ps1](./install.ps1)：Windows 批量安装脚本
- [install.sh](./install.sh)：macOS/Linux 批量安装脚本

## 用法

Windows:

```powershell
pwsh .\opensource\install.ps1
```

macOS / Linux:

```bash
bash ./opensource/install.sh
```

## 更新方式

1. 在 `sources.txt` 中新增、删除或调整开源 skill 安装命令
2. 重新运行安装脚本
3. 如需统一检查更新，可额外运行 `npx skills check` 或 `npx skills update`

## 说明

这里的命令默认带 `-g -y`，用于全局安装并跳过确认提示，方便批量执行。
