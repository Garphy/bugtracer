<?php
define('SELFNAME', 'AJAX');
require 'common.inc.php';

if(!isset($_GET['action'])) err();
$action = $_GET['action'];
$changer = $_G['uid'];
$time = time();
//new bug
if($action == 'new'){
    $type = intval($_POST['type']);
    $content = filter(urldecode($_POST['content']));
    $files = filter($_POST['files']);
    $ver = empty($_POST['ver']) ? 'NULL' : "'" . filter($_POST['ver']) . "'";
    $assignto = $_POST['assignto'];
    if(!($type > 0 && $content != '')) err();
    $sql = "INSERT INTO `items` (`type`, `ver`, `content`, `creator`, `assignto`, `timestamp`, `changetime`, `files`)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "issiiiis", $type, $ver, $content, $changer, $assignto, $time, $time, $files);
    if(mysqli_stmt_execute($stmt)){
        $id = mysqli_insert_id($GLOBALS['conn']);
        echo $id;
        savelog("New Bug-{$id}", $changer);
    } else {
        echo 0;
    }
//get
} elseif($action == 'get'){
    $id = intval($_GET['id']);
    $sql = "SELECT i.content, i.ver, i.status, i.type, i.assignto, i.lastchanger, i.changetime, i.files, u.fullname 
            FROM `items` as i 
            LEFT JOIN `users` as u ON i.creator = u.uid 
            WHERE `id` = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "i", $id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $return = [];
    if($row = mysqli_fetch_assoc($result)){
        $return = $row;
        $return['lastchanger'] = empty($return['lastchanger']) ? '' : getNameByUid($return['lastchanger']);
        $return['changetime'] = date('Y-m-d H:i:s', $return['changetime']);
    } else {
        $return = ['content' => false];
    }
    echo json_encode($return);
//edit
} elseif($action == 'edit'){
    $id = intval($_POST['id']);
    $type = intval($_POST['type']);
    $assignto = intval($_POST['assignto']);
    $content = filter(rawurldecode($_POST['content']));
    $files = filter($_POST['files']);
    $ver = empty($_POST['ver']) ? 'NULL' : "'" . filter($_POST['ver']) . "'";
    if(!($type > 0 && $content != '')) err();
    $sql = "UPDATE `items` SET 
        `type` = ?, 
        `content` = ?,
        `ver` = ?,
        `assignto` = ?,
        `lastchanger` = ?,
        `changetime` = ?,
        `files` = ?
        WHERE `id` = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "issiiiis", $type, $content, $ver, $assignto, $changer, $time, $files, $id);
    if(mysqli_stmt_execute($stmt)){
        echo $id;
        savelog("Edit Bug-{$id}.", $changer);
    } else {
        echo 0;
    }
//flag
} elseif($action == 'flag'){
    $id = intval($_POST['id']);
    $status = intval($_POST['status']);
    if(!($id > 0)) err();
    $sql = "UPDATE `items` SET `status` = ?, 
        `lastchanger` = ?,
        `changetime` = ?";
    $params = [$status, $changer, $time];
    $types = "iii";
    if($status == $_G['status_fixed']){
        $sql .= ", `fix_time` = ?";
        $params[] = $time;
        $types .= "i";
    }
    $sql .= " WHERE `id` = ?";
    $params[] = $id;
    $types .= "i";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, $types, ...$params);
    if(mysqli_stmt_execute($stmt)){
        echo $id;
        savelog("Flag Bug-{$id} to {$_G['status'][$status]}.", $changer);
    } else {
        echo 0;
    }
//addfile
} elseif($action == 'addfile'){
    $id = intval($_POST['id']);
    $files = filter($_POST['files']);
    if(!($id > 0)) err();
    $sql = "UPDATE `items` SET `files` = ?, 
        `lastchanger` = ?,
        `changetime` = ? 
        WHERE `id` = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "siii", $files, $changer, $time, $id);
    if(mysqli_stmt_execute($stmt)){
        echo $id;
        savelog("Add File-{$files} ON Bug-{$id}.", $changer);
    } else {
        echo 0;
    }
//delfile
} elseif($action == 'delfile'){
    $id = intval($_POST['id']);
    $pid = intval($_POST['pid']);
    $filename = filter($_POST['filename']);
    $dir = './uploads/' . $pid . '/';
    $isDel = @unlink($dir . $filename);
    if(!$isDel){
        savelog("Del File:{$dir}{$filename} failed.");
    }
    $sql = "SELECT files FROM `items` WHERE `id` = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "i", $id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if($row = mysqli_fetch_assoc($result)){
        $filelist = explode('|', $row['files']);
        $filelist = array_filter($filelist, function($v) use ($filename) {
            return $v != $filename;
        });
        $files = implode('|', $filelist);
        $sql = "UPDATE `items` SET `files` = ?, 
            `lastchanger` = ?,
            `changetime` = ? 
            WHERE `id` = ?";
        $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
        mysqli_stmt_bind_param($stmt, "siii", $files, $changer, $time, $id);
        if(mysqli_stmt_execute($stmt)){
            echo json_encode(['result' => 1, 'files' => $files]);
            savelog("Delete File-{$filename} ON Bug-{$id}.", $changer);
        } else {
            echo json_encode(['result' => 0]);
            savelog("Delete File-{$filename} ON Bug-{$id} failed: " . mysqli_error($GLOBALS['conn']), $changer);
        }
    }
}

function err($return = 0){
    echo $return;
    exit;
}
?>