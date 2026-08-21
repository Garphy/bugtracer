# BugTracer 2.0 极速缺陷跟踪系统

> 现代化重构版 | 紧凑高效 | 全快捷键驱动 | SQLite & MySQL 双兼容 | 原生支持 AI Agent (MCP 协议)

---

## 🌟 核心特性

1. **紧凑极简与极致高频交互**：
   - **高密度列表**：35px 行高紧凑布局，去除冗余留白，一屏纵览数十条缺陷。
   - **1秒状态流转 (Flagger)**：点击/悬浮 Bug ID 弹出悬浮层，1 次点击完成状态变更；点击状态徽章快捷流转。
   - **无缝详情查看与连审**：双击任意行即刻弹出浮层查看，支持 `< 上一条` / `下一条 >` 连续评审。
   - **智能图文混排**：正文中直接输入 `图1`、`图2`，系统自动映射展示上传的对应附件截图。
   - **全量快捷键支持**：
     - `Ctrl + \`` (或 `Ctrl + ~`)：随时唤起新建 Bug 弹窗。
     - `Ctrl + Enter`：输入框内直接快速提交。
     - `Esc`：快速关闭弹窗/浮层。
     - `Ctrl + V`：**直接粘贴剪贴板截图**，自动上传并追加为附件。
     - 拖拽文件到弹窗直接自动上传。

2. **双数据库无缝支持 (SQLite & MySQL)**：
   - 默认采用 **SQLite** 单文件数据库（开箱即用，免装数据库服务）。
   - 只需在 `.env` 中修改 `DATABASE_URL`，即可一键切换到 **MySQL / MariaDB**。

3. **单端口一体化极简部署**：
   - 生产模式下由 Python FastAPI 直接托管 Vue 3 编译前端，单个命令 `python run.py` 即可单端口运行全套系统。

4. **原生 AI Agent (MCP 协议) 赋能**：
   - 内置 **Model Context Protocol (MCP)** 服务（支持 STDIO 与 SSE 双通道）。
   - 支持让 AI Agent（如 Claude Desktop, Cursor, Antigravity 等）直接连接 BugTracer 进行需求分析、查 Bug、提 Bug、更新状态与追加技术评论。

5. **多维统计报表与周报导出**：
   - 全项目质量总览看板、14天新增 vs 解决趋势图（ECharts）、状态分布饼图、成员处理负荷矩阵表。
   - 支持一键导出 Excel 兼容的 CSV 文件与打印视图。

---

## 🚀 快速启动

### 方式一：本地 Python 极速运行（推荐）

1. **准备环境** (Python 3.10+):
   ```bash
   # 1. 创建并激活虚拟环境
   python3 -m venv .venv
   source .venv/bin/activate  # Windows 用户运行: .venv\Scripts\activate

   # 2. 安装依赖
   pip install -r backend/requirements.txt
   ```

2. **启动服务**:
   ```bash
   python run.py
   ```

3. **访问系统**:
   - 浏览器打开：`http://localhost:5002`
   - **初始管理员账号**：`admin` / **密码**：`123456`
   - **API 文档 (Swagger)**：`http://localhost:5002/docs`
   - **MCP SSE 端点**：`http://localhost:5002/mcp`

---

### 方式二：Docker 一键启动

```bash
docker-compose up -d --build
```
启动后直接访问 `http://localhost:5002` 即可。

---

## 🤖 AI Agent (MCP) 接入配置

BugTracer 2.0 提供完整的 MCP Tools，供大模型智能体（LLM Agent）自动检索、跟踪与修复 Bug。

### 1. Claude Desktop 配置 (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "bugtracer": {
      "command": "/绝对路径/bugtracer/.venv/bin/python",
      "args": ["/绝对路径/bugtracer/run_mcp_stdio.py"]
    }
  }
}
```

### 2. Cursor / Antigravity 配置
- **Transport**: `stdio`
- **Command**: `python`
- **Args**: `["run_mcp_stdio.py"]`

### 3. MCP 工具集清单
| 工具名称 | 功能描述 |
| :--- | :--- |
| `list_projects` | 获取所有有效项目列表及活动缺陷概览 |
| `get_project_context` | 获取项目的模块清单、成员分配及上下文 |
| `query_bugs` | 检索缺陷列表（支持状态、模块、指派人及高级搜索语法） |
| `get_bug_detail` | 获取缺陷完整描述、版本、附件清单、讨论评论及审计记录 |
| `create_bug` | 提交/创建新的缺陷或开发任务（支持 Markdown 与图文混排） |
| `update_bug_status` | 修改缺陷状态（如标记为已解决 fixed=4 或关闭 closed=0） |
| `add_bug_comment` | 追加技术方案分析、跟进说明或修复日志评论 |
| `get_project_stats` | 获取项目整体质量统计概览与负荷分布 |

---

## 🔍 智能搜索语法速查

在顶部搜索框输入以下格式即可快速过滤：
- `102` 或 `102,103`：查找指定 ID 的 Bug（单 ID 自动弹出详情浮层）。
- `(用户ID)`：查找此用户提出的 Bug，如 `(1)`。
- `{用户ID}`：查找指派给此用户的 Bug，如 `{2}`。
- `!{用户ID}`：查找非此用户处理的 Bug，如 `!{2}`。
- `{2026-01-01~2026-02-01}`：查找变更时间在此区间的 Bug。
- `关键词`：模糊匹配 Bug 描述与版本。
- **状态筛选技巧**：在状态复选框上**双击**任意一项，可立即单选该状态！

---

## 🛠️ 前端二次开发 (可选)

如需对前端界面进行独立调试与二次开发：
```bash
cd frontend
npm install
npm run dev
```
前端开发服务器将运行在 `http://localhost:5173`，自动代理 API 请求至后端的 8000 端口。
修改完成后执行 `npm run build && cp -r dist/* ../backend/app/static/` 即可同步更新生产静态产物。
