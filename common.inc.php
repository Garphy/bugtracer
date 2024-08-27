<?php
date_default_timezone_set('Etc/GMT-8');
$_G = array();
//global variables
define( 'PAGESIZE', 30 );
$_G['roles'] = array( 'admin', 'coder' );
$_G['defaultFilter'] = array(1,2,3);//白名单，默认排除closed/fixed/won't fix
$_G['vers'] = array();
$_G['vers'][1] = '';// default version for pid = 1
/*
Status:
0.closed
1.new
2.partial fixed
3.fixed
4.won't fixed
5.todo
6.idea
*/
$_G['status'] = array( 'closed', 'new', 'key', 'part_fixed', 'fixed', 'wont_fix', 'todo', 'idea');
$_G['status_default'] = 1;
$_G['status_fixed'] = 4;

include 'config.inc.php';
include 'login.inc.php';
include 'lang.inc.php';
$_G['pid'] = isset($_GET['pid']) ? intval($_GET['pid']):0;
$thisPid = $_G['pid'];
$_G['prjName'] = '';
$_G['cur_ver'] = isset($_G['vers'][$thisPid])?$_G['vers'][$thisPid]:'';
$_G['projects'] = $_G['types'] = $_G['typeid'] = array();
//mybug counts for each project
$sql = 'SELECT t.pid, count(i.id) as num FROM `items` AS i LEFT JOIN `types` AS t ON i.type = t.tid WHERE i.status in ('.implode(', ', $_G['defaultFilter']).')';
if( $_G['mode'] == 'coder' ) $sql .= ' AND i.assignto = '.$_G['uid'];
$sql .= ' GROUP BY t.pid';
$result = mysql_query($sql);
$mybugs = array( 'total' => 0 );
while($row = mysql_fetch_array($result)){
	$mybugs[$row['pid']] = $row['num'];
	$mybugs['total'] += $row['num'];
}
//echo $sql;
//project list
$sql = "SELECT * FROM `projects`";
$result = mysql_query($sql);
while($row = mysql_fetch_array($result)){
	if( $thisPid == $row['pid'] ){
		$_G['prjName'] = $row['pname'];
		$_G['members'] = unserialize($row['members']);
	}
	$_G['projects'][$row['pid']] = $row['pname'];
	if( !isset($mybugs[$row['pid']]) ) $mybugs[$row['pid']] = 0;
}
$sql = "SELECT * FROM `types` WHERE pid={$thisPid}";
$result = mysql_query($sql);
while($row = mysql_fetch_array($result)){
	$_G['typeid'][] = $row['tid'];
	$_G['types'][$row['tid']] = $row['name'];
}
//all user list
$sql = "SELECT uid, fullname FROM `users`";
$result = mysql_query($sql);
$_G['users'] = array();
while($row = mysql_fetch_array($result)){
	$_G['users'][$row['uid']] = $row['fullname'];
}
function getNameByUid( $uid ){
	global $_G;
	return isset( $_G['users'][$uid] ) ? $_G['users'][$uid] : null;
}
//str filter
function filter($str){
	$str = str_replace( array(' '), '&nbsp;' , $str);
	$str = str_replace("<", "&lt;", $str);
	$str = str_replace(">", "&gt;", $str);
	$str = str_replace('"', "&quot;", $str);
	$str = str_replace("'", "&#39;", $str);
	return $str;
}
function savelog( $log, $userid = '', $filename = '', $path = './log/' ){
	if( empty($filename) ) $filename= date('Ym');
	if( !empty($userid) ) $log = "USERID={$userid} {$log}";
	$time = date('Ymd H:i:s');
	$log = "{$time}@{$_SERVER['REMOTE_ADDR']}@{$log}";
	write2file($filename, $log."\n", $path, $suffix = '.log');
}
//to xml
function write2file($filename, $output, $prefix = './', $suffix = '.log') {//写入文件 $filename = 路径+写入文件名 ; $output = 写入的文件流
	$filename = $prefix.$filename.$suffix;
	$temp = explode('/',$filename);
	$temp[count($temp)-1] ='';
	$dir = implode('/',$temp);
	if(!is_dir($dir)) {
		@mkdir($dir, 0777);
	}
	if($fp = @fopen($filename, 'a')) {
		fwrite($fp, $output);
		fclose($fp);
	} else {
		echo "Unable to write into file".$filename;
	}
}
?>