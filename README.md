# 首席财务官 Skill

供本机智能体查询首席财务官本地镜像数据的只读 Skill。支持公司清单、总览、异常、财报、发票、申报表、资金洞见和分析报告预览。

首席财务官需要先运行。Skill 只访问 `127.0.0.1` / `localhost`，不连接各助手的业务明细，不触发同步或任何修改操作。安装和命令说明见 [SKILL.md](SKILL.md)。

GitHub 仓库：[LittleBeaverStudio/CFO](https://github.com/LittleBeaverStudio/CFO)

默认服务端口为 8860，端口被占用时依次顺延。自动发现失败时，在命令中传入 `--base-url http://127.0.0.1:端口`。
