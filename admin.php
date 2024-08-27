<?php
/* bugTracer v1.0	by Garphy

todo:
合并子类及bug
删除子类同时删除bug
*/

define('SELFNAME', 'ADMIN');
include 'common.inc.php';
if($_G['role'] != 'admin' ) exit;
$action = isset($_GET['action']) ? $_GET['action'] : 'projectList';

$msg = '';
//============新建项目
if( $action=='newProject' ){
	$pid = $projectName = '';	
	$types = $members = array();
	$coders = getMembers('coder');
//============修改项目
}else if( $action=='editProject' ){
	if( !isset($_GET['pid']) ) showErr('invalid pid!');
	$pid = intval($_GET['pid']);
	$projectName = $_G['projects'][$pid];
	$sql = "SELECT * FROM `projects` WHERE pid={$pid}";
	$result = mysql_query($sql);
	$row = mysql_fetch_array($result);
	if( !mysql_num_rows($result) ) showErr('project not found!');
	$members = !empty($row['members']) ? unserialize($row['members']) : array();
	$typesId = array_keys( getProjectlist($pid) );
	$sql = "SELECT type, count(1) as num FROM `items` WHERE type in (".implode(',', $typesId).") GROUP BY type";
	$result = mysql_query($sql);
	if( @mysql_num_rows($result) ){
		while($row = mysql_fetch_array($result)){
			$typesNum[$row['type']] = $row['num'];
		}
	}
	$types = getProjectlist($pid);
	$coders = getMembers('coder');
//============保存项目：新建/修改
}else if( $action=='saveProject' ){
	$pid = intval($_POST['pid']);
	if( !isset($_G['projects'][$pid]) ) showErr('project not found');
	$projectName = strFilter($_POST['projectName']);
	if( in_array( '', $_POST['members'] ) ){
		$memberStr = '';
	}else{
		array_walk( $_POST['members'], 'intvalArr');
		$memberStr = serialize($_POST['members']);
	}
	if( $pid >= 0 && $_POST['action']=='editProject' ){
		mysql_query("UPDATE `projects` SET pname='{$projectName}', members='{$memberStr}' WHERE pid={$pid}");
	}else if( $_POST['action']=='newProject' ){
		if( empty($projectName) ) showErr('不能建立空项目');
		$sql = "INSERT INTO `projects` ( `pname`, `members` ) VALUES ( '{$projectName}', '{$memberStr}' )";
		if( !mysql_query($sql) ) showErr('新建项目失败！');
		$pid = mysql_insert_id();
	}else{
		exit;
	}
	$typesExisted = array_keys( getProjectlist($pid) );
	foreach( $_POST['tid'] as $tid => $typeName ){
		$tid = intval($tid);
		$typeName = strFilter($typeName);
		if( empty($typeName) ) continue;
		if( in_array( $tid, $typesExisted ) ){
			$sql = ($typeName=='TO_BE_REMOVED') ? "DELETE FROM `types` WHERE tid={$tid}" : "UPDATE `types` SET name='{$typeName}' WHERE tid={$tid}";
		}else{//new
			$sql = "INSERT INTO `types` ( `pid`, `name` ) VALUES ( {$pid}, '{$typeName}' )";
		}
		mysql_query($sql);
	}
	$msg = 'Project saved.';
	$action = 'projectList';
//============人员列表
}else if( $action=='memberList' ){
	$members = getMembers();
//============修改人员信息
}else if( $action=='editMember' ){
	$uid = intval($_GET['uid']);
	$members = getMembers( $uid, 'uid' );
	$member = $members[$uid];
//============新增人员
}else if( $action=='newMember' ){
	$uid = 0;
	$member = array( 'username' => '', 'fullname' => '', 'role' => '' );
//============保存人员：新增/修改
}else if( $action=='saveMember' ){
	$uid = intval($_POST['uid']);
	if( !$uid && $action=='editMember' ) showErr('无效UID');
	$username = strFilter($_POST['username']);
	$fullname = strFilter($_POST['fullname']);
	$role = @strFilter($_POST['role']);
	if( !in_array($role, $_G['roles'] ) ) showErr('不给权限别人怎么玩啊！');
	$pw = strFilter($_POST['password']);
	if( empty($username) ) showErr('用户名没填怎么行啊！');
	if( !preg_match( '/^[_\-A-Za-z0-9]+$/', $username ) ) showErr('用户名请用英文字母！');
	if( empty($fullname) ) $fullname = $username;
	if( $_POST['action']=='editMember' ){
		$sql = "UPDATE `users` SET username='{$username}', fullname='{$fullname}', role='{$role}'";
		if( !empty($pw) ) $sql .= ", password='". md5($pw) ."'";
		$sql .= " WHERE uid={$uid}";
	}else if( $_POST['action']=='newMember' ){
		if( empty($pw) ) $pw = '123456';
		$pw = md5($pw);
		$sql = "INSERT INTO `users` ( `role` , `fullname` , `username` , `password` ) VALUES ( '{$role}', '{$fullname}', '{$username}', '{$pw}' )";
	}
	$msg = mysql_query($sql) ? 'Member saved.' : 'err.';
	$action = 'memberList';
	$members = getMembers();
//============项目列表
}else{
	$projects = $_G['projects'];
}
//cur tab
$curtab = (stripos( $action, 'member') !== false) ? 'member' : 'prj';

function strFilter($str){
	return trim($str);
}

function intvalArr( &$v, $k ){
	$v = intval($v);
}
function getMembers( $by = '', $filter = 'role' ){
	$coders = array();
	$sql = "SELECT uid, username, fullname, role FROM `users`";
	if( !empty($by) ) $sql .= " WHERE `{$filter}` = '{$by}'";
	$sql .= " ORDER BY role, fullname";
	$result = mysql_query($sql);
	if(!mysql_num_rows($result)) return $coders;
	while($row = mysql_fetch_array($result)){
		$member = array();
		foreach( $row as $k => $v ){
			if( !preg_match( '/^\d+$/', $k ) ) $member[$k] = $v ;
		}
		$coders[$row['uid']] = $member;
	}
	return $coders;
}
	
function getProjectlist($pid){
	$list = array();
	$sql = "SELECT * FROM `types` WHERE pid='{$pid}' ORDER BY pid ASC";
	$result = mysql_query($sql);
	if(!mysql_num_rows($result)) return $list;
	while($row = mysql_fetch_array($result)){
		$list[$row['tid']] = $row['name'];
	}
	return $list;
}

function showErr( $msg ){
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
        <?php include './tpl/admin.tpl.htm';?>
    </div>
</div>

<div class="tips">
Tips：前端人员全称前统一加个*，以示区别；
</div>

<?php include './tpl/foot.tpl.htm';	?>

</div>
</body>
</html>
