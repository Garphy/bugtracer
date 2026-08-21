# BugTracer 2.0 极速缺陷跟踪系统

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://www.python.org/)
[![Vue: 3.x](https://img.shields.io/badge/Vue-3.x-42b883.svg)](https://vuejs.org/)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io/)

> 现代化轻量重构版 | 35px 极高密度交互 | 全键盘驱动 | Markdown & 图文混排 | SQLite & MySQL 双兼容 | 原生支持 AI Agent (MCP 协议)

---

## 🌟 为什么选择 BugTracer 2.0？

市面上的缺陷与项目管理工具普遍偏“重”，操作层级多、界面留白大、提单与流转阻力高。
**BugTracer** 专为追求极致效率的研发团队和 AI 智能体设计，传承高密度轻量哲学：

1. **极低操作阻力 (Zero-Friction UX)**：
   * **35px 紧凑列表**：一屏容纳数十条缺陷，无冗余留白；
   * **1 秒流转 (Hover Tick & Flagger)**：鼠标悬浮状态 Badge 展示 `✓ 解决` 动态提示，点击一键流转；悬浮 Bug ID 弹出全状态流转浮层；
   * **全量键盘快捷键**：
     * `Ctrl + \`` (或 `Ctrl + ~`)：随时唤起新建 Bug 弹窗；
     * `Ctrl + Enter`：输入框内直接快速提交；
     * `Esc`：快速关闭弹窗/浮层；
     * `< 上一条` / `下一条 >`：弹窗内免关闭连续评审；
   * **零步骤贴图 (`Ctrl + V`)**：直接粘贴剪贴板截图自动上传并嵌入附件；支持文件拖拽上传；
   * **一键导出列表**：点击 `📋 [复制列表]` 一键将当前页缺陷以整洁纯文本复制到剪贴板。

2. **标准 Markdown 渲染与智能图文混排**：
   * 完整支持标题（`#`）、代码块、列表、表格、引用等 Markdown 语法；
   * 正文中直接输入 `图1`、`图2` 或 `![图1](...)`，自动内嵌对应附件截图并支持点击大图预览；
   * 提单/编辑时支持 `[实时预览 Markdown / 切换编辑]`。

3. **双数据库引擎开箱即用 (SQLite & MySQL)**：
   * **默认 SQLite**：零配置单文件数据库，无需安装任何数据库服务，解压即跑；
   * **无缝切 MySQL**：在 `.env` 中修改连接串即可切换到 MySQL / MariaDB，系统自动建表与初始化。

4. **原生 AI Agent (MCP 协议) 深度协同**：
   * 原生内置 **Model Context Protocol (MCP)** 服务（支持 STDIO 与 SSE 双通道）；
   * 让 Cursor、Claude Desktop、Antigravity 等编程智能体能够直接读取项目上下文、检索 Bug、提交缺陷、修改状态与追加技术评论。

5. **多维统计看板与导出**：
   * 14 天新增 vs 解决趋势图（ECharts）、状态分布饼图、成员处理负荷矩阵表，支持 CSV 导出与打印视图。

---

## 🚀 快速启动与部署

系统采用**单端口一体化架构**，后端 FastAPI 自动托管前端静态产物，单个命令即可启动全套服务。

### 方式一：本地 Python 极速启动（推荐）

#### 1. 克隆仓库与创建虚拟环境 (Python 3.10+)
```bash
git clone https://github.com/Garphy/bugtracer.git
cd bugtracer

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows 用户
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动服务 (数据库自动初始化)
```bash
python run.py
```
> **提示**：系统首次启动时会自动创建 SQLite 数据库（存放在 `./data/bugtracer.db`）、建表并初始化默认管理员账号及公共项目，无需手动执行 SQL。

#### 4. 访问系统
* **工作台访问地址**：`http://localhost:5002`
* **默认管理员账号**：`admin`
* **默认管理员密码**：`123456`
* **API 文档 (Swagger UI)**：`http://localhost:5002/docs`
* **MCP SSE 端点**：`http://localhost:5002/mcp`

---

### 方式二：Docker / Docker Compose 一键启动

无需配置 Python 环境，直接通过 Docker 容器化运行：

```bash
docker-compose up -d --build
```

启动后即可通过浏览器访问 `http://localhost:5002`。
数据与上传文件会自动持久化挂载在宿主机的 `./data` 与 `./uploads` 目录中。

---

## ⚙️ 数据库配置 (SQLite / MySQL)

系统通过项目根目录的 `.env` 文件进行配置。复制配置模板即可开始自定义：

```bash
cp .env.example .env
```

### 选项 A：使用默认 SQLite（推荐）
保持 `.env` 中的默认配置即可：
```ini
DATABASE_URL=sqlite+aiosqlite:///./data/bugtracer.db
```

### 选项 B：切换至 MySQL / MariaDB
1. 在 MySQL 中创建好空数据库（字符集推荐 `utf8mb4`）：
   ```sql
   CREATE DATABASE bugtracer DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. 在 `.env` 中配置连接串：
   ```ini
   DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/bugtracer?charset=utf8mb4
   ```
3. 启动服务 `python run.py`，系统将自动在 MySQL 中完成建表和默认数据填充。

---

## 🛠️ 数据库运维与演示数据填充

系统提供了独立的数据库管理 CLI 脚本：

```bash
# 1. 仅初始化/同步表结构
python scripts/init_db.py

# 2. 初始化并填充示例数据（生成演示缺陷、开发与测试角色）
python scripts/init_db.py --seed-demo

# 3. 重置并清空数据库（⚠️ 危险操作，请谨慎使用）
python scripts/init_db.py --reset
```

---

## 🤖 AI Agent (MCP 协议) 接入指南

BugTracer 2.0 内置了 8 大标准化 MCP 工具，可供大模型编程智能体直接接入人机协同：

### 1. Cursor 接入配置
1. 打开 Cursor：`Settings` -> `Features` -> `MCP Servers` -> 点击 `+ Add New MCP Server`；
2. 填写配置：
   * **Name**：`bugtracer`
   * **Type**：`command` (stdio)
   * **Command**：
     ```bash
     /绝对路径/bugtracer/.venv/bin/python /绝对路径/bugtracer/run_mcp_stdio.py
     ```

### 2. Claude Desktop 接入配置
编辑本地 Claude 配置文件（`claude_desktop_config.json`）：
```json
{
  "mcpServers": {
    "bugtracer": {
      "command": "/绝对路径/bugtracer/.venv/bin/python",
      "args": [
        "/绝对路径/bugtracer/run_mcp_stdio.py"
      ]
    }
  }
}
```

### 3. Antigravity / 通用 Agent 配置
* **Transport**: `stdio`
* **Command**: `/path/to/.venv/bin/python`
* **Args**: `["/path/to/run_mcp_stdio.py"]`

### 4. 内置 MCP 工具集清单
| 工具名称 | 功能描述 |
| :--- | :--- |
| `list_projects` | 获取所有项目列表及活动缺陷总览 |
| `get_project_context` | 获取指定项目的模块结构、成员列表及上下文 |
| `query_bugs` | 检索缺陷列表（支持快捷搜索语法与多状态过滤） |
| `get_bug_detail` | 获取缺陷完整详情、版本、附件清单、技术讨论与审计历史 |
| `create_bug` | 智能体直接提交缺陷或任务（支持 Markdown 与图文混排） |
| `update_bug_status` | 流转缺陷状态（如开发修复后设为 `fixed=4` 或验收后设为 `closed=0`） |
| `add_bug_comment` | 为缺陷追加技术方案分析、跟进说明或修复推演评论 |
| `get_project_stats` | 获取项目整体质量统计报表与人员负荷分析 |

---

## 🔍 快捷搜索语法速查

在顶部搜索框输入以下格式即可快速过滤：
* `102` 或 `102,103`：查找指定 ID 的 Bug（单 ID 自动弹出详情浮层）。
* `(用户ID)`：查找此用户提出的 Bug，如 `(1)` 或 `(admin)`。
* `{用户ID}`：查找指派给此用户的 Bug，如 `{2}` 或 `{coder1}`。
* `!{用户ID}`：查找非此用户处理的 Bug，如 `!{2}`。
* `{2026-08-01~2026-08-21}`：查找变更时间在此区间的 Bug。
* `关键词`：模糊匹配 Bug 描述与版本。
* **状态筛选技巧**：在状态复选框上**双击**任意一项，可立即单选该状态！

---

## 👨‍💻 前端二次开发 (可选)

如需修改前端源码进行二次开发：
```bash
cd frontend
npm install
npm run dev
```
开发服务器将运行在 `http://localhost:5173`，自动代理 API 请求至后端的 5002 端口。
修改完成后执行：
```bash
npm run build && cp -r dist/* ../backend/app/static/
```
即可同步打包并更新单端口托管的生产静态产物。

---

## 📄 开源许可证 (License)

本项目采用 [GNU General Public License v3.0 (GPL-3.0)](LICENSE) 开源许可证。

Copyright (C) 2026 Garphy.
