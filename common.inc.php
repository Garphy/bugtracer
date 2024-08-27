<?php
date_default_timezone_set('Etc/GMT-8');
$_G = array();
//global variables
define('PAGESIZE', 30);
$_G['roles'] = ['admin', 'coder'];
$_G['defaultFilter'] = [1,2,3]; //白名单，默认排除closed/fixed/won't fix
$_G['vers'] = [];
$_G['vers'][1] = ''; // default version for pid = 1
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
$_G['status'] = ['closed', 'new', 'key', 'part_fixed', 'fixed', 'wont_fix', 'todo', 'idea'];
$_G['status_default'] = 1;
$_G['status_fixed'] = 4;

// init
require 'config.inc.php';
// 使用 mysqli 替代 mysql
$conn = mysqli_connect($dbhost, $dbuser, $dbpw) or die("数据库连接失败");
$GLOBALS['conn'] = $conn;
if ($dbcharset) {
    mysqli_set_charset($conn, $dbcharset);
}
mysqli_select_db($conn, "bug") or die("目标库不存在");

require 'login.inc.php';
require 'lang.inc.php';

$_G['pid'] = $_GET['pid'] ?? 0;
$thisPid = $_G['pid'];
$_G['prjName'] = '';
$_G['cur_ver'] = $_G['vers'][$thisPid] ?? '';
$_G['projects'] = $_G['types'] = $_G['typeid'] = [];
//mybug counts for each project
$sql = 'SELECT t.pid, count(i.id) as num FROM `items` AS i LEFT JOIN `types` AS t ON i.type = t.tid WHERE i.status in (' . implode(', ', $_G['defaultFilter']) . ')';
if ($_G['mode'] == 'coder') $sql .= ' AND i.assignto = ' . $_G['uid'];
$sql .= ' GROUP BY t.pid';
$result = mysqli_query($GLOBALS['conn'], $sql);
$mybugs = ['total' => 0];
while ($row = mysqli_fetch_assoc($result)) {
    $mybugs[$row['pid']] = $row['num'];
    $mybugs['total'] += $row['num'];
}
//echo $sql;
//project list
$sql = "SELECT * FROM `projects`";
$result = mysqli_query($GLOBALS['conn'], $sql);
while ($row = mysqli_fetch_assoc($result)) {
    if ($thisPid == $row['pid']) {
        $_G['prjName'] = $row['pname'];
        $_G['members'] = unserialize($row['members']);
    }
    $_G['projects'][$row['pid']] = $row['pname'];
    if (!isset($mybugs[$row['pid']])) $mybugs[$row['pid']] = 0;
}
$sql = "SELECT * FROM `types` WHERE pid={$thisPid}";
$result = mysqli_query($GLOBALS['conn'], $sql);
while ($row = mysqli_fetch_assoc($result)) {
    $_G['typeid'][] = $row['tid'];
    $_G['types'][$row['tid']] = $row['name'];
}
//all user list
$sql = "SELECT uid, fullname FROM `users`";
$result = mysqli_query($GLOBALS['conn'], $sql);
$_G['users'] = [];
while ($row = mysqli_fetch_assoc($result)) {
    $_G['users'][$row['uid']] = $row['fullname'];
}
function getNameByUid($uid) {
    global $_G;
    return $_G['users'][$uid] ?? null;
}
//str filter
function filter($str) {
    $str = str_replace([' '], '&nbsp;', $str);
    $str = str_replace("<", "&lt;", $str);
    $str = str_replace(">", "&gt;", $str);
    $str = str_replace('"', "&quot;", $str);
    $str = str_replace("'", "&#39;", $str);
    return $str;
}
function savelog($log, $userid = '', $filename = '', $path = './log/') {
    if (empty($filename)) $filename = date('Ym');
    if (!empty($userid)) $log = "USERID={$userid} {$log}";
    $time = date('Ymd H:i:s');
    $log = "{$time}@{$_SERVER['REMOTE_ADDR']}@{$log}";
    write2file($filename, $log . "\n", $path, '.log');
}
//to xml
function write2file($filename, $output, $prefix = './', $suffix = '.log') { //写入文件 $filename = 路径+写入文件名 ; $output = 写入的文件流
    $filename = $prefix . $filename . $suffix;
    $dir = dirname($filename);
    if (!is_dir($dir)) {
        @mkdir($dir, 0777, true);
    }
    if ($fp = @fopen($filename, 'a')) {
        fwrite($fp, $output);
        fclose($fp);
    } else {
        echo "Unable to write into file" . $filename;
    }
}
?>