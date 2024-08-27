# BugTracer v1.0 使用说明
------------
copy rights by Garphy

## 安装
php启用必要扩展
```
sudo apt-get install php-mbstring

php.ini启用扩展
extension=mbstring

sudo systemctl restart nginx
```
创建附件目录：uploads 并赋予写入权限

## 特性
- 功能兼容IE6，界面上BS IE6
- 分项目、分子类存放问题
- 问题可指派给指定人员处理
- 提交bug界面，支持文件拖拽上传（仅限现代浏览器）
- 点击bugID，下拉修改状态；
- 双击bug，当前页显示问题详情及截图；
- 快捷标记问题状态：支持快捷标记为fixed、快捷标记为closed；
- 后台项目管理
- 后台人员管理

## 问题状态
- closed		- 关闭
- new		- 新建
- key		- 高优问题
- part_fixed	- 部分已处理
- fixed		- 已解决
- wont_fix	- 放弃处理的问题
- todo		- 代处理的问题
- idea		- 备忘/点子

注：默认仅显示 new/key/part_fixed 问题

## 问题搜索
- 文本		- 查找项目中包括此关键词的问题
- 数字		- 查找并显示以此为ID的问题
- (用户ID)	- 查找项目中由此用户提出的问题
- {用户ID}	- 查找项目中分派给此用户的问题
- {yyyy-mm-dd~yyyy-mm-dd}	-查找项目中变更日期在此时间段内的问题（从前一个日期到后一个日期之前，例如查询3.1当天变更的问题：{2012-3-1~2012-3-2}）

问题状态筛选技巧：只想筛选某一状态的问题，直接双击某项即可；

## 提交问题高级技巧
- 加粗套红：代码 `[b]加粗文本[/b]`
- 图文混排：识别内文中的中文字符：图1、图2、图3等，自动用附件图片替换

## 快捷操作
- ctrl + `	提交新问题
- Esc		关闭问题详情浮层

## 上传
- 拖放文件到文件详情浮层，自动上传；
- 支持文件类型：jpg gif png txt doc docx rar zip
- 上传大小限制：1M
- 以上定义存放在 common.js: createUploader()

## 帐号类型
- admin	- 管理员（显示全部问题，允许操作后台）
- coder	- 技术（默认仅显示分派给自己的问题）

# 文件结构
- config.sample.php	数据库配置文件，需要重命名为config.inc.php
- index.php	前台主文件
- common.inc.php	通用函数/全局定义
- login.inc.php	登录验证
- login.tpl.htm	登录页面
- upload.php	上传文件
- admin.php	管理后台
- admin.tpl.htm	管理后台模板
- common.js	前台js
- admin.js	后台js
- fileuploader.js	html5拖拽上传js
- style.css	主样式表
- uploads/	上传目录（按项目id分开存放）

# 维护SQL
```sql
//批量修改状态
UPDATE items SET status=0 WHERE status=4 AND type in (SELECT tid FROM `types` WHERE pid=1)
```

