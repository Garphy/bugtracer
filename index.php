<?php
/* bugTracer v1.0	by Garphy

todo:
字段整理，诸如tid、type统一
密码验证优化，加密post

权限系统；
删除分类同时删除bug；
一个bug分配多个人；

bug:
*/
define('SELFNAME', 'INDEX');
include 'common.inc.php';

$foot_out = '';
$type = isset($_GET['type']) ? intval($_GET['type']):'all';
$page = isset($_GET['page']) ? intval($_GET['page']):1;
$order = isset($_GET['order']) ? filter($_GET['order']):'id';
$filter = array();
$filter = isset($_GET['status']) ? $_GET['status']:$_G['defaultFilter'];
//search
if( isset($_GET['search']) ){
	$sql = "SELECT i.*, t.name FROM `items` AS i LEFT JOIN `types` AS t ON i.type = t.tid WHERE t.pid={$thisPid}";
	if(  $_GET['search'] == 'alll' ){//all
		header('Location:./report.php');
	}else if( preg_match( '/^\d+,?/', $_GET['search'] ) ){//by id
		$ids = explode(',', $_GET['search']);
		foreach($ids as $k => $id){
			$ids[$k] = intval($id);
			if( $ids[$k]==0 ) unset($ids[$k]);
		}
		$sql .= " AND i.id in (". implode(',', $ids) .")";
		if(count($ids)==1){//auto popup edit
			$foot_out = '<script type="text/javascript">$(document).ready(function(){if($("#bug_"+'.$_GET['search'].'))edit($("#bug_"+'.$_GET['search'].'))})</script>';
		}
	}else if( preg_match( '/^\((\d+)\)$/', $_GET['search'], $match ) ){//by creator
		$user = $match[1];
		$sql .= " AND i.creator = {$user}";
		$sql .= ' AND i.status in ('.implode(', ', $filter).')';
	}else if( preg_match( '/^{(\d+)}$/', $_GET['search'], $match ) ){//by assignto
		$user = $match[1];
		$sql .= " AND i.assignto = {$user}";
		$sql .= ' AND i.status in ('.implode(', ', $filter).')';
	}else if( preg_match( '/^!{(\d+)}$/', $_GET['search'], $match ) ){//assignto excluded
		$user = $match[1];
		$sql .= " AND i.assignto != {$user}";
		$sql .= ' AND i.status in ('.implode(', ', $filter).')';
	}else if( preg_match( '/^{(\d{4}-\d+-\d+)~(\d{4}-\d+-\d+)}$/', $_GET['search'], $match ) ){//by changetime
		$from = $match[1];
		$to = $match[2];
		$time0 = explode('-', $from);
		$time1 = explode('-', $to);
		$t0 = mktime( 0,0,0,$time0[1],$time0[2],$time0[0] );
		$t1 = mktime( 0,0,0,$time1[1],$time1[2],$time1[0] );
		$sql .= " AND i.changetime >= {$t0} AND i.changetime < {$t1}";
		$sql .= ' AND i.status in ('.implode(', ', $filter).')';
	}else{//by keywords
		$str = filter($_GET['search']);
		$sql .= " AND i.content LIKE '%{$str}%'";
	}
//list
}else{
	$cond = array();
	if( $type!='all' ) $cond[] = 'i.type = '.$type;
	if( count($filter) ) $cond[] = 'i.status in ('.implode(', ', $filter).')';
	//if( $_G['role'] == 'coder' ) $cond[] = isset($_GET['viewall']) ? 'i.assignto > 0 ' : 'i.assignto = '.$_G['uid'];//开发人员搜索可以查到所有已指派问题。
	if( $_G['mode'] == 'coder' ) $cond[] = 'i.assignto = '.$_G['uid'];//限制开发人员只能查看自己的问题
	$cond[] = "t.pid={$thisPid}";
	$sql_clause = '';
	$sql_clause .= ' WHERE '.implode( ' AND ', $cond );
	$sql = " FROM `items` AS i LEFT JOIN `types` AS t ON i.type = t.tid";
	$sql_items = "SELECT i.*, t.name".$sql;
	//pages
	$sql_pages = "SELECT count(id) as total".$sql;
	$sql = $sql_pages.$sql_clause;
	$result = mysql_query($sql);
	$row = mysql_fetch_array($result);
	$shown_items = $row['total'];
	$pages_total = ceil( $shown_items/PAGESIZE );
	$limitFrom = ($page-1)*PAGESIZE;
	//order
	if( count($filter)==1 && $filter[0]==4 ) $order = 'changetime';//order by time for fixed
	$sql_clause .= ' ORDER BY i.'.$order.' desc';
	$sql_clause .= " LIMIT {$limitFrom}, ".PAGESIZE;
	$sql = $sql_items.$sql_clause;
}
//echo "<!--$sql-->";
$titleMaxLen = 176;
$result = mysql_query($sql);
$items = array();
if(mysql_num_rows($result)){
while($row = mysql_fetch_array($result)){
	$row['status_name'] = $_G['status'][$row['status']];
	if( $type == 'all' ) $row['content'] = '『'.$row['name'].'』'.$row['content'];
	$row['content'] = ( strlen($row['content']) > $titleMaxLen ) ? 
		makeTages( mb_strcut( $row['content'], 0, $titleMaxLen, 'utf-8') ).' <a class="more" href="javascript:void(0);">[...]</a>'
		:
		makeTages( $row['content'] );
	$row['attach'] = empty($row['files']) ? false:true;
	$row['assigned'] = (
		$_G['mode'] == 'coder' && $row['assignto'] != $_G['uid'] || 
		$row['assignto']==0 && in_array( $row['status'], $_G['defaultFilter'] )
		) ? false:true;
	$items[] = $row;
}}
//total items
if( !isset($shown_items) ) $shown_items = mysql_num_rows($result);
$sql = "SELECT count( id ) as total FROM `items` WHERE type in (".implode(',', $_G['typeid']).")";
if( $type!='all' ) $sql.= ' AND type = '.intval($type);
$result = mysql_query($sql);
$row = mysql_fetch_array($result);
$total_items = $row['total'];
$numbers = $shown_items.'/'.$total_items;
//user list
$sql = !empty($_G['members']) ? " WHERE role = 'admin' OR uid in (".implode(',', $_G['members']).")" : '';
$sql = "SELECT uid, role, fullname FROM `users`".$sql." ORDER BY role DESC";
$result = mysql_query($sql);
$userlist = '';
while($row = mysql_fetch_array($result)){
	$name = $row['role']=='coder' ? $row['fullname'] : '（'.$row['fullname'].'）';
	$userlist .= '<option value="'.$row['uid'].'">'.$name.'</option>';
}
//title
$page_title = empty($_G['prjName']) ? '':$_G['prjName'].' - ';
//pages
function makePages(){
	global $page, $pages_total;
	if( $pages_total < 2 ) return '';
	$url = preg_replace( '/(?:^|&)page=(\d+)?&?/', '', $_SERVER["QUERY_STRING"] );
	$out = '';
	$out .= '<li id="pages"><div>';
	if( $page != 1 ) $out .= '<a href="?'.$url.'&page='.($page-1).'">&lt;&lt;</a>';
	$out .= '<span class="on">'.$page.'/'.$pages_total.'</span>';
	if( $page != $pages_total ) $out .= '<a href="?'.$url.'&page='.($page+1).'">&gt;&gt;</a>';
	$out .= '</div></li>';
	return $out;
}
//[b] => <b> 、add link
function makeTages( $str ){
	$availableTags = array('b');
	$str = preg_replace( '/\[('.implode( '|', $availableTags).')\](.*?)\[\/\1\]/', '<\\1>\\2</\\1>', $str );
	$str = preg_replace( '/\[\/?('.implode( '|', $availableTags).')?(\]|$)/', '', $str );
	$str = preg_replace( '/(https?\:\/\/(?:\w+\.)?\w+\.\w+\/[\/\?&\.\-%+=_A-Za-z0-9]{0,}(?:#\w+)?)(\s)/', '<a href="\\1" target="_blank">\\1</a>\\2', $str);//links
	return $str;
}
?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title><?php echo $page_title;?>BugTracer</title>
<link rel="stylesheet" href="style.css" />
<link rel="stylesheet" href="img/fileuploader.css" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=Edge，chrome=1">
<?php if($_G['role']!='admin'){ ?>
<style type="text/css">
.content li .over span.fixed { background-image:url(img/tick_solid.png) !important;}
</style>
<?php } ?>
<script type="text/javascript">
var isAdmin = <?php echo $_G['role']=='admin' ? 1:0 ?>;
var cur_pid = '<?php echo $thisPid ?>';
var cur_ver = '<?php echo $_G['cur_ver'] ?>';
var cur_type = '<?php echo $type ?>';
var G_status = ['<?php echo implode("', '", $_G['status']) ?>'];
var G_status_default = <?php echo $_G['status_default'] ?>;
var G_status_fixed = <?php echo $_G['status_fixed'] ?>;
</script>
</head>
<body>
<div class="top">
	<div class="login">
		<span>Login as: <?php echo getNameByUid( $_G['uid'] ) .' ('. $_G['username'].')' ?></span>
		<a href="?logout">[退出]</a>
	</div>
	<div class="mode">
		<?php
			$modes = array(
				'admin' => array( 'name'=>'管理模式', 'target'=>'Debug模式', 'link'=>'debugmode' ),
				'coder' => array( 'name'=>'Debug模式', 'target'=>'管理模式', 'link'=>'adminmode' )
			);
			$mode = $modes[$_G['mode']];
		?>
		<span>当前处于：<?php echo $mode['name']?></span>
		<a href="?<?php echo $mode['link']?>">[切<?php echo $mode['target']?>]</a>
	</div>
	<div class="projects" id="project_switch">
		<a href="javascript:void(0)" class="flag">总活动Bug<em>(<?php echo $mybugs['total']?>)</em> 当前项目：<?php echo $_G['prjName'];?>(<?php echo $mybugs[$thisPid]?>)</a>
		<div id="project_list"><ul>
			<li>项目：</li>
			<?php
        foreach( $_G['projects'] as $k => $t){
          $attr = $thisPid == $k ? ' class="on"' : '';//class
          echo '<li'.$attr.'><a href="?pid='.$k.'">'.$t.'('.$mybugs[$k].')</a></li>';
        }
      ?>
		</ul></div>
	</div>
