<?php
/* bugTracer v1.0    by Garphy

todo:
合并子类及bug
删除子类同时删除bug
*/

define('SELFNAME', 'ADMIN');
require 'common.inc.php';
if($_G['role'] != 'admin' ) exit;
$action = $_GET['action'] ?? 'projectList';

$msg = '';
//============新建项目
if($action == 'newProject'){
    $pid = $projectName = '';    
    $types = $members = [];
    $coders = getMembers('coder');
//============修改项目
} elseif($action == 'editProject'){
    if(!isset($_GET['pid'])) showErr('invalid pid!');
    $pid = intval($_GET['pid']);
    $projectName = $_G['projects'][$pid];
    $sql = "SELECT * FROM `projects` WHERE pid = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "i", $pid);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $row = mysqli_fetch_assoc($result);
    if(!mysqli_num_rows($result)) showErr('project not found!');
    $members = !empty($row['members']) ? unserialize($row['members']) : [];
    $typesId = array_keys(getProjectlist($pid));
    $sql = "SELECT type, COUNT(1) as num FROM `items` WHERE type IN (" . implode(',', array_fill(0, count($typesId), '?')) . ") GROUP BY type";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, str_repeat('i', count($typesId)), ...$typesId);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $typesNum = [];
    while($row = mysqli_fetch_assoc($result)){
        $typesNum[$row['type']] = $row['num'];
    }
    $types = getProjectlist($pid);
    $coders = getMembers('coder');
//============保存项目：新建/修改
} elseif($action == 'saveProject'){
    $pid = intval($_POST['pid']);
    if(!isset($_G['projects'][$pid])) showErr('project not found');
    $projectName = strFilter($_POST['projectName']);
    $memberStr = in_array('', $_POST['members']) ? '' : serialize(array_map('intval', $_POST['members']));
    if($pid >= 0 && $_POST['action'] == 'editProject'){
        $sql = "UPDATE `projects` SET pname = ?, members = ? WHERE pid = ?";
        $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
        mysqli_stmt_bind_param($stmt, "ssi", $projectName, $memberStr, $pid);
        mysqli_stmt_execute($stmt);
    } elseif($_POST['action'] == 'newProject'){
        if(empty($projectName)) showErr('不能建立空项目');
        $sql = "INSERT INTO `projects` (`pname`, `members`) VALUES (?, ?)";
        $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
        mysqli_stmt_bind_param($stmt, "ss", $projectName, $memberStr);
        if(!mysqli_stmt_execute($stmt)) showErr('新建项目失败！');
        $pid = mysqli_insert_id($GLOBALS['conn']);
    } else {
        exit;
    }
    $typesExisted = array_keys(getProjectlist($pid));
    foreach($_POST['tid'] as $tid => $typeName){
        $tid = intval($tid);
        $typeName = strFilter($typeName);
        if(empty($typeName)) continue;
        if(in_array($tid, $typesExisted)){
            $sql = ($typeName == 'TO_BE_REMOVED') ? "DELETE FROM `types` WHERE tid = ?" : "UPDATE `types` SET name = ? WHERE tid = ?";
            $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
            if($typeName == 'TO_BE_REMOVED'){
                mysqli_stmt_bind_param($stmt, "i", $tid);
            } else {
                mysqli_stmt_bind_param($stmt, "si", $typeName, $tid);
            }
        } else {
            $sql = "INSERT INTO `types` (`pid`, `name`) VALUES (?, ?)";
            $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
            mysqli_stmt_bind_param($stmt, "is", $pid, $typeName);
        }
        mysqli_stmt_execute($stmt);
    }
    $msg = 'Project saved.';
    $action = 'projectList';
//============人员列表
} elseif($action == 'memberList'){
    $members = getMembers();
//============修改人员信息
} elseif($action == 'editMember'){
    $uid = intval($_GET['uid']);
    $members = getMembers($uid, 'uid');
    $member = $members[$uid];
//============新增人员
} elseif($action == 'newMember'){
    $uid = 0;
    $member = ['username' => '', 'fullname' => '', 'role' => ''];
//============保存人员：新增/修改
} elseif($action == 'saveMember'){
    $uid = intval($_POST['uid']);
    if(!$uid && $action == 'editMember') showErr('无效UID');
    $username = strFilter($_POST['username']);
    $fullname = strFilter($_POST['fullname']);
    $role = strFilter($_POST['role'] ?? '');
    if(!in_array($role, $_G['roles'])) showErr('不给权限别人怎么玩啊！');
    $pw = strFilter($_POST['password']);
    if(empty($username)) showErr('用户名没填怎么行啊！');
    if(!preg_match('/^[_\-A-Za-z0-9]+$/', $username)) showErr('用户名请用英文字母！');
    if(empty($fullname)) $fullname = $username;
    if($_POST['action'] == 'editMember'){
        $sql = "UPDATE `users` SET username = ?, fullname = ?, role = ?";
        $params = [$username, $fullname, $role];
        $types = "sss";
        if(!empty($pw)){
            $sql .= ", password = ?";
            $params[] = md5($pw);  // 使用 MD5 加密
            $types .= "s";
        }
        $sql .= " WHERE uid = ?";
        $params[] = $uid;
        $types .= "i";
    } elseif($_POST['action'] == 'newMember'){
        if(empty($pw)) $pw = '123456';
        $pw = md5($pw);  // 使用 MD5 加密
        $sql = "INSERT INTO `users` (`role`, `fullname`, `username`, `password`) VALUES (?, ?, ?, ?)";
        $params = [$role, $fullname, $username, $pw];
        $types = "ssss";
    }
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    if (!$stmt) {
        die("准备语句失败: " . mysqli_error($GLOBALS['conn']));
    }
    mysqli_stmt_bind_param($stmt, $types, ...$params);
    if (!mysqli_stmt_execute($stmt)) {
        $error = mysqli_stmt_error($stmt);
        die("执行语句失败: " . $error);
    }
    $msg = 'Member saved.';
    $action = 'memberList';
    $members = getMembers();
//============项目列表
} else {
    $projects = $_G['projects'];
}
//cur tab
$curtab = (stripos($action, 'member') !== false) ? 'member' : 'prj';

