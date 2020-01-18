var userLikeAndUnlike=[];
function loaderBoloShowDynamicDe(classLoader){
    var boloLoader='<img src="/media/loader.gif">';
        $('.'+classLoader).html(boloLoader);

}

function loaderBoloHideDynamicDe(classLoader){
    var boloLoader='';
    $('.'+classLoader).html(boloLoader);
    
}

jQuery(document).ready(function(){
    listCommentsById();
    getElementsByPage(1);
});

function getElementsByPage(currentPage){
    loaderBoloShowDynamicDe('_scroll_load_more_loading_user_videos');
    var playListData=[]; 
    var platlistItems;
    var listItems="";
    var itemCount=0;


    var uri='/api/v1/get_popular_video_bytes/?page='+currentPage;
    var res = encodeURI(uri);
    $.get(res, function (data, textStatus, jqXHR) {
        var topicVideoList=data.topics;
        playListData=topicVideoList;
        var itemCount=-1;
        topicVideoList.forEach(function(itemVideo) {itemCount++;
          var isPlaying="";
          var isPlayIconDis="none";
          if(itemCount==1){
                isPlaying='is-playing';
                isPlayIconDis="block";
            }
          var content_title="";
          var videoTitle="";
              videoTitle=itemVideo.title;
              content_title = videoTitle.substr(0, 40) + " ..."
            listItems += '<li><a href="/'+itemVideo.user.username+'/'+itemVideo.id+'" ><div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="jsx-3077367275 video-card default"><div class="jsx-3077367275 video-card-mask"><div class="jsx-1633345700 card-footer small"><div class="jsx-1633345700"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideo.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></div></div></div></a></li>';

        });

        $("#playlist").append(listItems);
        loaderBoloHideDynamicDe('_scroll_load_more_loading_user_videos');

    });

}



// function video_play_using_video_js1(file,image){
//   loaderShow();
//   var video = document.getElementById('playerDetails');

//   var hls = new Hls();
//   if(Hls.isSupported()) {
    
//     hls.loadSource(file);
//     hls.attachMedia(video);
//     hls.on(Hls.Events.MANIFEST_PARSED,function() {
//       video.play();
//       loaderHide();
//   });
//  }
//   else if (video.canPlayType('application/vnd.apple.mpegurl')) {
//     video.src = file;
//     video.addEventListener('loadedmetadata',function() {
//       video.play();
//       loaderHide();
//     });
//   }

//   hls.on(Hls.Events.ERROR, function (event, data) {

//       if (data.fatal) {
//         switch(data.type) {
//         case Hls.ErrorTypes.NETWORK_ERROR:
//           console.log("fatal network error encountered, try to recover");
//           if (!retrying) {
//               retry;
//           }
//           break;
//         case Hls.ErrorTypes.MEDIA_ERROR:
//           console.log("fatal media error encountered, try to recover");
//           hls.recoverMediaError();
//           break;
//         }
//       }
//   });

// }
var isLoading = false;
var hideErrorMsg = true;
var video = document.getElementById('playerDetails');
var retryCount=0;

const config = {
    autoStartLoad: true,
    maxBufferSize: 1 * 1000 * 1000,
    manifestLoadingMaxRetry: 300000,
    manifestLoadingMaxRetryTimeout: 1000,
    levelLoadingMaxRetry: 300000,
    levelLoadingMaxRetryTimeout: 1000,
    fragLoadingMaxRetry: 300000,
    fragLoadingMaxRetryTimeout: 1000
}
var muteStatus=false;

var hls = new Hls(config);

