//by Garphy 
/* config */
var liHight = 35;
var timer_config = 2000;
/* eof config */
var isMobile = !!navigator.userAgent.match(/mobile/i);
var timer;
//flag mousover
function showflagger( obj ){
	clearTimeout(timer);
	var flaggerLayer = $('#flaggerLayer');
	var li = obj.parents('li:eq(0)');
	var id = parseInt(obj.html());
	if( id==0 ) return false;
	if( id == $('#changeId').val() && flaggerLayer.is(':visible') ){
		flaggerLayer.hide();
		return false;
	}
	$('#changeId').val(id);
	var n = $('#items li').index(li);
	var t = 36+liHight*(n+1);
	flaggerLayer.css('top', t).show();
	timer = setTimeout( hideflagger, timer_config );
}
//hide flagger
function hideflagger(){
	clearTimeout(timer);
	$('#flaggerLayer').hide();
	$('#items b').removeClass('over');
}
//not null
function empty(val){
	return ( typeof(val)=='undefined' || val==null || val=='' ) ? true:false;
}
//unfilter
function unfilter(str){
	str = str.replace( /&nbsp;/gi, ' ')
		.replace( /&quot;/gi, '"')
		.replace( /&#39;/gi, "'")
		.replace( /&lt;/gi, "<")
		.replace( /&gt;/gi, ">");
	return str;
}
//newbug
function newbug(){
	reset_dlg();
	$('#add_detail').hide();
	$('#add_content').css('visibility', 'visible');	
	$('#dlg .roll').hide();
	if( cur_type != 'all') $('#add_type').val(cur_type);
	show_dlg();
	setTimeout( function(){ $('#add_content').focus(); }, 500 );
}
//post bug
function postbug(){
	var self = $(this);
	var id = $('#add_id').html();
	var status = $('#add_status').val();
	var action = id==0 ? 'new' : 'edit';
	var type = $('#add_type').val();
	var content = $('#add_content').val();
	var ver = $('#add_ver').val();
	var assignto = $('#add_assignto').val();
	var files = $('#add_files').val();
	var creator = '';
	if( !(type > 0 && content !='') ){
		$('#add_err').html('提交内容不完整');
		setTimeout( function(){ $('#add_err').html(''); }, 3*1000);
		return false;
	}
	self.addClass('loading');
	$.ajax({
		type: "POST",
		url: 'ajax.php?action='+action,
		data: 'id='+id+'&type='+type+'&content='+encodeURIComponent(content)+'&ver='+ver+'&assignto='+assignto+'&files='+files,
		success: function(return_id){
			if( !checkReturn( return_id ) ) return false;
			if( content.length > 90 ) content = content.substr(0, 90) + ' <a class="more" href="javascript:void(0);">[...]</a>';
			var newli = $('<li id="bug_'+return_id+'" type="'+type+'"><div><b class="id">'+return_id+'</b> <em><span class="'+G_status[status]+'" status="'+status+'">['+G_status[status]+']</span></em><strong>'+content+'</strong> <span>'+ver+'</span> </div></li>');
			if( action == 'new'){
				$('#items').prepend(newli);
			}else if( action == 'edit'){
				$('#bug_'+id).replaceWith(newli);
			}
			var newclass = assignto==0 ? 'new unassigned':'new';
			newli.dblclick(function(){ edit( $(this) )}).addClass(newclass);
			init();
			setTimeout(function(){ newli.removeClass('new'); },3000);
			$('#dlg').hide();
			reset_dlg();
		},
		error: function(){
			err();
			self.removeClass('loading');
		}
	}); 
}
//edit
function edit(obj){
	reset_dlg();
	var id = obj.find('b').html();
	if( !(id>0) ){
		console.log( 'id = null' );
		return false;
	}
	$('#add_id').html(id);
	$('#add_detail span').html('Loading...');
	var pics = [];
	var format = function(html){//format
		html = html.replace(/(https?\:\/\/(?:\w+\.)?\w+\.\w+\/[\/\?&;\.\-%+=_A-Za-z0-9]{0,}(?:#\w+)?)/g, '<a href="$1" target="_blank">$1</a>')
			.replace(/\[b\](.*?)\[\/b\]/gi, '<b>$1</b>')
			.replace(/\n/g, '<br />')
			.replace(/图(\d+)/g, function(str, no){
				if(typeof(pics[no])=='undefined'){
					return str;
				}else{
					var pic = pics[no];
					pics[no] = '';
					return str+'：<a href="'+pic+'" target="_blank" title="点击查看大图"><img src="'+pic+'" alt="图片载入中..." /></a>';
				}
			});
		//show other pics
		for(i=0;i<pics.length;i++){
			if( !empty(pics[i]) ){
				var pic = pics[i];
				var names = pic.split('.');
				var index = names.length-1;
				var ext = names[index];
				ext = ext.toLowerCase();
				if( ext=='jpg' || ext=='gif' || ext=='png' ) html += '<br />图'+i+'：<a href="'+pic+'" target="_blank" title="点击查看大图"><img src="'+pic+'" alt="图片载入中..." /></a>';
			}
		}
		return html;
	};
	var autoHeight = function(){
		var h = $('#add_detail').height();
		$('#add_content').height(h+'px');
	};
	$.getJSON( 'ajax.php?action=get&id='+id+'&_='+(new Date().getTime()), function(json){
		if( json == -1 ) checkReturn(json);
		var content = json.content;
		if( !json.content ) alert('err in getting data!');
		$('#add_type').val(json.type);
		$('#add_status').val(json.status);
		$('#add_ver').val(json.ver);
		if( $('#add_assignto option[value='+json.assignto+']').length == 0 ) alert('被指派人不属于本项目！');
		$('#add_assignto').val(json.assignto);
		$('#add_content').val( unfilter(content) );
		var updateInfo = json.lastchanger=='' ? '' : ' / Updated by '+ json.lastchanger;
		if( !!json.fullname ) $('#add_creator').html('posted by '+json.fullname+ updateInfo +' @'+json.changetime);
		if( !empty(json.files) ){
			$('#add_files').val(json.files);
			var filelist = json.files.split('|');
			//files
			var list = '';
			for(var i=0;i<filelist.length;){
				realname = filelist[i];
				link = './uploads/'+ cur_pid + '/' + realname;
				var names = realname.split('.');
				var index = names.length - 1;
				var ext = names[index].toUpperCase();
				list += '<li>' +
						'<span class="qq-upload-file"><a href="'+ link +'" target="_blank">附件'+ (++i) +'：'+ ext +'</a></span>' +
						'<a href="'+ link + '" target="_blank">[view]</a>' +
						'<a href="javascript:void(0)" onclick="delfile(\''+ realname +'\', '+ cur_pid +', this)" class="del">[X]</a>' +
				'</li>';
				pics[i] = link;
			}
			$('#file-uploader .qq-upload-list').html(list);
		}
		$('#add_detail span').html( format(content) );
		autoHeight();
		if( $('#add_detail span img').length ) $('#add_detail span img').load(autoHeight);
	}); 
	show_dlg();
}
//close dlg
function show_dlg(){
	var scrollTop = window.pageYOffset 
		|| document.documentElement.scrollTop 
		|| document.body.scrollTop 
		|| 0;
	var t = scrollTop + 30;
	$('#dlg').css('top', t+'px').show();
}
//close dlg
function close_dlg(){
	$('#dlg').hide();
	reset_dlg();
}
//reset dlg
function reset_dlg(){
	$('#add_id').html(0);
	$('#add_creator').html('');
	$('#add_type').val('');
	$('#add_status').val(G_status_default);
	$('#add_content').val('').height('100px').css('visibility', 'hidden');
	$('#add_detail span').html('');
	$('#add_detail').show();
	$('#add_ver').val(cur_ver);
	$('#add_assignto').val(0);
	$('#add_files').val('');
	$('#file-uploader .qq-upload-list').html('');
	$('#addbug').removeClass('loading');
	$('#dlg .roll').show();
}
//change status
function changeStatus(status){
	id = $('#changeId').val();
	flag(id,status);
	hideflagger()
}
//change status
function flag(id, status){
	$.ajax({
		type: "POST",
		url: "ajax.php?action=flag",
		data: 'id='+id+'&status='+status,
		success: function(return_id){
			if( !checkReturn( return_id ) ) return false;
			var node = $('#bug_'+return_id);
			node.find('em').html( '<span class="'+G_status[status]+'" status="'+status+'">['+G_status[status]+']</span>' ).removeClass();
			node.addClass('new');
			setTimeout(function(){ node.removeClass('new'); },3000);
			//if(status == 3)node.find('em').addClass('fixed');
		},
		error: function(){ alert('System error!');}
	}); 
}
//addfile
function addfile(id, files){
	$.ajax({
		type: "POST",
		url: "ajax.php?action=addfile",
		data: 'id='+id+'&files='+files,
		success: function(return_id){
			if( !checkReturn( return_id ) ) return false;
			//done
		},
		error: function(){ alert('System error!');}
	}); 
}
//del file
function delfile( filename, pid, obj){
	var id = parseInt($('#add_id').html());
	if( !id || !confirm('确定删除此附件！？') ) return false;
	var self = $(obj);
	$.ajax({
		type: "POST",
		url: "ajax.php?action=delfile",
		data: 'id='+id+'&pid='+pid+'&filename='+filename,
		dataType: 'json',
		success: function( json ){
			if( !checkReturn( json.result ) ) return false;
			if( $('#add_detail:hidden').length ){//编辑界面不重新加载
				self.parent().remove();
				$('#add_files').val( json.files );
			}else{//查看界面重新加载
				edit( $('#bug_'+id) );
			}
		},
		error:function( err ){
			console.log(err);
		}
	});
}
function roll( type ){
	var id = $('#add_id').html();
	if( !(id>0) ) return false;
	if( type=='next' )
		var obj = $('#bug_'+id).next();
	else if ( type=='prev' )
		var obj = $('#bug_'+id).prev();
	else 
		return false;
	if( obj.find('b.id').length ) edit(obj);
}
function checkReturn( flag ){
	if( flag == -1 ){
		err('登录超时，请重新登录！');
		return false;
	}else if( !/^\d+$/.test( parseInt(flag) ) || flag == 0 ){
		err('result mismatch!');
		return false;
	}
	return true;
}
function err(){
	var msg = arguments.length ? arguments[0]:'system error!';
	alert(msg);
}
//upload
function createUploader(){            
	var uploader = new qq.FileUploader({
			element: document.getElementById('file-uploader'),
			action: './upload.php',
			allowedExtensions: ['jpg','gif','png','txt','doc','docx','rar','zip','xls','xlsx'],
			sizeLimit: 1048576,//1M
			params: {
        pid: cur_pid
			},
			onComplete: function( no, fileName, data){
				var realname = data.filename;
				var link = ' <a href="./uploads/'+cur_pid + '/' + realname+'" target="_blank">[view]</a>' +
					'<a href="javascript:void(0)" onclick="delfile(\''+ realname +'\', '+ cur_pid +', this)" class="del">[X]</a>';
				$('#f_'+no).append(link);
				var filelist = $('#add_files').val() == '' ? []:$('#add_files').val().split('|');
				filelist.push(realname);
				var files = filelist.join('|');
				$('#add_files').val( files );
				var id = parseInt($('#add_id').html());
				if( id != 0)addfile(id, files);
			},
			debug: false
	});
	$('#file-uploader .qq-upload-drop-area a').click(function(){
		$('#file-uploader .qq-upload-drop-area').hide();
	});
}
//init
function init(){
	//html font-size init
	if( $('html').css('font-size')=='12px' ){
		$('html').css('font-size','12px')
	}
	//edit
	$('#items li').unbind().bind( 'dblclick', function(){
		edit( $(this) )
	});
	if( isMobile ){ //is mobile?
		$(document.documentElement).addClass('M');
		timer_config = 3000;
		$('#items li').unbind().bind( 'click', function(){
			edit( $(this) )
		});
		/*.bind( 'touchstart', function(e){
			if (e.cancelable) {
				 if (!e.defaultPrevented) {
					 e.preventDefault();
				 }
			 }
		}).bind( 'touchend', function(){
			edit( $(this) )
		});*/
		$('#project_switch').unbind().click(function(){
			$('#project_list').toggle();
			$('#filter').toggle();
		});
		//$('#add_detail .edit').click(function(){
		//	$('#add_content').show();
		//});
	}
	
	//mode switch
	if( isAdmin ) $('.top .mode').show();

	$('#items li a[class="more"]').click(function(){
		edit( $(this).parents('li:eq(0)') );
	});
	//flagger
	//$('#items .flagger').unbind().bind( 'mouseover', showflagger );
	$('#items b.id').unbind().bind( 'mouseover', function(){
		$(this).addClass('over');
	}).bind( 'mouseout', function(){
		$(this).removeClass('over');
	}).bind( 'click', function(e){
		showflagger( $(this));
		e.stopPropagation();
	});
	//set flag
	$('#items em').unbind().bind( 'mouseover', function(){
		$(this).addClass('over');
	}).bind( 'mouseout', function(){
		$(this).removeClass('over');
	});
	$('#items em span').bind( 'click', function(e){
		var status = $(this).attr('class');
		if( ( !isAdmin && status == 'fixed') || 
			( status != 'fixed' && status != 'part_fixed' && status != 'new' && status != 'key' )
		) return false;
		var id = parseInt($(this).parents('li:eq(0)').attr('id').substr(4));
		var set2 = status=='fixed' ? 0 : G_status_fixed;
		flag(id,set2);
		e.stopPropagation();
	});
}
$(document).ready(function(){
	//cur tab
	if( $('#types .on').length==0 ) $('#types li:first-child').addClass('on');
	//new bug
	$('#types .add a').click( newbug );
	$('#addbug').click( postbug );
	$('#add_content').keydown( function(e){
		e = e || window.event;
		if( e.ctrlKey && e.which == 13 ) postbug();
	});
	//filter
	$('#c_all').click(function(){ $('#filter input[type="checkbox"]').prop('checked', true); });
	$('#c_unall').click(function(){ $('#filter input[type="checkbox"]').removeAttr('checked'); });
	$('#filter input[type="checkbox"]').add('#filter label').dblclick(function (){
		$('#filter input[type="checkbox"]').removeAttr('checked');
		$(this).find('input[type="checkbox"]').prop('checked', true);
		$('#filter button').click();
	});
	//flagger
	$('#flaggerLayer').mouseover(function(){
		clearTimeout(timer);
		$('#flaggerLayer').show().mouseout( hideflagger );
	});
	var searchText = $('#searchBug').val();
	$('#searchBug').focus(function(){ $(this).val('');})
		.blur(function(){$(this).val(searchText);})
		.keydown( function(e){
		e = e || window.event;
		if( e.which == 13 ) location.href = '?pid='+ cur_pid +'&search='+ $(this).val();
	});
	//project_switch
	$('#project_switch').mouseover( function(){
		$('#project_list').show();
	}).mouseout( function(){
		$('#project_list').hide();
	}).click( function(){
		$('#project_list').toggle();
	});;
	//dlg
	$('#add_detail .edit').click(function(){
		$('#add_detail').hide();
		$('#add_content').height('200px').css('visibility', 'visible');
	});
	$('#dlg .prev').click(function(){
		roll('prev');
	});
	$('#dlg .next').click(function(){
		roll('next');
	});
	//shortcuts
	$(document).keydown( function(e){
		e = e || window.event;
		//:Ctrl + ~
		if( e.ctrlKey && e.which == 192 ) newbug();
		//:ESC
		if( e.which == 27 && ( $('#add_content').css('visibility')=='hidden' || ($('#add_content').val().length==0) ) )
			close_dlg();
	});
	init();
	try{createUploader();}catch(e){}
});
