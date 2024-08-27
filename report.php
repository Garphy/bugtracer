<?php
define('SELFNAME', 'REPORT');
include 'common.inc.php';

$foot_out = '';
$type = isset($_GET['type']) ? intval($_GET['type']):'all';
$date = isset($_GET['date']) ? intval($_GET['date']):'';
$order = isset($_GET['order']) ? filter($_GET['order']):'id';
$filter = array();
$filter = isset($_GET['status']) ? $_GET['status']:$_G['defaultFilter'];

//user Names
$sql = "SELECT uid, role, fullname FROM `users`";
$result = mysql_query($sql);
$userNames = array( 0 => '未指派', 'all' => '合计' );
while($row = mysql_fetch_array($result)){
	$userNames[$row['uid']] = $row['role']=='admin' ? "（{$row['fullname']}）":$row['fullname'];
}
//var_dump($userNames);

$sql = "SELECT i.*, t.name, t.pid FROM `items` AS i inner JOIN `types` AS t ON i.type = t.tid WHERE 1";
if( isset($_GET['search']) ){
	if( preg_match( '/^\d+,?/', $_GET['search'] ) ){//by id
		$ids = explode(',', $_GET['search']);
		foreach($ids as $k => $id){
			$ids[$k] = intval($id);
			if( $ids[$k]==0 ) unset($ids[$k]);
		}
		$sql .= " AND i.id in (". implode(',', $ids) .")";
	}else if( preg_match( '/^\((\d+)\)$/', $_GET['search'], $match ) ){//by creator
		$user = $match[1];
		$sql .= " AND i.creator = {$user}";
	}else if( preg_match( '/^{(\d+)}$/', $_GET['search'], $match ) ){//by assignto
		$user = $match[1];
		$sql .= " AND i.assignto = {$user}";
	}else if( preg_match( '/^{(\d{4}-\d+-\d+)~(\d{4}-\d+-\d+)}$/', $_GET['search'], $match ) ){//by changetime
		$from = $match[1];
		$to = $match[2];
		$time0 = explode('-', $from);
		$time1 = explode('-', $to);
		$t0 = mktime( 0,0,0,$time0[1],$time0[2],$time0[0] );
		$t1 = mktime( 0,0,0,$time1[1],$time1[2],$time1[0] );
		$sql .= " AND i.changetime >= {$t0} AND i.changetime < {$t1}";
	}else{//by keywords
		$str = filter($_GET['search']);
		$sql .= " AND i.content LIKE '%{$str}%'";
	}
//list
}
$sql .= ' AND i.status in ('.implode(', ', $filter).') AND i.assignto!=0';

//date
if( !empty($date) && preg_match( '/^(\d{2})(\d{2})(\d{2})$/', $date, $match ) ){
	$y = $match[1];
	$m = $match[2];
	$d = $match[3];
	$t0 = mktime( 0,0,0,$m,$d,$y );
	$t1 = $t0 + 3600*24;
	$sql .= " AND i.timestamp >= {$t0} AND i.timestamp < {$t1}";
}

$sql .= " ORDER BY t.pid asc, t.tid asc, i.id desc";
//echo $sql;
//show
$result = mysql_query($sql);
$items = array();
if(mysql_num_rows($result)){
while($row = mysql_fetch_array($result)){
	$row['status_name'] = $_G['status'][$row['status']];
	$row['content'] = makeTages( $row['content'] );
	$urls = array();
	if( !empty($row['files']) ){
		$files = explode( '|', $row['files'] );
		foreach( $files as $file ){
			$urls[] = './uploads/'.$row['pid'].'/'.$file;
		}
	}
	$row['files'] = $urls;
	//$row['content'] = '『'.$row['name'].'』'.$row['content'];
	$row['attach'] = empty($row['files']) ? false:true;
	$row['assigned'] = (
		$_G['mode'] == 'coder' && $row['assignto'] != $_G['uid'] || 
		$row['assignto']==0 && in_array( $row['status'], $_G['defaultFilter'] )
		) ? false:true;
	$row['creatorName'] = $userNames[$row['creator']];
	$items[] = $row;
}}
//total items
if( !isset($shown_items) ) $shown_items = mysql_num_rows($result);
$sql = "SELECT count( id ) as total FROM `items`";
if( $type!='all' ) $sql.= ' AND type = '.intval($type);
$result = mysql_query($sql);
$row = mysql_fetch_array($result);
$total_items = $row['total'];
$numbers = $shown_items.'/'.$total_items;