function video_play_using_video_js(url,backup_url,image) {
    if(Hls.isSupported()) {
        let retrying = false;
        
        video.onplaying = () => {
            isLoading = false;
            hideErrorMsg = false;
            //clearInterval(retry);
            retrying = false;

        }
        
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
            video.play();
        });
    
        hls.on(Hls.Events.ERROR, function (event, data) {
            if (!hideErrorMsg) {
                isLoading = true;
                hideErrorMsg = true;
            }
            if (data.fatal) {
              switch(data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
              
                console.log("fatal network error encountered, try to recover");
                if (!retrying) {
                    if(retryCount<2){
                      retryLiveStream(hls,url);
                    }
                    
                }
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                console.log("fatal media error encountered, try to recover");
                hls.recoverMediaError();
                break;
              }
            }
        });
    }else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = file;
    video.addEventListener('loadedmetadata',function() {
      video.play();
      loaderHide();
    });
  }
  checkPlayStatus(video);
}

function retryLiveStream(hls, url) {
    retrying = true;
    retryCount++;
    hls.loadSource(url);
    hls.startLoad();
}

function checkPlayStatus(video){
  if(video.paused) {
    var newSrc='/media/mute_icon.svg';
    $('#mutedImageId').attr('src', newSrc);
    $('.videoPlayButtonDetails').removeClass('play-button');
    //video.play();
  } else {
    //video.pause();
    $('.videoPlayButtonDetails').removeClass('play-button');
    $('.videoPlayButtonDetails').addClass('play-button');
  }
}


$(".event-delegate-maskDesk").click(function(){

  if(video.paused) {
    var newSrc='/media/mute_icon.svg';
    $('#mutedImageId').attr('src', newSrc);
    $('.videoPlayButtonDetails').removeClass('play-button');
    video.play();
  } else {
    video.pause();
    $('.videoPlayButtonDetails').removeClass('play-button');
    $('.videoPlayButtonDetails').addClass('play-button');
  }
  
});


$(".event-delegate-maskMob").click(function(){
var video = document.getElementById('playerDetailsMobile');

  if(video.paused) {
    $('.videoPlayButtonDetails').removeClass('play-button');
    video.play();
  } else {
    video.pause();
    $('.videoPlayButtonDetails').removeClass('play-button');
    $('.videoPlayButtonDetails').addClass('play-button');
  }

  
});



muteStatus=$("video").prop('muted', false);

function muteAndUnmutePlayerDet(muteDetails){
  if(muteDetails=='playerDetailsMobile'){

  if($("video").prop('muted')){

      $("video").prop('muted', false);
      var newSrc='/media/mute_icon.svg';
      $('#mutedImageIdDe').attr('src', newSrc);
    }else{
        $("video").prop('muted', true);
        var newSrc='/media/sound_mute.svg';
        $('#mutedImageIdDe').attr('src', newSrc);
    }
  var video = document.getElementById('playerDetailsMobile');  
  if(video.paused) {
    $('.videoPlayButtonDetails').removeClass('play-button');
    video.play();
  }

    
  }else{
  if($("video").prop('muted')){

      $("video").prop('muted', false);
      var newSrc='/media/mute_icon.svg';
      $('#mutedImageIdDeDesk').attr('src', newSrc);
    }else{
        $("video").prop('muted', true);
        var newSrc='/media/sound_mute.svg';
        $('#mutedImageIdDeDesk').attr('src', newSrc);
    }
  }
  checkPlayStatus(video);

}


function VideoPlayByURL(file,image){
  loaderShow();
  var playerInstanceDe = jwplayer("playerDetails");
  jwplayer('playerDetails').setMute(false);
  var newSrc='/media/mute_icon.svg';
  $('#mutedImageId').attr('src', newSrc);
  $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');

      var preBufferDone = false;
      
        playerInstanceDe.setup({
          file: file,
          controls: false,
          repeat:'true',
          image:image,
          preload:'metadata',
          autostart:'viewable',
          primary: "html5",
          mute:'false'
      });
      playerInstanceDe.on('playerDetails', function() {
            loaderHide();
            preBufferDone = true;
          
      }); 

    playerInstanceDe.on('buffer', function() {
        console.log(playerInstanceDe);
      var time = 1;

    });   


    playerInstanceDe.on('error', function(event) {
        loaderHide();
        var erroCode=event.code;
        console.log(erroCode);
        playerInstanceDe.setup({
          file:videoFileBackupURL,
          controls: false,
          repeat:true,
          image:image,
          preload: 'metadata',
          autostart:'viewable',
          primary: "html5",
          mute:'false'
        });        

    });

    playerInstanceDe.on('complete', function() {
        //jwplayer('playerDetails').setMute(true);
        //playerInstanceDe.remove();
        //playerInstanceDe = null;
    });


}

