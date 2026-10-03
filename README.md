# 论文侦探 · Paper Detective

输入一句科学结论，追查它由什么原始研究支持，以及哪里超出了证据。

**这是一个 Codex skill，首版为 v0.1.0。** 它提供可重复的核验流程、证据卡模板和可选的 JSON 报告检查工具。检索与阅读由使用它的助手及现有工具完成；本仓库没有独立模型、网页、小程序或自动后台服务。

[English documentation](README.en.md) · [Skill instructions](paper-detective/SKILL.md) · [Release](https://github.com/BoteXu/paper-detective/releases)

## 能做什么

| 模式 | 输入 | 输出 |
|---|---|---|
| 结论查证 | 一句结论 | 候选原始证据、支持程度、冲突与适用边界 |
| 引用追溯 | 结论 + 来源论文/DOI/全文 | 实际引用链、原始实验与转引中的表述变化 |

每个主张分别核对研究对象、实验类型、独立单位、对照、实际结果和原文位置。效应、受体依赖与直接结合分开判断。相关论文不冒充真实引用来源；动物或细胞实验不自动支持人体疗效；材料不足时保留“不足以判断”。

## 安装

下载 [v0.1.0 的 skill ZIP](https://github.com/BoteXu/paper-detective/releases/download/v0.1.0/paper-detective-v0.1.0.zip)，解压后将内层 `paper-detective` 文件夹放到 `$CODEX_HOME/skills/`；未设置 `CODEX_HOME` 时使用 `~/.codex/skills/`。该文件夹内应直接包含 `SKILL.md`。

也可以克隆仓库后复制 skill 子目录。下面的命令在目标 skill 已存在时会停止，避免覆盖已有版本。

Windows PowerShell：

```powershell
git clone https://github.com/BoteXu/paper-detective.git
$skillBase = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
$skillTarget = Join-Path $skillBase 'paper-detective'
if (Test-Path -LiteralPath $skillTarget) { throw 'paper-detective already exists; inspect it before updating.' }
New-Item -ItemType Directory -Path $skillBase -Force | Out-Null
Copy-Item -LiteralPath './paper-detective/paper-detective' -Destination $skillTarget -Recurse
```

macOS / Linux：

```sh
git clone https://github.com/BoteXu/paper-detective.git
skill_base="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skill_base"
if [ -e "$skill_base/paper-detective" ]; then
  printf '%s\n' 'paper-detective already exists; inspect it before updating.'
else
  cp -R ./paper-detective/paper-detective "$skill_base/"
fi
```

安装后重新开启 Codex 会话；如 skill 列表未刷新，重启客户端。

## 使用

```text
使用 $paper-detective 核验：蛋白 A 通过受体 B 改善心功能。
把效应、受体依赖和直接结合拆开，说明研究对象和证据缺口。
```

```text
使用 $paper-detective 追溯这篇论文中以下句子的引用。
来源：<DOI 或论文链接>
结论：<原句>
请区分实际引用链与独立检索发现的补充证据。
```

上述实体是使用示例，不是真实科研结论。默认最多追溯两层引用、检查十五篇候选文献，用户可以调整。每份报告说明检索边界与未完成分支，不默认声称穷尽证据。

## 工具与可移植性

没有必须安装的 Python 包或必须配置的 Biomni 服务。具备检索、全文阅读和文件工具的助手可执行核心流程；无网络时仅能核验提供的材料。生物医学任务优先发现并复用已配置的 Biomni 直接工具，不另设推理模型；也可使用官方文献数据源。详细路由见 [retrieval.md](paper-detective/references/retrieval.md)。

可选 JSON 报告检查器只使用 Python 3.10+ 标准库：

```sh
python paper-detective/scripts/validate_report.py path/to/report.json
python -m unittest discover -s tests -v
```

检查器可发现悬空来源、证据与主张错接、没有位置的强支持记录、以及把独立检索伪装为引用边等结构问题。**它不能验证原文是否真实、实验是否可靠或科学判断是否正确。** 格式见 [report-format.md](paper-detective/references/report-format.md)。

## 当前验证边界

首版提供结构测试和明确标注的模拟案例，用于检验核验边界。它尚未在人工标注的真实文献集合上完成准确率或科研有效性评估。请勿将模拟案例当作已核实的文献证据，也勿将助手的输出直接当作临床决策依据。

使用时不向外部端点发送未经授权的敏感材料，不在公开仓库提交私有论文、临床信息、凭据或完整工具回执。引用原文和分享全文时遵守许可。

## 仓库结构

- `paper-detective/`：可安装 skill，包含入口、界面元数据、检索指南、输出模板和检查器。
- `examples/`：模拟核验案例与 JSON 演示，不含真实科学验证结果。
- `tests/`：报告一致性与关键边界的自动测试。
- `.github/workflows/validate.yml`：持续检查。

反馈请提供可公开的最小案例、预期行为与实际结果；提交前移除敏感信息。MIT License。