//stats
$stats = array();
$stats['all'] = array( 'total' => 0, 'fixed' => 0, 'key' => 0, 'name' => $userNames['all'] );
$sql = 'SELECT assignto, status, count(1) AS sum FROM `items` group by `assignto`, `status`';
//$sql = 'SELECT assignto, status, count(1) AS sum FROM `items` WHERE TIMESTAMP >1547107200 group by `assignto`, `status`';
$result = mysql_query($sql);
if(mysql_num_rows($result)){
while($row = mysql_fetch_array($result)){
	$uid = $row['assignto'];
	$stats[$uid]['name'] = $userNames[$uid];
	//活动bug：123
	if( in_array( $row['status'], array(1,2,3) ) ){ 
		$stats[$uid]['total'] = isset($stats[$uid]['total']) ? $stats[$uid]['total']+$row['sum'] : $row['sum'];
		$stats['all']['total'] += $row['sum'];
	//已解决bug：04
	}else if( in_array( $row['status'], array( 0,4 ) ) ){
		$stats[$uid]['fixed'] =  isset($stats[$uid]['fixed']) ? $stats[$uid]['fixed']+$row['sum'] : $row['sum'];
		$stats['all']['fixed'] += $row['sum'];
	//关键bug：2
	}
	if( $row['status'] == 2 ){
		$stats[$uid]['key'] =  isset($stats[$uid]['key']) ? $stats[$uid]['key']+$row['sum'] : $row['sum'];
		$stats['all']['key'] += $row['sum'];
	}
}}
//var_dump($stats);
//title
$page_title = '全项目报表 - ';
//[b] => <b> 、add link
function makeTages( $str ){
	$availableTags = array('b');
	$str = preg_replace( '/\[('.implode( '|', $availableTags).')\](.*?)\[\/\1\]/', '<\\1>\\2</\\1>', $str );
	$str = preg_replace( '/\[\/?('.implode( '|', $availableTags).')?(\]|$)/', '', $str );
	$str = preg_replace( '/\n/', '<br/>', $str );
	$str = preg_replace( '/(https?\:\/\/(?:\w+\.)?\w+\.\w+\/[\/\?&\.\-%+=_A-Za-z0-9]{0,}(?:#\w+)?)(\s)/', '<a href="\\1" target="_blank">\\1</a>\\2', $str);//links
	return $str;
}
?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=Edge，chrome=1">
<title><?php echo $page_title;?>BugTracer</title>
<link rel="stylesheet" href="style.css" />
<link rel="stylesheet" href="img/fileuploader.css" />
<style type="text/css">
.report { width:96%; margin: 50px auto;}
.report h2 { margin:1em 0 0.5em; font-weight:bold; font-size:20px; line-height:2em; font-family:'微软雅黑'; background:#eee; border-radius:5px; text-indent:0.5em;}
.report-items { padding:1em;}
.report-items:nth-child(odd) { background:#f9f9f9;}
.report-items h6 { position:relative; font-weight:bold; font-family:'微软雅黑';}
.report-items h6 a{ font-weight:bold;  color:darkgreen;}
.report-items h6 em { position:absolute; right:1em; color:#999;}
.report-items .desc{ margin:10px; padding-left:50px; font-size:14px; line-height:1.5em;}
.report-items .key { color:#f00;}
.report-items .files img{ max-height:200px; max-width:50%; border:1px solid #ddd; padding:1px;}
.stats { width:96%; margin: 20px auto;}
th, td { font-size:12px; line-height:1.5em;  text-align:center;}
.stats table { width:50%; border-collapse:collapse;}
.stats table th { color: #333; background:#ccc;}
.stats table td { border:1px solid #ccc;}
</style>
<link rel="stylesheet" href="img/print.css" type="text/css" media="print" />
<script type="text/javascript">
var isAdmin = <?php echo $_G['role']=='admin' ? 1:0 ?>;
var cur_pid = '<?php echo $thisPid ?>';
var cur_ver = '<?php echo $_G['cur_ver'] ?>';
var cur_type = '<?php echo $type ?>';
var G_status = ['<?php echo implode("', '", $_G['status']) ?>'];
var G_status_default = <?php echo $_G['status_default'] ?>;
var G_status_fixed = <?php echo $_G['status_fixed'] ?>;
var no_upload = true;
</script>
</head>
<body>
<div class="top">
	<div class="login">
		<span>Login in as: <?php echo $_G['username'] ?></span>
		<a href="?logout">[退出]</a>
	</div>
	<div class="projects" id="project_switch">
		<a href="javascript:void(0)" class="flag">总活动Bug<em>(<?php echo $mybugs['total']?>)</em> 当前项目：<?php echo $_G['prjName'];?>(<?php echo $mybugs[$thisPid]?>)</a>
		<div id="project_list"><ul>
			<li>项目：</li>
			<?php
        foreach( $_G['projects'] as $k => $t){
          $attr = $thisPid == $k ? ' class="on"' : '';//class
          echo '<li'.$attr.'><a href="./?pid='.$k.'">'.$t.'('.$mybugs[$k].')</a></li>';
        }
      ?>
		</ul></div>
	</div>
</div>
<div class="main">

<div class="menu clearfix">
	<ul id="types">
    	<li class="first-child"><a href="./">返回列表</a></li><li class="on"><a href="./report.php">项目报告</a></li>
    </ul>
</div>
<div class="content">
	<div id="filter">
		<input type="text" id="searchBug" value="<?php echo isset($_GET['search']) ? $_GET['search'] : 'Bug搜索/ID查询' ?>" />
		<span class="numbers">显示：<?php echo $numbers?></span> 
		<form action="?report.php" method="get">
    	状态： <!--<label><input type="radio" name="status"  /> 全部</label> -->
        <?php
        foreach( $_G['status'] as $k => $t){
					$checked = in_array($k, $filter) ? ' checked="checked"':'';
          echo '<label title="'.$t.'"><input type="checkbox" name="status[]" value="'.$k.'"'.$checked.' /> '. _L($t).'</label> ';
        }
        ?>
        <a id="c_all" href="javascript:void(0)">全选</a>/<a id="c_unall" href="javascript:void(0)">不选</a>
        <input type="hidden" name="type" value="<?php echo $type;?>" />
				<input type="hidden" name="viewall" value="1" />
				<input type="hidden" name="date" value="<?php echo $date;?>" />
				<!--input type="hidden" name="pid" value="<?php echo $thisPid;?>" /-->
				<?php
					if( isset($_GET['search']) ) echo '<input type="hidden" name="search" value="'.$_GET['search'].'" />';
				?>
        <button type="submit">筛选</button>
			</form>
    </div>
		
		<div class="report">
		<?php
		$curPid = '';
		if( count( $items) > 0 ){
			foreach( $items as $i){
				$status = $i['status'];
				$flag = ' class="'.$_G['status'][$status].'"';
				//echo '<li id="bug_'.$i['id'].'" type="'.$i['type'].'"'.$assigned.'><div><b class="id">'.$i['id'].'</b> <em><span'.$flag.' status="'.$i['status'].'">['.$i['status_name'].']</span></em><strong>'.$i['content'].'</strong> '.$attach.'<span>'.$i['ver'].'</span></div></li>';
				
				if( $i['pid']!=$curPid ){
					$cid = $i['pid'];
					echo '<h2>'.$_G['projects'][$cid].'</h2>';
					$curPid = $cid;
				}
				
				?>
			<div type="<?php echo $i['type'];?>" id="bug_<?php echo $i['id'];?>" class="report-items">
				<h6><a href="./?pid=<?php echo $i['pid'];?>&search=<?php echo $i['id'];?>" target="_blank">Bug-<?php echo $i['id'];?></a> / 
					<span<?php echo $flag;?> status="<?php echo $i['status'];?>">[<?php echo $i['status_name'];?>]</span> / 
					<a href="./?pid=<?php echo $i['pid'];?>&type=<?php echo $i['type'];?>" target="_blank"><?php echo $i['name'];?></a>
					<em><?php echo date('Y-m-d H:i:s', $i['timestamp']) ?>
					by <?php echo $i['creatorName'];?></em>
				</h6>
				<div class="desc">
					@<?php echo $userNames[$i['assignto']];?> : 
					<?php echo $i['content'];?>
					<div class="files">
						<?php
							if(!empty($i['files'])){
							foreach( $i['files'] as $f ){
								$urls = explode( '.', $f );
								$index = count($urls)-1;
								$ext = strtolower($urls[$index]);
								$out = in_array( $ext, array('jpg', 'png', 'gif') ) ? '<img src="'.$f.'" />' : $ext.'文件';
								echo '<a href="'.$f.'" target="_blank">'.$out.'</a>';
							}}
						?>
					</div>
				</div>
			</div>
				<?php
			}
		}else{
			echo '<li class="none">木有发现相关bug！</li>';
		}
    ?>
		</div>
		
		<div class="stats">
			<table>
				<tr>
					<th>负责人</th><th>总活动bug</th><th>KEY</th><th>已处理</th>
				</tr>
				<?php
					if( count( $stats) > 0 ){
					foreach( $stats as $k => $stat ){
						$total = isset($stat['total']) ? $stat['total'] : 0;
						$total = $k > 0 ? '<a href="./report.php?pid=0&search={'.$k.'}">'.$total.'</a>' : $total;
				?>
					<tr>
						<td><?php echo $stat['name'];?></td>
						<td><?php echo $total; ?></td>
						<td><?php echo isset($stat['key']) ? $stat['key']:'-';?></td>
						<td><?php echo isset($stat['fixed']) ? $stat['fixed']:0;?></td>
					</tr>
				<?php
					}}
				?>
			</table>
		</div>

</div>
<?php include './tpl/foot.tpl.htm';	?>

</div>
<!--main end-->

<script type="text/javascript" src="./img/jquery.min.js"></script>
<!--script type="text/javascript" src="fileuploader.js"></script-->
<script type="text/javascript" src="common.js"></script>
<?php echo $foot_out?>
</body>
</html>