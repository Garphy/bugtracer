# Changelog

All notable changes to the **BugTracer** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