</div>
<div class="main">

<div class="menu clearfix">
	<ul id="types">
    	<li class="first-child"><a href="?pid=<?php echo $thisPid?>&type=all">全部</a></li><?php
        foreach( $_G['types'] as $k => $t){
          $attr = $type == $k ? ' class="on"' : '';//class
          echo '<li'.$attr.'><a href="?pid='.$thisPid.'&type='.$k.'">'.$t.'</a></li>';
        }
      ?>
    	<li class="add"><a href="javascript:void(0)" title="快捷键：Ctrl+`">提交新bug</a></li>
    </ul>
</div>
<div class="content">
	<div id="filter">
		<input type="text" id="searchBug" value="<?php echo isset($_GET['search']) ? $_GET['search'] : 'Bug搜索/ID查询' ?>" />
		<span class="numbers">显示：<?php echo $numbers?></span> 
		<form action="" method="get">
    	状态： <!--<label><input type="radio" name="status"  /> 全部</label> -->
        <?php
        foreach( $_G['status'] as $k => $t){
					$checked = in_array($k, $filter) ? ' checked="checked"':'';
          echo '<label title="'.$t.'"><input type="checkbox" name="status[]" value="'.$k.'"'.$checked.' /> '. _L($t) .'</label> ';
        }
        ?>
        <a id="c_all" href="javascript:void(0)">全选</a>/<a id="c_unall" href="javascript:void(0)">不选</a>
        <input type="hidden" name="type" value="<?php echo $type;?>" />
				<input type="hidden" name="viewall" value="1" />
				<input type="hidden" name="pid" value="<?php echo $thisPid;?>" />
				<?php
					if( isset($_GET['search']) ) echo '<input type="hidden" name="search" value="'.$_GET['search'].'" />';
				?>
        <button type="submit">筛选</button>
			</form>
    </div>
	<ul id="items">
    <!--<li type="1" id="bug_1"><div><b>1</b> <em status="3" class="fixed">[fixed]<div class="flagger"></div>
        </em><strong>弹窗遮住任务栏</strong> <span></span> <span></span></div></li>-->
		<?php
		if( count( $items) > 0 ){
			foreach( $items as $i){
				$status = $i['status'];
				$flag = ' class="'.$_G['status'][$status].'"';
				$attach = $i['attach'] ? '<span class="attach">　</span>':'';
				$assigned = $i['assigned'] ? '' : ' class="unassigned"';
				$ver = empty($i['ver']) ? '' : '<span>'.$i['ver'].'</span>';
				echo '<li id="bug_'.$i['id'].'" type="'.$i['type'].'"'.$assigned.'><div><b class="id">'.$i['id'].'</b> <em><span'.$flag.' status="'.$i['status'].'">['.$i['status_name'].']</span></em><strong>'.$i['content'].'</strong> '.$attach.$ver.'</div></li>';
			}
		}else{
			echo '<li class="none">木有发现相关bug！</li>';
		}
    ?>
		<?php echo makePages();?>
	</ul>
    <!--flagger-->
    <div id="flaggerLayer">
    	<input type="hidden" id="changeId" />
        <ul>
					<?php
					foreach( $_G['status'] as $n => $status){
						if( $_G['role'] == 'coder' && !in_array( $status, array('fixed','part_fixed','wont_fix') ) ) continue;//coder禁止部分功能
						echo '<li><a href="javascript:void(0)" onclick="changeStatus('.$n.')" title="'.$status.'">设为：'._L($status).'</a></li>';
					}
					?>
        </ul>
    </div>
     <!--flagger end-->