$(".event-delegate-maskDesk1").click(function(){
  var plaerState=jwplayer('playerDetails').getState();

  if( jwplayer('playerDetails').getState() == "playing" || jwplayer('playerDetails').getState() == "buffering" ) {
          jwplayer('playerDetails').pause();
          $('.videoPlayButtonDetails').removeClass('play-button');
          $('.videoPlayButtonDetails').addClass('play-button');
          
      }else{
        var newSrc='/media/mute_icon.svg';
        $('#mutedImageId').attr('src', newSrc);
        jwplayer('playerDetails').play(true);
        jwplayer('playerDetails').setMute(false);
        $('.videoPlayButtonDetails').removeClass('play-button');
      }
  
});


function video_play_using_video_js_mobile(url,backup_url,image) {
    
    var video = document.getElementById('playerDetailsMobile');

      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
          loaderHide();
          var playPromise = video.play();

          if (playPromise !== undefined) {
            playPromise.then(_ => {
              // Automatic playback started!
              // Show playing UI.
              console.log('Video Eror');
            })
            .catch(error => {
                console.log('Video Eror1');
              // Auto-play was prevented
              // Show paused UI.
            });
          }

      });
     }


     // hls.js is not supported on platforms that do not have Media Source Extensions (MSE) enabled.
     // When the browser has built-in HLS support (check using `canPlayType`), we can provide an HLS manifest (i.e. .m3u8 URL) directly to the video element through the `src` property.
     // This is using the built-in support of the plain video element, without using hls.js.
     // Note: it would be more normal to wait on the 'canplay' event below however on Safari (where you are most likely to find built-in HLS support) the video.src URL must be on the user-driven
     // white-list before a 'canplay' event will be emitted; the last video event that can be reliably listened-for when the URL is not on the white-list is 'loadedmetadata'.
      else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = backup_url;
        video.addEventListener('loadedmetadata',function() {
          video.play();
          loaderHide();
        });
      }
}


function VideoPlayByURLMobile(file,image){
  loaderShow();
  // var playerInstanceDe = jwplayer("playerDetailsMobile");
  // jwplayer('playerDetailsMobile').setMute(false);
  var newSrc='/media/mute_icon.svg';
  $('#mutedImageIdDe').attr('src', newSrc);


    $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
    var preBufferDone = false;
    video_play_using_video_js_mobile(file,file,image);
    $('.videoPlayButtonDetails').removeClass('play-button');
      
    //   playerInstanceDe.setup({
    //     file: file,
    //     controls: false,
    //     repeat:true,
    //     //image:image,
    //     preload: 'metadata',
    //     autostart:'true',
    //     primary: "html5",
    //     mute:'false'
    //   });
    //   playerInstanceDe.on('playerDetailsMobile', function() {
    //         loaderHide();
    //         preBufferDone = true;
          
    //   }); 

    // playerInstanceDe.on('buffer', function() {
    //     console.log(playerInstanceDe);
    //     var time = 1;

    // });   


    //  playerInstanceDe.on('error', function(event) {
    //     loaderHide();
    //     var erroCode=event.code;
    //     console.log(erroCode);
    //     playerInstanceDe.setup({
    //       file:videoFileBackupURL,
    //       controls: false,
    //       repeat:true,
    //       //image:image,
    //       preload: 'metadata',
    //       autostart:'true',
    //       primary: "html5",
    //       mute:'false'
    //     });

    // });

    // playerInstanceDe.on('complete', function() {
    // jwplayer('playerDetailsMobile').setMute(true);

    //   playerInstanceDe.remove();
    //   playerInstanceDe = null;
    // });


 }