function strFilter($str){
    return trim($str);
}

function getMembers($by = '', $filter = 'role'){
    $coders = [];
    $sql = "SELECT uid, username, fullname, role FROM `users`";
    if(!empty($by)) $sql .= " WHERE `{$filter}` = ?";
    $sql .= " ORDER BY role, fullname";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    if(!empty($by)) mysqli_stmt_bind_param($stmt, "s", $by);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if(!mysqli_num_rows($result)) return $coders;
    while($row = mysqli_fetch_assoc($result)){
        $member = array_filter($row, function($k) {
            return !is_numeric($k);
        }, ARRAY_FILTER_USE_KEY);
        $coders[$row['uid']] = $member;
    }
    return $coders;
}
    
function getProjectlist($pid){
    $list = [];
    $sql = "SELECT * FROM `types` WHERE pid = ? ORDER BY pid ASC";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "i", $pid);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if(!mysqli_num_rows($result)) return $list;
    while($row = mysqli_fetch_assoc($result)){
        $list[$row['tid']] = $row['name'];
    }
    return $list;
}

function showErr($msg){
    echo $msg;
    exit;
}

?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>ADMIN - BugTracer</title>
<link rel="stylesheet" href="style.css" />
<script type="text/javascript" src="/include/jquery.min.js"></script>
<script type="text/javascript" src="admin.js"></script>
</head>
<body>
<div class="top">
    <h1><a href="admin.php">BugTracer 管理后台</a> <a href="./">[返回前台]</a></h1>
</div>
<div class="main" id="admin">
<div class="menu clearfix">
    <ul id="types">
        <li id="prj" class="first-child"><a href="?">项目管理</a></li>
        <li id="member"><a href="?action=memberList">人员管理</a></li>
        <!--<li class="add"><a href="javascript:void(0)" title="快捷键：Ctrl+`">提交新bug</a></li>-->
    </ul>
    <script type="text/javascript"> $('#<?php echo $curtab?>').addClass('on'); </script>
</div>
<div class="content2">
    <div class="cms clearfix">
        <div id="msg"><?php echo $msg; ?></div>
        <?php require './tpl/admin.tpl.htm';?>
    </div>
</div>

<div class="tips">
Tips：前端人员全称前统一加个*，以示区别；
</div>

<?php require './tpl/foot.tpl.htm';    ?>

</div>
</body>
</html>