</div>

<div class="tips">
Tips：^~ = 提交新bug；Esc = 关闭弹窗； ^Enter = 提交bug； 双击描述显示详情； 筛选复选框双击 = 单选； FF/Chrome支持拖拽上传图片； 灰色项目：无关项或未指派；
</div>

<?php include './tpl/foot.tpl.htm';	?>

</div>
<!--main end-->

<!--editor-->
<div id="dlg">
  <ul class="editor">
  	<li class="close"><a href="javascript:void(0)" onclick="close_dlg()">X</a></li>
		<li><label>Bug ID</label> <span id="add_id">0</span> <span id="add_creator"></span></li>
    <li><label>所属模块</label> <select id="add_type">
        <option value="" selected="selected" style="color:#999">-所属模块-</option>
        <?php
        foreach( $_G['types'] as $k => $t){
          echo '<option value="'.$k.'">'.$t.'</option>';
        }
        ?>
			</select>
			<div class="roll">
				<a class="prev" href="javascript:void(0)">&lt;上一条</a> | 
				<a class="next" href="javascript:void(0)">下一条&gt;</a>
			</div>
		</li>
    <li class="detail"><label>BUG描述</label> <div id="add_detail">
				<span></span>
				<a class="edit" href="javascript:void(0)">[编辑]</a>
			</div>
			<textarea id="add_content"></textarea>
		</li>
    <li><label>版本</label> <input type="text" id="add_ver" value="<?php echo $_G['cur_ver']; ?>" /></li>
		<li><label>指派</label> <select id="add_assignto"><option value="0">-</option><?php echo $userlist;?></select></li>		
		<li><div id="file-uploader"></div></li>
    <li><label>&nbsp;</label> <button class="btn" id="addbug">提交</button> <span id="add_err"></span> 
			<input type="hidden" id="add_status" value="<?php echo $_G['status_default'];?>" />
			<input type="hidden" id="add_files" value="" />
		</li>
  </ul>
</div>
<script type="text/javascript" src="./img/jquery.min.js"></script>
<script type="text/javascript" src="fileuploader.js"></script>
<script type="text/javascript" src="common.js"></script>
<?php echo $foot_out?>
</body>
</html>