//  $(".event-delegate-maskMob").click(function(){
//   var plaerState=jwplayer('playerDetailsMobile').getState();

//   if( jwplayer('playerDetailsMobile').getState() == "playing" || jwplayer('playerDetailsMobile').getState() == "buffering" ) {
//           jwplayer('playerDetailsMobile').pause();
//           $('.videoPlayButtonDetails').removeClass('play-button');
//           $('.videoPlayButtonDetails').addClass('play-button');
          
//       }else{
//         var newSrc='/media/mute_icon.svg';
//         $('#mutedImageId').attr('src', newSrc);
//         jwplayer('playerDetailsMobile').play(true);
//         jwplayer('playerDetailsMobile').setMute(false);
//         $('.videoPlayButtonDetails').removeClass('play-button');
//       }
  
// });

// $('.videoPlayButtonDetails').click(function(){
//       var newSrc='/media/mute_icon.svg';
//       $('#mutedImageIdDe').attr('src', newSrc);
//       $('.videoPlayButtonDetails').removeClass('play-button');
//       jwplayer('playerDetails').setMute(false);
//       jwplayer('playerDetails').play(true);
// });




// function muteAndUnmutePlayerDet(playerDetailsMobile){
//   var muteStatus=jwplayer(playerDetailsMobile).getMute();
//   if(muteStatus==true){
//         var newSrc='/media/sound_mute.svg';
//         $('#mutedImageIdDe').attr('src', newSrc);
//     }else{
//         var newSrc='/media/mute_icon.svg';
//         $('#mutedImageIdDe').attr('src', newSrc);
//     }

// }

jQuery('#UCommentLink').on('click',function(){
    var commentBoxInputStatus=jQuery('#commentInputId').hasClass('hide');
    if(commentBoxInputStatus==true){
       var loginStatus= check_login_status();
       if(loginStatus==false){
        if( jwplayer('playerDetails').getState() == "playing"){
            jwplayer('playerDetails').pause();
        } 
        if(!video.paused) {
          video.pause();
          $('.videoPlayButtonDetails').removeClass('play-button');
          $('.videoPlayButtonDetails').addClass('play-button');
        }
        // if( jwplayer('playerDetails').getState() == "playing"){
        //     jwplayer('playerDetails').pause();
        // }
        
        document.getElementById('openLoginPopup').click();
            //jQuery("#openLoginPopup").click();
       }else{
            jQuery('#commentInputId').removeClass('hide');
       }

        
    }else{
       jQuery('#commentInputId').addClass('hide'); 
    }
    
});

jQuery('#shareLinkId').on('click',function(){
    var shareListId='shareListId';
   // scrollDownOrUp(shareListId);
});

function downloadAppLink(){
    var appLink='https://play.google.com/store/apps/details?id=com.boloindya.boloindya&hl=en_IN';
    window.open(appLink, '_blank');
}

$('.sbutton').on('click', function(event) {
  event.preventDefault();
  
  $('.smenu').toggleClass('share');
});

function openShareTab(){
   jQuery('.openShareTabId').toggleClass('hide',8000);

} 
jQuery('.hideShareOnMobile').click(function(){
    jQuery('.openShareTabId').toggleClass('hide');
 
});

function scrollDownOrUp(id){

    $('._video_card_big_comments').animate({
        scrollTop: $("#"+id).offset().top-100
    }, 1000);

}
jQuery('#UReactionLink').on('click',function(){
    var likeStatus=jQuery('#UReactionLink').hasClass('liked');
    if(likeStatus==false){
       var loginStatus= check_login_status();
       if(loginStatus==false){
        if( jwplayer('playerDetails').getState() == "playing"){
            jwplayer('playerDetails').pause();
        }

        document.getElementById('openLoginPopup').click();
            //jQuery("#openLoginPopup").click();
       }
       var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25c');
       if(likeStatus==true){
            jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25c');
            jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25d');
       }

        jQuery('#UReactionLink').addClass('liked');
        updateUserLikeStatus();
    }else{
       jQuery('#UReactionLink').removeClass('hide');
       updateUserLikeStatus();
       var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25d');
       if(likeStatus==true){
            jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25d');
            jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25c');
            jQuery('#UReactionLink').removeClass('liked');
       }

    }
    
});

