<?php
$dbhost="localhost";
$dbuser="root";
$dbpw="123456";
$dbcharset="utf8";
define( 'ANTI_FISH_STR', 'wefoi#0sfJ@*:fweofwiefx' );
$db = mysql_connect($dbhost, $dbuser, $dbpw) or die ("数据库连接失败"); 
if($dbcharset) {
	@mysql_query("SET character_set_connection=$dbcharset, character_set_results=$dbcharset, character_set_client=binary");
}
mysql_select_db("bug", $db) or die ("目标库不存在"); 
?>
