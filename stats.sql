BUG提出者统计
SELECT u.fullname, count(1) AS sum FROM `items` AS i LEFT JOIN users AS u ON i.creator=u.uid WHERE i.status!=5 group by `creator`

分模块BUG分布
SELECT t.name, count(1) AS sum FROM `items` AS i LEFT JOIN types AS t ON i.type=t.tid WHERE i.status<5 group by `type`

分模块已解决BUG分布
SELECT t.name, count(1) AS sum FROM `items` AS i LEFT JOIN types AS t ON i.type=t.tid WHERE i.status in (0,4) group by `type`

【周报相关】http://tool.chinaz.com/Tools/unixtime.aspx
新增bug计数
SELECT count(1) AS sum FROM `items`  WHERE status!=5 and timestamp > 1548316800

新增BUG模块分布
SELECT t.name, count(1) AS sum FROM `items` AS i LEFT JOIN types AS t ON i.type=t.tid WHERE i.status<5 AND i.TIMESTAMP >1548316800 group by `type`

新增BUG解决情况分布
SELECT u.fullname, i.status, count(1) AS sum FROM `items` AS i LEFT JOIN users AS u ON i.lastchanger=u.uid WHERE i.TIMESTAMP >1548316800  group by i.`assignto`, i.`status`

本周BUG解决情况模块分布
SELECT t.name, count(1) AS sum FROM `items` AS i LEFT JOIN types AS t ON i.type=t.tid WHERE i.`status` in (0,4) and i.fix_time >1548316800 group by `type`

本周BUG解决情况人员分布
SELECT u.fullname, count(1) AS sum FROM `items` AS i LEFT JOIN users AS u ON i.assignto=u.uid WHERE i.`status` in (0,4) AND i.fix_time >1548316800  group by i.`assignto`