function social_share(shareType){

    var loginStatus=check_login_status();
    if(loginStatus==false){
        document.getElementById('openLoginPopup').click();
        //return false;
    }

    var topicId=$("#topicID").val();
    var topicCreatorUsername=$("#topicCreatorUsername").val();
    var shareURL="";
    if(shareType=='facebook_share'){

        shareURL='https://www.facebook.com/sharer/sharer.php?app_id=113869198637480&u='+site_base_url+topicCreatorUsername+'/'+topicId+'&display=popup&sdk=joey/';

    }else if(shareType=='twitter_share'){

        shareURL='https://twitter.com/intent/tweet?text='+site_base_url+topicCreatorUsername+'/'+topicId+'/&url='+site_base_url+topicCreatorUsername+'/'+topicId+'/'
    }else if(shareType=='whatsapp_share'){
        shareURL='https://api.whatsapp.com/send?text='+site_base_url+topicCreatorUsername+'/'+topicId+'/';
    }
    

    var ge_local_data="";
        ge_local_data = JSON.parse(localStorage.getItem("access_data"));
    var accessToken=ge_local_data.access_token;

    jQuery.ajax({
        url:'/api/v1/shareontimeline/',
        type:"POST",
        headers: {
          'Authorization':'Bearer '+accessToken,
        },
        data:{topic_id:topicId,share_on:shareType},
        success: function(response,textStatus, xhr){
            window.open(shareURL, '_blank');
            $('.smenu').toggleClass('share');

        },
        error: function(jqXHR, textStatus, errorThrown){
          //$("form#optForm")[0].reset();
          jQuery(".commentErrorStatus").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
          console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        }


    });
} 

$(document).ready(function() {
  var default_color = $(".chars-counter").css("color");

  $("#comment-input").on('keydown keyup', function() {
    var comment_len = $(this).val().length;
    
    $("#chars-current").html(comment_len);
    
    if(comment_len == 60)
      $(".chars-counter").css("color", "red");
    
    if(comment_len < 60 && $('.chars-counter').css("color") != default_color)
      $(".chars-counter").css("color", default_color);
  });
  
});

$('#comment-input').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
  {

    var commentdata=$('#comment-input').val();
    if(commentdata.length>1){
    create_comment(commentdata);
    }else{
        $('.commentError').html('<span style="color:red">Opps! Comment is missing</span>');
        return false;
    }

  }
});

function create_comment(inputComment){

    var loginStatus=check_login_status();
    if(loginStatus==false){
        document.getElementById('openLoginPopup').click();
        //return false;
    }
    var ge_local_data="";
    ge_local_data = JSON.parse(localStorage.getItem("access_data"));
    var user_details=ge_local_data.user.userprofile;
    //topic_id = request.POST.get('topic_id’, ‘’)
    var language_id = user_details.language;
    var comment_html = inputComment;
    var mobile_no = user_details.mobile_no;
    var thumbnail = user_details.profile_pic;
    if(thumbnail==""){
        thumbnail='/media/demo_user.png';
    }

    var topicID = document.getElementById('singleTopicId').value;
    var elem = document.getElementById('some_div');
    var data=[];
    data.push({name: 'topic_id', value: topicID});
    data.push({name: 'language_id', value: language_id});
    data.push({name: 'comment', value: comment_html});
    data.push({name: 'mobile_no', value: mobile_no});
    data.push({name: 'thumbnail', value: thumbnail});
    data.push({name: 'media_duration', value: '90'});
    var accessToken=ge_local_data.access_token;

    console.log(data);
     //return false;

      
    jQuery.ajax({
        url:'/api/v1/reply_on_topic',
        type:"POST",
        headers: {
          'Authorization':'Bearer '+accessToken,
        },
        data:data,
        success: function(response,textStatus, xhr){
            console.log(response);
            current_comment(response.comment);
            var commentdata=$('#comment-input').val();
            jQuery('#commentInputId').addClass('hide');
            jQuery(".commentErrorStatus").html('<span style="color:green;float:right;text-align:right">'+response.message+'</span>').fadeOut(8000);


        },
        error: function(jqXHR, textStatus, errorThrown){
          //$("form#optForm")[0].reset();
          jQuery(".commentErrorStatus").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
          console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        }


    });
}

