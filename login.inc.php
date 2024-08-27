<?php
if (isset($_GET['logout'])) {
    delCookie('auth');
    delCookie('mode');
    echo 'You quit! <a href="?">Login again</a>';
    exit;
}
if (!check_auth()) {
    if (SELFNAME == 'AJAX') {
        echo -1;
        exit;
    } else {
        include './tpl/login.tpl.htm';
        exit;
    }
}
//login check
function check_auth() {
    global $_G;
    $authcode = $_COOKIE['auth'] ?? '';
    $authcode = $authcode ? authcode($authcode, 'DECODE') : '';
    $_isNew = isset($_POST['username']);
    if (!empty($authcode)) {
        [$user, $pw] = explode("\t", $authcode);
    } elseif ($_isNew) {
        $user = trim($_POST['username']);
        $pw = md5(trim($_POST['password']));
    } else {
        return false;
    }
    $sql = "SELECT uid, role FROM `users` WHERE `username` = ? AND `password` = ?";
    $stmt = mysqli_prepare($GLOBALS['conn'], $sql);
    mysqli_stmt_bind_param($stmt, "ss", $user, $pw);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    if (mysqli_num_rows($result)) {
        $row = mysqli_fetch_assoc($result);
        $_G['uid'] = $row['uid'];
        $_G['username'] = $user;
        $_G['role'] = $row['role'];
        $_G['mode'] = $row['role'];
        if ($_isNew) {
            $cookie = implode("\t", [$user, $pw]);
            bsetCookie('auth', authcode($cookie));
        }
        //mode
        $mode = $_COOKIE['mode'] ?? '';
        $mode = $mode ? authcode($mode, 'DECODE') : $_G['mode'];
        if (!in_array($mode, $_G['roles'])) $mode = $row['role'];
        if ($row['role'] == 'admin') {
            $_G['mode'] = $_GET['debugmode'] ?? ($_GET['adminmode'] ?? $mode);
        }    
        if ($_isNew || $_G['mode'] != $mode) {
            bsetCookie('mode', authcode($_G['mode']), 7*24*3600);
        }
        return true;
    }
    return false;
}
//setcookie: 3day by default
function bsetCookie($name, $value, $time = 259200) {
    setcookie($name, $value, time() + $time);
}
function delCookie($name) {
    setcookie($name, '', time() - 999);
}
//authcode from dz
function authcode($string, $operation = 'ENCODE', $expiry = 0) {
    $ckey_length = 4;
    $key = md5(ANTI_FISH_STR . $_SERVER['HTTP_USER_AGENT']);
    $keya = md5(substr($key, 0, 16));
    $keyb = md5(substr($key, 16, 16));
    $keyc = $ckey_length ? ($operation == 'DECODE' ? substr($string, 0, $ckey_length): substr(md5(microtime()), -$ckey_length)) : '';

    $cryptkey = $keya . md5($keya . $keyc);
    $key_length = strlen($cryptkey);

    $string = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : sprintf('%010d', $expiry ? $expiry + time() : 0) . substr(md5($string . $keyb), 0, 16) . $string;
    $string_length = strlen($string);

    $result = '';
    $box = range(0, 255);

    $rndkey = array_map(fn($i) => ord($cryptkey[$i % $key_length]), range(0, 255));

    for ($j = $i = 0; $i < 256; $i++) {
        $j = ($j + $box[$i] + $rndkey[$i]) % 256;
        [$box[$i], $box[$j]] = [$box[$j], $box[$i]];
    }

    for ($a = $j = $i = 0; $i < $string_length; $i++) {
        $a = ($a + 1) % 256;
        $j = ($j + $box[$a]) % 256;
        [$box[$a], $box[$j]] = [$box[$j], $box[$a]];
        $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));
    }

    if ($operation == 'DECODE') {
        if ((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() > 0) && substr($result, 10, 16) == substr(md5(substr($result, 26) . $keyb), 0, 16)) {
            return substr($result, 26);
        } else {
            return '';
        }
    } else {
        return $keyc . str_replace('=', '', base64_encode($result));
    }
}
?>