# Changelog

All notable changes to the **BugTracer** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.2] - 2026-08-27

### Added
- **项目子模块拖拽排序 (#43)**: 管理后台编辑项目中的子模块列表支持 HTML5 原生鼠标拖拽排序（`GripVertical` 图标手柄 + 实时动态占位高亮），保存项目时自动更新并持久化 `sort_order`，前台首页 Tab 栏与报表页即时按最新顺序生效。
- **URL 查询参数显式绑定项目 ID (#47)**: 前台主页、项目报表等路由全面支持 `?project_id=X`（同时兼容 `?pid=X`），页面初次加载或刷新时最高优先级依据 URL 参数识别项目，彻底解决多标签页打开不同项目互相干扰的问题；切换项目自动 replace 同步至 URL；报表页和管理后台返回主页链接自动保持选中的项目 ID。
- **SQLite WAL 预写日志与并发性能调优**: 为 SQLite 数据库连接挂载 `PRAGMA journal_mode = WAL`、`PRAGMA synchronous = NORMAL` 与 `PRAGMA busy_timeout = 30000`，实现读写完全并发与 30 秒忙等待排队机制，彻底消除并发读写下的 `database is locked` 锁死报错，写入吞吐提升 5~10 倍。
- **SQLite 7 天自动滚动热备系统**: 基于原生 `sqlite3.Connection.backup()` API 实现零停机安全在线热备；FastAPI 后台自动调度（每天凌晨 02:00 定时执行热备 + 启动自检）；自动按日期保留最近 7 天备份并清理过期历史文件；提供独立运维 CLI 工具 `scripts/backup_db.py`（支持手动热备、列表查看、一键灾难恢复与清理）。
- **高并发压测与热备自动化测试套件**: 新增 `backend/tests/test_backup.py`（测试 WAL 模式、高并发多协程并发读写压测、滚动保留 7 天与数据还原校验），自动化测试用例扩充至 14 项。

### Fixed
- **弹层遮罩防误触关闭 (#46)**: 移除提交及缺陷详情弹窗外围半透明遮罩的 `@click.self` 关闭触发事件，防止用户误触外围区域导致未保存的编辑内容丢失；保留右上角 `[✕]`、底部 `[取消]` 按钮与 `Esc` 键关闭。
- **子模块删除真实持久化与安全解绑 (#37)**: 前端 `AdminView` 追踪已删除模块并在保存时发起 `DELETE /api/projects/modules/{id}` 请求；后端 `delete_module` 服务自动解绑关联缺陷的 `module_id` 设为 `NULL`，防止外键冲突。
- **自动化测试数据库沙箱隔离 (#36)**: 在 `backend/tests/conftest.py` 中引入 Session 级别隔离临时数据库 Fixture，彻底杜绝测试用例对开发/生产库生成多余测试账号。
- **子模块创建 Schema 校验修复**: 将 `ModuleCreate` Schema 中的 `project_id` 设为可选，修复前端创建模块报 422 字段缺失错误。

---

## [2.0.1] - 2026-08-21

### Added
- **Markdown & 富文本支持 (#17)**: 集成 `marked` 标准 Markdown 渲染引擎，完整支持标题、代码块、列表、表格、引用等语法，并与老版 `[b]加粗红字[/b]` 向下兼容。
- **图文混排与附件嵌入增强 (#17)**: 支持正文中直接输入 `图1`、`图2` 或 Markdown 标准图片语法 `![图1](...)` 自动内嵌对应附件截图；在提单/编辑弹窗中新增 `[实时预览 Markdown / 切换编辑]` 交互。
- **列表一键复制到剪贴板 (#20)**: 在模块 Tab 栏新增 `📋 [复制列表]` 按钮，支持一键将当前页所有缺陷提取为整洁的无格式文本并复制到系统剪贴板。
- **ID 悬浮流转图标提醒 (#29)**: 鼠标悬浮 Bug ID 时，前缀 `#` 自动平滑切换为蓝色的 `▼` 下拉图标，给用户明确的可点击流转状态视觉暗示。
- **状态 Badge 悬浮 Tick 快速操作 (#28)**: 复刻经典特性，鼠标悬浮在活动缺陷状态 Badge 上时自动展示 `✓ 解决` 动态提示，点击即可一键流转为已解决；对已解决状态悬浮提示 `✓ 关闭`，已关闭状态悬浮提示 `↺ 激活`。

### Fixed
- **多位数 Bug ID 标题对齐修复 (#19)**: 为 Bug ID 设置 `min-w-[46px]` 最小宽度与等宽数字对齐，为状态 Badge 设置固定 `w-[64px]` 宽度，彻底解决 ID 宽度增加导致标题不对齐的问题。
- **状态多选与单选筛选修复 (#18)**: 修复前端 Store 模式默认值，锁定 `admin` 管理模式；重构后端 `status` 查询参数自适应解析器，完美支持复选框勾选、双击单选、全选与不选。
- **MCP 客户端相对路径寻址修复**: 为 `config.py` 和 `run_mcp_stdio.py` 增加基于 `PROJECT_ROOT` 的绝对路径解析与 CWD 锁定，彻底解决外部客户端在根目录执行时报 `[Errno 30] Read-only file system` 的问题。
- **状态 Badge 视觉去重框 (#28)**: 优化状态 Badge 样式，去除厚重深色边框，采用高密度现代淡彩设计。

---

## [2.0.0] - 2026-08-21

### Added
- **架构全新重构**: 后端采用 Python 3.10+ (FastAPI + SQLAlchemy 2.0 Async + Pydantic v2)，前端采用 Vue 3 + Vite + Tailwind CSS + TypeScript + Pinia。
- **完全传承 35px 高密度交互**: 传承高密度紧凑布局与全键盘快捷键体系（`Ctrl + \`` 新建、`Ctrl + Enter` 提交、`Esc` 关闭、`< 上一条` / `下一条 >` 连续评审）。
- **截图直接粘贴 (`Ctrl + V`)**: 弹窗内支持直接粘贴剪贴板截图自动上传并追加为附件，支持文件拖拽上传。
- **双数据库引擎兼容**: 默认采用零配置 SQLite 单文件数据库，支持一键切换至 MySQL / MariaDB。
- **原生 AI Agent (MCP 协议) 赋能**: 内置 Model Context Protocol (MCP) STDIO 与 SSE 服务，提供 `list_projects`, `get_project_context`, `query_bugs`, `get_bug_detail`, `create_bug`, `update_bug_status`, `add_bug_comment`, `get_project_stats` 8 大核心工具。
- **精细化角色与状态权限控制**: 引入 `admin`、`coder`、`tester`、`guest` 四大角色，严密控制状态流转权限。
- **多维质量统计看板**: 集成 ECharts 14天新增 vs 解决趋势图、状态分布饼图、人员负荷矩阵表，支持一键导出 CSV 与打印视图。
- **单端口一体化交付**: 生产模式由 FastAPI 单端口直接托管前端构建产物（默认端口 `5002`），支持 Docker / Docker Compose 一键启动。
- **GNU General Public License v3.0 (GPL-3.0)** 开源许可声明。