function current_comment(videoCommentList){
    var itemCount=1;
    var profileImage="";
    var listCommentItems="";
    var itemVideo=videoCommentList;
    var userProfile=itemVideo.user.userprofile;
    if(userProfile.profile_pic==""){
       profileImage='/media/demo_user.png';
    }else{
        profileImage=userProfile.profile_pic;
    }

    listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'?langCountry=en">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/?langCountry=en"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+'"><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" id="commentLikeReaction" href="javascript:void();" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

    $("#currentCommentId").append(listCommentItems);
}

function likeAndUnlikeComment(commentId){
    var ge_local_data="";
        ge_local_data = JSON.parse(localStorage.getItem("access_data"));
    var accessToken=ge_local_data.access_token;
    var listCommentItems="";
    //================Comments List =================
    var uri='/api/v1/like/';
    var res = encodeURI(uri);
    jQuery.ajax({
        url:res,
        type:"POST",
        headers: {
          'Authorization':'Bearer '+accessToken,
        },
        data:{comment_id:commentId},
        success: function(response,textStatus, xhr){
            if(response.message=='liked'){
                jQuery('.changeLikeColor-'+commentId).removeClass('liked');
                jQuery('.likedStatus-'+commentId).removeClass('hide');
                jQuery('.changeLikeColor-'+commentId).addClass('liked');


            }else if(response.message=='unliked'){
                jQuery('.changeLikeColor-'+commentId).removeClass('liked');
                jQuery('.likedStatus-'+commentId).removeClass('hide');
                jQuery('.likedStatus-'+commentId).addClass('hide');
            }
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        }

  
    });
} 

  function updateUserLikeStatus(){
    return false;
  }  


function listCommentsById(){
    loaderBoloShowDynamicDe('_scroll_load_more_loading_comment');
    
    var topicId=jQuery("#singleTopicId").val();
    var topicSlug=jQuery("#singleTopicSlug").val();

    var listCommentItems="";
    $(".videoCommentId").html("");
    //================Comments List =================
    var uri='/api/v1/topics/'+topicSlug+'/'+topicId+'/comments?limit=5&offset=1';
    var res = encodeURI(uri);
    $.get(res, function (data, textStatus, jqXHR) {
        var videoCommentList=data.results;

        var itemCount=0;
        videoCommentList.forEach(function(itemVideo) {itemCount++;
        var profileImage="";
        var userProfile=itemVideo.user.userprofile;
        if(userProfile.profile_pic==""){
           profileImage='/media/demo_user.png';
        }else{
            profileImage=userProfile.profile_pic;
        }

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'?langCountry=en">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/?langCountry=en"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
        });
        $(".videoCommentId").append(listCommentItems);
        var loadMoreComment='<span class="loadMoreComment"><a onclick="loadMoreComments(\''+data.next+'\');" class="" href="javascript:void(0);">Load More Comments...</a></span';
        $(".loadMoreComments").html(loadMoreComment);
         loaderBoloHideDynamicDe('_scroll_load_more_loading_comment');
        //console.log(listItems);


    });
}

