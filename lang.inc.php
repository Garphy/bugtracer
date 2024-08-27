<?php
function _L($k) {
	$LANG = [
		'closed' => '已关闭',
		'new' => '新增',
		'key' => '重要',
		'part_fixed' => '部分处理',
		'fixed' => '已解决',
		'wont_fix' => '不处理',
		'todo' => '待办',
		'idea' => '备忘'
	//'' =>'',
	];

	return $LANG[$k] ?? $k;
}
?>
