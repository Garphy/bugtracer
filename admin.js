//管理模式
function addsub(){
	$('#typelist').append('<li><input type="text" tid="0" value="" name="tid[]"> <a href="javascript:void(0)" class="del">X</a></li>');
	init();
	$('#typelist li:last input').focus();
}
function delType(obj){
	var li = obj.parent();
	var input = li.find('input');
	if( !confirm('确定删除子分类：【'+ input.val() +'】？') ) return false;
	if( parseInt(input.attr('tid'))>0 ){
		input.val('TO_BE_REMOVED');
		li.hide();
	}else{
		li.remove();
	}
	return true;
}
function init(){
	$('#typelist li .del').unbind().bind( 'click', function(){ delType($(this)); });
	if($('#msg').html()=='') $('#msg').hide();
}
$(document).ready(init);