function loadMoreComments(nextPageURl){

    var listCommentItems="";
    //================Comments List =================
    var uri=nextPageURl;
    var res = encodeURI(uri);
    $.get(res, function (data, textStatus, jqXHR) {
        var videoCommentList=data.results;

        var itemCount=0;
        videoCommentList.forEach(function(itemVideo) {itemCount++;
        var profileImage="";
        var userProfile=itemVideo.user.userprofile;
        if(userProfile.profile_pic==""){
           profileImage='/media/demo_user.png';
        }else{
            profileImage=userProfile.profile_pic;
        }

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'?langCountry=en">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/?langCountry=en"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
        });
        $(".videoCommentId").append(listCommentItems);
        var loadMoreComment='<span class="loadMoreComment"><a class="" onclick="loadMoreComments(\''+data.next+'\');" href="javascript:void(0);">Load More Comments...</a></span';
        $(".loadMoreComments").html(loadMoreComment);
        loaderBoloHide();
    });
}

function followLikeList(){

    var ge_local_data="";
    ge_local_data = JSON.parse(localStorage.getItem("access_data"));
  if(ge_local_data){
    var accessToken=ge_local_data.access_token;

    var listCommentItems="";

    //================Comments List =================
    var uri='/api/v1/follow_like_list/';
    var res = encodeURI(uri);
    jQuery.ajax({
        url:res,
        type:"POST",
        headers: {
          'Authorization':'Bearer '+accessToken,
        },
        success: function(response,textStatus, xhr){
            userLikeAndUnlike=response;

            var countFollowStatus=userLikeAndUnlike.all_follow;
            if(undefined !==countFollowStatus && countFollowStatus.length>0){
                var followList=userLikeAndUnlike.all_follow;
                followList.forEach(function(followId){
                    followStatus=jQuery('.followCheck').hasClass('followStatusChange-'+followId);
                    if(followStatus==true){
                        jQuery('.followStatusChange-'+followId).removeClass('sx_5da455');
                        jQuery('.followStatusChange-'+followId).addClass('sx_5da456');
                        jQuery('.btnTextChange-'+followId).text(followed_trans);
                    }

                });
            }
            
        //var videoCommentList=data.results;
        }
  
    });
  }

}

jQuery(document).ready(function(){
    followLikeList();
});

//====================Mention and hashtag===================

    $(function () {

      var searchURI="";
      var hashTagSearch="";
      $('#comment-input').keydown(function(e){
        console.log('keyCode:'+e.keyCode);
        if (e.keyCode == 51) {
          searchURI="/api/v1/mention_suggestion/";
          hashTagSearch="";
        }else if(e.keyCode == 50){
          hashTagSearch=50;
          searchURI="/api/v1/hashtag_suggestion/";
        }
      });

      $('textarea.mention').mentionsInput({
        onDataRequest:function (mode, query, callback) {
            console.log(query);
            var uri='/api/v1/mention_suggestion/';
            var res = encodeURI(uri);
            var valIn=document.getElementById("comment-input").value;
            var s2 = valIn.substr(1);

            var ge_local_data="";
              ge_local_data = JSON.parse(localStorage.getItem("access_data"));
            var accessToken=ge_local_data.access_token;

            $.ajax({
                  url:res,
                  data:{'term':query},
                  type:"POST",
                  headers: {
                    'Authorization':'Bearer '+accessToken,
                  },

                success: function (response) {

                    if(hashTagSearch==50){
                      var responseData = response.hash_data;
                      capitals = responseData.map(function(obj) { 
                          obj['name'] = obj.hash_tag; // Assign new key  
                          return obj; 
                      });
                      responseData = _.filter(responseData, function(item) { return item.hash_tag.toLowerCase().indexOf(query.toLowerCase()) > -1 });
                    
                    }else{
                      var responseData = response.mention_users;
                      responseData = _.filter(responseData, function(item) { return item.name.toLowerCase().indexOf(query.toLowerCase()) > -1 });
                    
                    }
                    callback.call(this, responseData);

                }
            });


        }

      });


      $('.get-syntax-text').click(function() {
        $('textarea.mention').mentionsInput('val', function(text) {
          alert(text);
        });
      });

      $('.get-mentions').click(function() {
        $('textarea.mention').mentionsInput('getMentions', function(data) {
          alert(JSON.stringify(data));
        });
      }) ;

    });

function removeDataFromURL(){
  video.src="";
  return true;
}

//=====================End mentions=========================

