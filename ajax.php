<?php
define('SELFNAME', 'AJAX');
include 'common.inc.php';

if(!isset($_GET['action']))err();
$action = $_GET['action'];
$changer = $_G['uid'];
$time = time();
//new bug
if($action == 'new'){
	$type = intval($_POST['type']);
	$content = filter(urldecode($_POST['content']));
	$files = filter($_POST['files']);
	$ver = empty($_POST['ver']) ? 'NULL':"'".filter($_POST['ver'])."'";
	$assignto = $_POST['assignto'];
	if( !($type > 0 && $content !='') ) err();
	$sql = "INSERT INTO `items` (`type` , `ver` , `content` , `creator` , `assignto`, `timestamp`, `changetime`, `files` )
		VALUES ( {$type}, {$ver} , '{$content}', '{$changer}', '{$assignto}', '".$time."', '".$time."', '{$files}' );";
	echo @mysql_query($sql) ? mysql_insert_id():0;
	savelog( "New Bug-".mysql_insert_id(), $changer );
//get
}elseif($action == 'get'){
	$id = intval($_GET['id']);
	$sql = "SELECT i.content, i.ver, i.status, i.type, i.assignto, i.lastchanger, i.changetime, i.files, u.fullname FROM `items` as i LEFT JOIN `users` as u ON i.creator = u.uid WHERE `id` = {$id}";
	$result = mysql_query($sql);
	$return = array();
	if(mysql_num_rows($result)){
		$row = mysql_fetch_array($result);
		foreach( $row as $k => $v ){
			if( !preg_match( '/^\d+$/', $k ) ) $return[$k] = $v ;
		}
		$return['lastchanger'] = empty($return['lastchanger']) ? '' : getNameByUid($return['lastchanger']);
		$return['changetime'] = date('Y-m-d H:i:s', $return['changetime']);
	}else{
		$return = array( 'content' => false );
	}
	echo json_encode( $return );
//edit
}elseif($action == 'edit'){
	$id = intval($_POST['id']);
	$type = intval($_POST['type']);
	$assignto = intval($_POST['assignto']);
	$content = filter(rawurldecode($_POST['content']));
	$files = filter($_POST['files']);
	$ver = empty($_POST['ver']) ? 'NULL':"'".filter($_POST['ver'])."'";
	if( !($type > 0 && $content !='') ) err();
	$sql = "UPDATE `items` SET `type` = {$type},
		`content` = '{$content}',
		`ver` = {$ver},
		`assignto` = {$assignto},
		`lastchanger` = {$changer},
		`changetime` = {$time},
		`files` = '{$files}'
		WHERE `id` = {$id};";
	echo @mysql_query($sql) ? $id:0;
	savelog( "Edit Bug-{$id}.", $changer );
//flag
}elseif($action == 'flag'){
	$id = intval($_POST['id']);
	$status = intval($_POST['status']);
	if( !($id > 0) ) err();
	$sql = "UPDATE `items` SET `status` = {$status}, 
		`lastchanger` = {$changer},
		`changetime` = {$time}";
	if( $status == $_G['status_fixed'] ) $sql .= ", `fix_time` = {$time}";
	$sql .= " WHERE `id` = {$id}";
	echo @mysql_query($sql) ? $id:0;
	savelog( "Flag Bug-{$id} to {$_G['status'][$status]}.", $changer );
//addfile
}elseif($action == 'addfile'){
	$id = intval($_POST['id']);
	$files = filter($_POST['files']);
	if( !($id > 0) ) err();
	$sql = "UPDATE `items` SET `files` = '{$files}', 
		`lastchanger` = {$changer},
		`changetime` = {$time} 
		WHERE `id` = {$id}";
	echo @mysql_query($sql) ? $id:0;
	savelog( "Add File-{$files} ON Bug-{$id}.", $changer );
//delfile
}elseif($action == 'delfile'){
	$id = intval($_POST['id']);
	$pid = intval($_POST['pid']);
	$filename = filter($_POST['filename']);
	$dir = './uploads/'.$pid.'/';
	$isDel = @unlink( $dir.$filename );
	if( !$isDel ){
		savelog( "Del File:{$dir}{$filename} failed." );
	}
	$sql = "SELECT files FROM `items` WHERE `id` = {$id}";
	$result = mysql_query($sql);
	if(mysql_num_rows($result)){
		$row = mysql_fetch_array($result);
		$filelist = explode( '|', $row['files'] );
		foreach( $filelist as $k => $v){
			if( $v == $filename ) unset($filelist[$k]);
		}
		$files = implode( '|', $filelist );
		$sql = "UPDATE `items` SET `files` = '{$files}', 
			`lastchanger` = {$changer},
			`changetime` = {$time} 
			WHERE `id` = {$id}";
		if( @mysql_query($sql) ){
			echo '{"result":1,"files":"'.$files.'"}';
			//echo "/*{$sql}*/";
			savelog( "Delete File-{$filename} ON Bug-{$id}.", $changer );
		}else{
			echo '{"result":0}';
			savelog( "Delete File-{$filename} ON Bug-{$id} failed: ".mysql_error(), $changer );
		}
	}
}
function err($return = 0){
	echo $return;
	exit;
}
?>