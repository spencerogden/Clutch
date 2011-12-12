(function( $ ){
    $.fn.gridslide = function( options ){
	var settings = $.extend( {
		'threshold' : .2,
	    }, options);

	return this.each(function(){
		var init_x = null;
		var init_y = null;
		var init_box = null;

		var gridwrap = $(this);

		var width  = parseInt(gridwrap.width() ,10);
		var height = parseInt(gridwrap.height(),10);
		
		var flip_thresh = parseInt(width  * settings['threshold'], 10);
		var vert_thresh = parseInt(height * settings['threshold'], 10);
		
		gridwrap.children('div:first').css('left',0).children(':first').css('top',0);

		gridwrap.children('div').each(function(){
			var label = $('<div class="groupLabel">' + $(this).attr('title') + '</div>').css({
				    'position'           : 'absolute',
				    'padding'            : '1em',
				    'top'                : '25%',
				    'background-color'   : 'dimgray',
				    'color'              : 'white',
				    'font-family'        : 'sans-serif',
				    'border-radius'      : '15px',
				    'user-select'        : 'none',
				    '-webkit-user-select': 'none',
				    '-khtml-user-select' : 'none',
				    '-moz-user-select'   : 'none',
				    '-o-user-select'     : 'none',
					}).appendTo($(this));
			label.css({'left' : (width - label.width())/2-20,});

		    });



		var moveInfo = function(e){
		    //Correct position in current box
		    if( e.type == 'touchmove' ){
			w.preventDefault();
			var pos_x = e.originalEvent.touches[0].pageX - gridwrap.offset().left;
			var pos_y = e.originalEvent.touches[0].pageY - gridwrap.offset().top;
		    }else{
			var pos_x = e.pageX - gridwrap.offset().left;
			var pos_y = e.pageY - gridwrap.offset().top;
		    }

		    //Set our initial position if this is the start of a new move
		    if( init_x === null ){
			init_x = pos_x;
			init_y = pos_y;
			init_box = $(this);
		    }

		    //Move relative to init
		    var move_x = init_x - pos_x;
		    var move_y = init_y - pos_y;

		    //Move the current Box to the point
		    $(this).parent().css({left: -move_x});
		    $(this).css({top: -move_y});

		    var right_neighbor = $(this).parent().next('div');
		    var left_neighbor = $(this).parent().prev('div');
		    
		    //Move neighbor groups (left/right) into place
		    if( right_neighbor.length && -move_x < 0 ){
			right_neighbor.css({left: width - move_x});
		    }else{
			right_neighbor.css({left: width});
		    }

		    if( left_neighbor.length && -move_x > 0 ){
			left_neighbor.css({left: -width - move_x});
		    }else{
			left_neighbor.css({left: -width});
		    }

		    //Move neighbor Boxes (up/down) into place
		    var up_neighbor = $(this).prev('div');
		    var dn_neighbor = $this.next('div:not(.groupLabel)');

		    if(up_neighbor.length && -move_y > 0){
			up_neighbor.css({top: -height - move_y});
		    }else{
			up_neighbor.css({top: -height});
		    }

		    if(dn_neighbor && -move_y < 0){
			dn_neighbor.css({top: height - move_y});
		    }else{
			dn_neighbor.css({top: height});
		    }
		}

		var panelAnimate = function($this){
		    var group = $this.parent();
		    var left_neighbor = group.prev('div');
		    var right_neighbor= group.next('div');
		    var up_neighbor = $this.prev('div');
		    var dn_neighbor = $this.next('div:not(.groupLabel)');

		    var pan_x = parseInt(group.css('left'), 10);
		    var pan_y = parseInt($this.css('top'), 10);
		    
		    if( pan_x < -flip_thresh && right_neighbor.length ){
			//User pulled to the left
			$('.groupLabel').stop(true,true).fadeIn(0);
			group.animate({left: -width});
			right_neighbor.animate({left: 0});
			$this.animate({top:0});
		    }else if( pan_x > flip_thresh && left_neighbor.length ){
			//User pulled to the right
			$('.groupLabel').stop(true,true).fadeIn(0);
			group.animate({left:width});
			left_neighbor.animate({left:0});
			$this.animate({top:0});
		    }else if( pan_y < -vert_thresh && dn_neighbor.length ){
			//User pulled to the top
			$this.animate({top: -height});
			dn_neighbor.animate({top:0});
			group.animate({left:0});
		    }else if(pan_y > vert_thresh && up_neighbor.length ){
			//User pulled to bottom
			$this.animate({top:height});
			up_neighbor.animate({top:0});
			group.animate({left:0});
		    }else{
			//Spring Back
			group.animate({left: 0});
			left_neighbor.animate({left: -width});
			right_neighbor.animate({left: width});
			$this.animate({top: 0});
			up_neighbor.animate({top: -height});
			dn_neighbor.animate({top: height});
		    }

		    fadeLabels();
		}

		var fadeLabels = function(){
		    setTimeout(function(){ 
			    gridwrap.find(".groupLabel").stop(true,true).fadeOut(2000);
			}, 500);
		}

		var resetVars = function(){
		    init_x   = null;
		    init_y   = null;
		    init_box = null;
		}

		gridwrap.find('.Box').bind("mousedown", function(e){
			$(this).bind("mousemove", moveInfo);
		    });
		gridwrap.find('.Box').bind('touchstart', function(e){
			console.log('touch start');
			$(this).bind('touchmove', moveInfo);
		    });
		
		gridwrap.find('.Box').bind('mouseup', function(e){
			$(this).unbind('mousemove', moveInfo);
			panelAnimate($(this));
			resetVars();
		    });
		gridwrap.find('.Box').bind('touchend', function(e){
			console.log('touch stop');
			$(this).unbind('touchmove', moveInfo);
			panelAnimate($(this));
			resetVars;
		    });

		$(document).bind('mouseleave', function(e){
			var from = e.relatedTarget || e.toElement;
			if( !from || from.nodeName === 'HTML' ){
			    if(init_box){
				panelAnimate(init_box);
				init_box.unbind('mousemove', moveInfo);
				init_box.unbind('touchmove', moveInfo);
				resetVars();
			    }
			}
		    });

		fadeLabels();

	    
		    
	    });
    };
})( jQuery );

