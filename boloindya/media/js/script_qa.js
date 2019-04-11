// enable nav dropdown in mobile device
// if ($(window).width() <= 767) {
  
//     $('.profile_link').click(function(e){
//         e.preventDefault();
//         //$('.navbar .navbar-nav .sub-menu').toggle('slow')
//         if($('.navbar .navbar-nav li .sub-menu').hasClass('active')){
//             $('.navbar .navbar-nav li .sub-menu').removeClass('active').hide('slow');
//         }
//         else{
//             $('.navbar .navbar-nav li .sub-menu').addClass('active').show('slow');
//         }
//     })
// }

//jwplayer for audio
    // var playerInstance = jwplayer("ans_audio");
    // playerInstance.setup({
    //     file: "",
    //     width:530,
    //     height:10,
    //     skin: {
    //         active: "#bb3335",
    //         inactive: "#bb3335",
    //         background: "white"
    //     }
    // });

//slider for top video answer    
var owl = $('.owl-carousel');
  owl.owlCarousel({
    loop:false,
    margin:10,
    nav:true,
    dots:true,
    items:1,
    video:true,
    lazyLoad:true,
    center:false,
    navText: [
        "<i class='fa fa-chevron-left'></i>",
        "<i class='fa fa-chevron-right'></i>"
     ],
    // responsive:{
    //     480:{
    //         items:1
    //     },
    //     600:{
    //         items:1
    //     }
    // }
  })
  owl.on('translate.owl.carousel',function(e){
    $('.owl-item video').each(function(){
      console.log('11')
      $(this).get(0).pause();
      $('.qa_sec .owl-item .item img').css('z-index','0')
    });
  });
  owl.on('translated.owl.carousel',function(e){
    $('.owl-item.active video').get(0).play();
    $('.qa_sec .owl-item .item img').css('z-index','-1')
  })
  // if(!isMobile()){
    $('.owl-item .item').each(function(){
      var attr = $(this).attr('data-videosrc');
      if (typeof attr !== typeof undefined && attr !== false) {
        console.log('hit');
        var videosrc = $(this).attr('data-videosrc');
        $(this).prepend('<video controls muted><source src="'+videosrc+'" type="video/mp4"></video>');
      }
      
    });
    $('.owl-item.active video').attr('autoplay',false).attr('loop',true);
  // }



function isMobile(width) {
	if(width == undefined){
		width = 719;
	}
	if(window.innerWidth <= width) {
		return true;
	} else {
		return false;
	}
}