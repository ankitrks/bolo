    var page = 1;
    var checkDataStatus=0;
    var userLikeAndUnlike=[];
    var totalCountVideo =0;
    var playListData=[];
    var category_id= $("#currentCatId").val();
    $(window).scroll(function() {
        var scorh=Number($(window).scrollTop() + $(window).height());
        if($(window).scrollTop() + $(window).height() > $("#playlist").height()){

            if(checkDataStatus==0){
                page++;
                loadMoreData(page);
            }

        }
    });

    function loadMoreData(page){
     loaderBoloShow();
    var platlistItems;
    checkDataStatus=1;

    var listItems="";
    var itemCount=0;
    var language_id=current_language_id;
    //var uri='https://www.boloindya.com/api/v1/get_popular_video_bytes/?page=1';
    var uri='/api/v1/get_category_video_bytes/';
    var res = encodeURI(uri);
      $.ajax(
            {
                url:res,
                type: "POST",
                data:{'category_id':category_id,'language_id':language_id,'page':1},
                beforeSend: function()
                {
                    $('.ajax-load').show();
                }
            })
            .done(function(data)
            {
                if(data == " "){
                    $('.ajax-load').html("");
                    return;
                }
                checkDataStatus=0;
           var topicVideoList=data.topics;
            //playListData+=topicVideoList;
            var itemCount=-1;
            topicVideoList.forEach(function(itemVideo) {itemCount++;totalCountVideo++;
              loaderBoloHide();
                //playListData+=itemVideo;
                playListData.push(itemVideo);
              var isPlaying="";
              var isPlayIconDis="none";
              if(itemCount==1){
                isPlaying='is-playing';
                isPlayIconDis="block";
              }
            var profilePics = itemVideo.user.userprofile.profile_pic;
            if(profilePics==''){
                profilePics= '/media/ic_profile_red_1.svg';
                //profilePics= '/media/user.svg';
            }

            var content_title="";
            var videoTitle="";

                videoTitle=removeTags(itemVideo.title);
                content_title = videoTitle.substr(0, 40) + " ...";
                if(itemVideo!=""){
                  //listItems +='<div class="_video_feed_item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+totalCountVideo+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideo.likes_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>';
                      listItems +='<div class="feedlist-item">\
                                      <header class="user-info"><img src="'+profilePics+'" class="avatar" alt="Khushi Kumari">\
                                          <div>\
                                              <div class="name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.userprofile.name+'</a></div>\
                                              <div class="description"></div>\
                                          </div>\
                                      </header>\
                                      <div class="title">'+itemVideo.title+'</div>\
                                      <div style="text-align: center;" class="jsx-3077367275 video-card">\
                                          <div style=" position: relative; background-color: rgb(0, 0, 0);object-fit: cover;">\
                                          <video id="player-'+itemVideo.id+'" controls preload="auto"  poster="'+itemVideo.question_image+'" class="videoCentered videoSliderPlay" preload="metadata"  width="212" height="160">\
                                        </video>\
                                          <div class="jsx-3077367275 video-card-mask"></div>\
                                          <div class="jsx-4030482358 theme playButtonStatus videoPlayButtonDetails-'+itemVideo.id+' play-button"></div>\
                                          <span class="jsx-3077367275 event-delegate-mask event-delegate-maskDesk" onclick="delegateClick('+itemVideo.id+',\''+itemVideo.backup_url+'\',\''+itemVideo.video_cdn+'\')"></span>\
                                          </div>\
                                          <img onclick="muteAndUnmutePlayerFeed('+itemVideo.id+');" class="jsx-3077367275 mute-icon '+itemVideo.id+'" id="mutedImageIdDeDesk" src="/media/mute_icon.svg">\
                                      </div>\
                                      <div class="statistics-info"><span class="digg">'+itemVideo.view_count+'</span><span class="comment">'+itemVideo.likes_count+'</span>\
                                      <hr style="margin-bottom: 10px;">\
                                      <div class="_6w18">\
                                          <div class="_6w1h">\
                                              <span class="_18vi">\
                                      <div class="_666k" data-testid="UFI2ReactionLink/actionLink">\
                                      <div class="_8c74">\
                                      <a aria-pressed="false" class=" _6a-y _3l2t  _18vj '+itemVideo.id+'" data-testid="UReactionLink-'+itemVideo.id+'" href="javascript:void(0)" id="UReactionLink-'+itemVideo.id+'" onclick="likeUnlikeFeed('+itemVideo.id+');" role="button" tabindex="0">\
                                      <i alt="" class="_6rk2 img sp_ddXiTdIB8vm sx_44a25c '+itemVideo.id+'"></i>'+likeTrans+'</a>\
                                      </div>\
                                      </div>\
                                      </span>\
                                      <span class="_18vi">\
                                      <a class=" _666h  _18vj _18vk _42ft " role="button" tabindex="0" testid="UFI2CommentLink" title="Leave a comment" id="UCommentLink" href="/explore/'+itemVideo.slug+'/'+itemVideo.id+'">'+commentTrans+'</a>\
                                      </span>\
                                      <span class="_18vi sbutton">\
                                      <span class="_1j6m">\
                                      <a class=" _2nj7  _18vj _18vk " href="javascript:void(0)" id="shareLinkId" role="button" tabindex="0" title="Send this to friends or post it on your Timeline." onclick="openShareTab()">'+shresTrans+'</a>\
                                      </span>\
                                              </span>\
                                          </div>\
                                      </div>\
                                      </div>\
                                  </div>';              

                }
            });

                $('.ajax-load').hide();
                //$("#playlist").append(listItems);
                $(".feedlist-container").append(listItems);
            })
            .fail(function(jqXHR, ajaxOptions, thrownError)
            {
                if(jqXHR.status!=201){

                }

                $('.ajax-load').html("");
            });
    }

$(window).scroll(function () {
    // End of the document reached?
    //console.log($(document).height() - $(this).height()-600);
    if ($(document).height() - $(this).height()-600 == $(this).scrollTop()) {
        //getElementsByPage(page);
        //console.log('ad');
       // console.log($(this).scrollTop());
    }
    //console.log('scroll'+$(this).scrollTop())
}); 
function loaderBoloShow(){
    var boloLoader='<div id="loading-bar-spinner" class="spinner"><div class="spinner-icon"></div></div>';
        $('._scroll_load_more_loading').html(boloLoader);

}

function loaderBoloHide(){
    var boloLoader='';
    $('._scroll_load_more_loading').html(boloLoader);
    
}

    var language_id=current_language_id;
    // var playListData=[]; 
    loaderBoloShow();
    var platlistItems;
    (function() {
        var listItems="";
        var itemCount=0;

        var uri='/api/v1/get_category_video_bytes/';
        var res = encodeURI(uri);
        jQuery.ajax({
            url:res,
            data:{'category_id':category_id,'language_id':language_id,'page':1},
            type:"POST",
            success: function(response,textStatus, xhr){
              loaderBoloHide();
                var topicVideoList=response.topics;
                //playListData=topicVideoList;
                var itemCount=-1;
                topicVideoList.forEach(function(itemVideo) {itemCount++;totalCountVideo++;
                playListData.push(itemVideo);
                //playListData+=itemVideo;
                  var isPlaying="";
                  var isPlayIconDis="none";
                  if(itemCount==1){
                    isPlaying='is-playing';
                    isPlayIconDis="block";
                  }

                var profilePics = itemVideo.user.userprofile.profile_pic;
                if(profilePics==''){
                    //profilePics= '/media/user.svg';
                    profilePics= '/media/ic_profile_red_1.svg';
                }
                var content_title="";
                var videoTitle="";
                    videoTitle=removeTags(itemVideo.title);
                    content_title = videoTitle.substr(0, 40) + " ...";
                    //<span class="_avatar_ _avatar_respond" style="background-image: url('+profilePics+');"></span>
                  //listItems +='<div class="_video_feed_item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+totalCountVideo+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideo.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>'; 
//                                          <img src="'+itemVideo.question_image+'" class="image-list-item" alt="" style="width: auto;height:400px">\
                  //<span class="_video_card_"></span>\
                  //onClick="openVideoInPopup(\''+itemVideo.backup_url+'\',\''+itemVideo.question_image+'\','+itemCount+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"
                  
                      listItems +='<div class="feedlist-item">\
                                      <header class="user-info"><img src="'+profilePics+'" class="avatar" alt="Khushi Kumari">\
                                          <div>\
                                              <div class="name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.userprofile.name+'</a></div>\
                                              <div class="description"></div>\
                                          </div>\
                                      </header>\
                                      <div class="title">'+itemVideo.title+'</div>\
                                      <div style="text-align: center;" class="jsx-3077367275 video-card">\
                                          <div style=" position: relative; background-color: rgb(0, 0, 0);object-fit: cover;">\
                                          <video id="player-'+itemVideo.id+'" controls  preload="auto"  poster="'+itemVideo.question_image+'" class="videoCentered videoSliderPlay" preload="metadata"  width="212" height="160">\
                                        </video>\
                                          <div class="jsx-3077367275 video-card-mask"></div>\
                                          <div class="jsx-4030482358 theme playButtonStatus videoPlayButtonDetails-'+itemVideo.id+'"></div>\
                                          <span class="jsx-3077367275 event-delegate-mask event-delegate-maskDesk" onclick="delegateClick('+itemVideo.id+',\''+itemVideo.backup_url+'\',\''+itemVideo.video_cdn+'\')"></span>\
                                          </div>\
                                          <img onclick="muteAndUnmutePlayerFeed('+itemVideo.id+');" class="jsx-3077367275 mute-icon '+itemVideo.id+'" id="mutedImageIdDeDesk" src="/media/mute_icon.svg">\
                                      </div>\
                                      <div class="statistics-info"><span class="digg">'+itemVideo.view_count+'</span><span class="comment">'+itemVideo.likes_count+'</span>\
                                      <hr style="margin-bottom: 10px;">\
                                      <div class="_6w18">\
                                          <div class="_6w1h">\
                                              <span class="_18vi">\
                                      <div class="_666k" data-testid="UFI2ReactionLink/actionLink">\
                                      <div class="_8c74">\
                                      <a aria-pressed="false" class=" _6a-y _3l2t  _18vj '+itemVideo.id+'" data-testid="UReactionLink-'+itemVideo.id+'" href="javascript:void(0)" id="UReactionLink-'+itemVideo.id+'" onclick="likeUnlikeFeed('+itemVideo.id+');" role="button" tabindex="0">\
                                      <i alt="" class="_6rk2 img sp_ddXiTdIB8vm sx_44a25c '+itemVideo.id+'"></i>'+likeTrans+'</a>\
                                      </div>\
                                      </div>\
                                      </span>\
                                      <span class="_18vi">\
                                      <a class=" _666h  _18vj _18vk _42ft" role="button" tabindex="0" testid="UFI2CommentLink" title="Leave a comment" id="UCommentLink" href="/explore/'+itemVideo.slug+'/'+itemVideo.id+'">'+commentTrans+'</a>\
                                      </span>\
                                      <span class="_18vi sbutton">\
                                      <span class="_1j6m">\
                                      <a class=" _2nj7  _18vj _18vk " href="javascript:void(0)" id="shareLinkId" role="button" tabindex="0" title="Send this to friends or post it on your Timeline." onclick="openShareTab()">'+shresTrans+'</a>\
                                      </span>\
                                              </span>\
                                          </div>\
                                      </div>\
                                      </div>\
                                  </div>';
                              
                });
                $(".feedlist-container").append(listItems);
                //$("_scroll_load_more_loading").append(listItems);
                checkDataStatus=0;

                var topicLIkes=userLikeAndUnlike.topic_like;
                if(topicLIkes){
                  topicLIkes.forEach(function(topicLikeId){
                    if(topicLikeId){
                      var topicId=topicLikeId;
                      var likeStatus=jQuery('.'+topicId).hasClass('sx_44a25c');
                      if(likeStatus==true){
                          jQuery('.'+topicId).removeClass('sx_44a25c');
                          jQuery('.'+topicId).addClass('sx_44a25d');
                      }

                      jQuery('#UReactionLink-'+topicId).addClass('liked');
                    }

                  });
                }

            },
            error: function(jqXHR, textStatus, errorThrown){
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
            }


        });

    })();


        // error: function(jqXHR, textStatus, errorThrown){

        //   jQuery(".commentErrorStatus").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
        //   console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        // }
    $("figure").mouseleave(
      function () {
        $(this).removeClass("hover");
      }
    );
    
$(".videoSliderPlay").click(function(){
  alert('asdfaf');
});
function delegateClick(videoPlayerId,video_backup_url,video_cdn_url){

  var playerId="player-"+videoPlayerId;
  var playerId1="#player-"+videoPlayerId;
  var backup_url=video_backup_url;
  var btnPlayerId = '.videoPlayButtonDetails-'+videoPlayerId;
  var video = document.getElementById(playerId);

    //openFullscreen(video);

    if(video.paused) {
      $(".videoSliderPlay").each(function() {
          $(this).get(0).pause();
      });
      $(".playButtonStatus").each(function() {
        var checkPlayButtonStatus= $(this).hasClass('play-button');
        if(!checkPlayButtonStatus){
            //$(this).addClass('play-button');
        }
      });


    var newSrc='/media/mute_icon.svg';
    $('#mutedImageId').attr('src', newSrc);
    $(btnPlayerId).removeClass('play-button');

      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(video_cdn_url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
          video.play();
          loaderHide();
      });

      hls.on(Hls.Events.ERROR, function (event, data) {debugger;
        if (data.fatal) {
          switch(data.type) {
          case Hls.ErrorTypes.NETWORK_ERROR:
          // try to recover network error
            console.log("fatal network error encountered, try to recover");
            hls.startLoad();
            video.src = backup_url;
            video.addEventListener('loadedmetadata',function() {
              video.play();
              loaderHide();
            });

            break;
          case Hls.ErrorTypes.MEDIA_ERROR:
            console.log("fatal media error encountered, try to recover");
            hls.recoverMediaError();
            break;
          default:
          // cannot recover
            hls.destroy();
            break;
          }
        }
      });


     }
      else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = backup_url;
        video.addEventListener('loadedmetadata',function() {
          video.play();
          loaderHide();
        });
      }



  } else {
    
    $(".videoSliderPlay").each(function() {
          $(this).get(0).pause();         
    });
    video.pause();
    var checkPlayButtonStatus= $('.playButtonStatus').hasClass('play-button');
    if(!checkPlayButtonStatus){
      //$('.playButtonStatus').addClass('play-button');
    }
    //video.removeAttribute('controls','true');
    $(btnPlayerId).removeClass('play-button');
    //$(btnPlayerId).addClass('play-button');
  }
}

function openFullscreen(elem) {
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.mozRequestFullScreen) { /* Firefox */
    elem.mozRequestFullScreen();
  } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari and Opera */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE/Edge */
    elem.msRequestFullscreen();
  }
}


    var sideBarDetails="";
    var sideBarCommentDetails="";
    var muteStatus=false;
    var isLoading = false;
    var hideErrorMsg = true;
    
    var retryCount=0;

function video_play_using_video_js(url,backup_url,image) {
    
    var video = document.getElementById('player');

      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
          video.play();
          loaderHide();
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
      video.on("waiting", function ()
      {
          this.addClass("vjs-custom-waiting");
      });
      video.on("playing", function ()
      {
          this.removeClass("vjs-custom-waiting");
      });

  //   video.src="";
  //   const config = {
  //       autoStartLoad: true,
  //       maxBufferSize: 1 * 1000 * 1000,
  //       manifestLoadingMaxRetry: 300000,
  //       manifestLoadingMaxRetryTimeout: 1000,
  //       levelLoadingMaxRetry: 300000,
  //       levelLoadingMaxRetryTimeout: 1000,
  //       fragLoadingMaxRetry: 300000,
  //       fragLoadingMaxRetryTimeout: 1000
  //   }

    

  //   var hls = new Hls();

  //   if(Hls.isSupported()) {
  //       let retrying = false;
        
  //       video.onplaying = () => {
  //           isLoading = false;
  //           hideErrorMsg = false;
  //           //clearInterval(retry);
  //           retrying = false;

  //       }
        
  //       hls.loadSource(url);
  //       hls.attachMedia(video);
  //       hls.on(Hls.Events.MANIFEST_PARSED,function() {
  //       playPromise= video.play();

  //       if (playPromise !== undefined) {
  //           playPromise.then(_ => {
  //           })
  //           .catch(error => {
  //               console.log(error);

  //           });
  //       }

  //           loaderHide();
  //       });
    
  //       hls.on(Hls.Events.ERROR, function (event, data) {
  //           if (!hideErrorMsg) {
  //               isLoading = true;
  //               hideErrorMsg = true;
  //           }
  //           if (data.fatal) {
  //             switch(data.type) {
  //             case Hls.ErrorTypes.NETWORK_ERROR:
              
  //               console.log("fatal network error encountered, try to recover");
  //               if (!retrying) {
  //                   if(retryCount<2){
  //                     retryLiveStream(hls,backup_url);
  //                   }
                    
  //               }
  //               break;
  //             case Hls.ErrorTypes.MEDIA_ERROR:
  //               console.log("fatal media error encountered, try to recover");
  //               if (!retrying) {
  //                   if(retryCount<3){
  //                     retryLiveStream(hls,backup_url);
  //                   }
                    
  //               }
  //               hls.recoverMediaError();
  //               break;
  //             }
  //           }
  //       });
  //   }else if (video.canPlayType('application/vnd.apple.mpegurl')) {
  //   video.src = file;
  //   video.addEventListener('loadedmetadata',function() {
  //     video.play();
  //     loaderHide();
  //   });
  // }
}

function retryLiveStream(hls, url) {
    retrying = true;
    retryCount++;
    hls.loadSource(url);
    hls.startLoad();
    loaderHide();
}



    function openVideoInPopup(file,image,indexId){
        loaderShow();
        var singleItemData=[];
        indexId=indexId-1;
        $("#indexId").val(indexId);

        $("#modelPopup").show();
        jwplayer('player').setMute(false);
        var newSrc='/media/mute_icon.svg';
        $('#mutedImageId').attr('src', newSrc);
        $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
        singleItemData=playListData[indexId];
        var preBufferDone = false;
        var video_backup="";
        var video_backup=singleItemData.question_video;

        video_play_using_video_js(file,video_backup,image);
          
        var shareURL=site_base_url+singleItemData.slug+'/'+singleItemData.id+'';
        var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
            $("#topicID").val(singleItemData.id);
            $("#currentPlayUserId").val(singleItemData.user.userprofile.id);

            $("#topicCreatorUsername").val(singleItemData.user.username);
            $(".video-meta-title").html(singleItemData.title);
            $("#shareInputbox").val(shareURL);
            var bigCommentLikeDet='<strong><span id="likeCountId">'+singleItemData.likes_count+'</span> '+likeTrans+' · <span id="commentCountId">'+singleItemData.comment_count+'</span> '+commentsTrans+'</strong>';
            $("#sideBarId").html(sideBarDetails);
            $("._video_card_big_meta_info_count").html(bigCommentLikeDet);

            //===================== Comment and Like count ===============

            $("#totalLikeCount").val(singleItemData.likes_count);
            $("#totalCommentCount").val(singleItemData.comment_count);

            //===================Comment and Like Count end =============

            
            var userprofileName=singleItemData.user.userprofile.name;
            var userHandleName=singleItemData.user.username;
            var videoTitle=singleItemData.title;
            var profilePics = singleItemData.user.userprofile.profile_pic;
            if(profilePics==''){
               profilePics= '/media/user.svg';
            }


            var likeStatus="";

            likeStatus="liked";
            var likeStatusClass=jQuery("#UReactionLink").hasClass('liked');
            if(likeStatusClass==true){
                jQuery("#UReactionLink").removeClass('liked');
                jQuery(".sp_ddXiTdIB8vm").addClass('sx_44a25c');
                jQuery(".sp_ddXiTdIB8vm").removeClass('sx_44a25d');
            }

            var likedCheck=userLikeAndUnlike.topic_like;
            if(undefined !== likedCheck && likedCheck.length>0){
                var lStatus = likedCheck.includes(singleItemData.id);
                if(lStatus==true){
                    likeStatus="liked";
                    var likeStatusClass=jQuery("#UReactionLink").hasClass('liked');
                    if(likeStatusClass==false){
                        jQuery("#UReactionLink").addClass('liked');
                        jQuery(".sp_ddXiTdIB8vm").removeClass('sx_44a25c');
                        jQuery(".sp_ddXiTdIB8vm").addClass('sx_44a25d');
                    }

                }
            } 

            //=========Check Follow User ==============
            var loginStatus=check_login_status();
            if(loginStatus==true){
                var countFollowStatus=userLikeAndUnlike.all_follow;
                if(undefined !==countFollowStatus && countFollowStatus.length>0){
                    var currentUserTopic=singleItemData.user.userprofile.id;
                    var followList=userLikeAndUnlike.all_follow;
                    followList.forEach(function(followId){
                        if(currentUserTopic==followId){
                            followStatus=jQuery('.followStatusChangePopup').hasClass('sx_5da455');
                            if(followStatus==true){
                                jQuery('.followStatusChangePopup').removeClass('sx_5da455');
                                jQuery('.followStatusChangePopup').addClass('sx_5da456');
                                jQuery('.btnTextChangePopup').text(followed_trans);
                            }else{
                                jQuery('.followStatusChangePopup').removeClass('sx_5da456');
                                jQuery('.followStatusChangePopup').addClass('sx_5da455');
                                jQuery('.btnTextChangePopup').text(follow_trans);
                            }
                        }

                    });
                }
            }
            //============== End=======================


            
           // document.getElementById('profileImageUserId').style.background = 'url('+profilePics+')';
           var profileURL='/'+userHandleName+'/';
            $("#profileImageUserId").css("background-image", "url(" + profilePics + ")");
            $(".shareandliketabprofileimage").attr("src", ""+profilePics+"");
            $(".userProfileURL").attr("href", ""+profileURL+"");
            $("._video_card_big_user_info_nickname").html(userprofileName);
            $("._video_card_big_user_info_handle").html(userHandleName);
            $("._video_card_big_meta_info_title_video").html(videoTitle);
            //$("._video_card_big_meta_info_title_video").html(videoTitle);
            loaderBoloShow();
            listCommentsById(singleItemData);
      
        var sideBarCommentDetails="";
        var origin   = window.location.origin;
        param1=singleItemData.slug;
        param2=singleItemData.id;
        history.pushState(null, null, '?video='+param1+'/'+param2);
        followLikeList();


    }

    function muteAndUnmutePlayer(){
        // jwplayer().setMute();
        // var muteStatus=jwplayer('player').getMute();
        // if(muteStatus==true){
        //     var newSrc='/media/sound_mute.svg';
        // $('#mutedImageId').attr('src', newSrc);
        // }else{
        //     var newSrc='/media/mute_icon.svg';
        // $('#mutedImageId').attr('src', newSrc);
        // }

        if($("video").prop('muted')){

          $("video").prop('muted', false);
          var newSrc='/media/mute_icon.svg';
          $('#mutedImageId').attr('src', newSrc);
        }else{
            $("video").prop('muted', true);
            var newSrc='/media/sound_mute.svg';
            $('#mutedImageId').attr('src', newSrc);
        }
    }

    function muteAndUnmutePlayerFeed(videoPlayerId){

  var playerId="player-"+videoPlayerId;
  var playerId1="#player-"+videoPlayerId;
  var btnPlayerId = '.videoPlayButtonDetails-'+videoPlayerId;
  var video = document.getElementById(playerId);

        if($("video").prop('muted')){

          $("video").prop('muted', false);
          var newSrc='/media/mute_icon.svg';
          $('.'+videoPlayerId).attr('src', newSrc);
        }else{
            $("video").prop('muted', true);
            var newSrc='/media/sound_mute.svg';
            $('.'+videoPlayerId).attr('src', newSrc);
        }
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


    function listCommentsById(singleTopicData){

        var topicId=singleTopicData.id;
        var topicSlug=singleTopicData.slug;
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
                   profileImage='/media/user.svg';
                }else{
                    profileImage=userProfile.profile_pic;
                }
                var likeStatus="";
                var likeTxt="Like";
                

                var likeStatusClass=jQuery(".likeStatusInfo").hasClass('liked');
                if(likeStatusClass==true){
                    jQuery(".likeStatusInfo").removeClass('liked');
                }

                if(undefined != userLikeAndUnlike.comment_like){
                    var countLikeStatus=userLikeAndUnlike.comment_like.length;
                    if(countLikeStatus>0){
                        var likedCheck=userLikeAndUnlike.comment_like;
                        var lStatus = likedCheck.includes(itemVideo.id);
                        if(lStatus==true){
                            likeStatus="liked";
                            likeTxt="Liked";
                        }
                    }
                }

                listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div id="likeCommentId-'+itemVideo.id+'" class="_8c74  likeStatusInfo '+likeStatus+' changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">'+likeTxt+'<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';
            });

            $(".videoCommentId").append(listCommentItems);
            var loadMoreComment='<span class="loadMoreComment"><a onclick="loadMoreComments(\''+data.next+'\');" class="" href="javascript:void(0);">Load More Comments...</a></span';
            $(".loadMoreComments").html(loadMoreComment);
            loaderBoloHide();
        });
    }

    function loadMoreComments(nextPageURl){
        loaderBoloShowDynamic('_scroll_load_more_loading_comment');
        if(nextPageURl=='null'){
            var loadMoreComment='<span class="loadMoreComment">No more comment</span';
            $(".loadMoreComments").html(loadMoreComment);
            loaderBoloHideDynamic('_scroll_load_more_loading_comment');
            return false;
        }
        var listCommentItems="";
        //================Comments List =================
        var uri=nextPageURl;
        var res = uri;
        $.get(res, function (data, textStatus, jqXHR) {
            var videoCommentList=data.results;

            var itemCount=0;
            videoCommentList.forEach(function(itemVideo) {itemCount++;
                var profileImage="";
                var userProfile=itemVideo.user.userprofile;
                if(userProfile.profile_pic==""){
                   profileImage='/media/user.svg';
                }else{
                    profileImage=userProfile.profile_pic;
                }

                listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

            });

            $(".videoCommentId").append(listCommentItems);
            var loadMoreComment='<span class="loadMoreComment"><a class="" onclick="loadMoreComments(\''+data.next+'\');" href="javascript:void(0);">Load More Comments...</a></span';
            $(".loadMoreComments").html(loadMoreComment);
            loaderBoloHide();
            loaderBoloHideDynamic('_scroll_load_more_loading_comment');
        });
    }


    function getElementsByPage(currentPage){
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

              listItems +='<div class="_video_feed_item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.backup_url+'\',\''+itemVideo.question_image+'\','+itemCount+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><span class="_avatar_ _avatar_respond" style="background-image: url('+itemVideo.question_image+');"></span><span class="_video_card_footer_likes"><img src="media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>';

            });

           // $("#playlist").append(listItems);

        });

    }


    function followLikeList(){
        var loginStatus=check_login_status();
        if(loginStatus==false){
            return false;
        }

        var ge_local_data="";
            ge_local_data = JSON.parse(localStorage.getItem("access_data"));
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
                var topicLIkes=userLikeAndUnlike.topic_like;
                  topicLIkes.forEach(function(topicLikeId){
                    if(topicLikeId){
                      var topicId=topicLikeId;
                      var likeStatus=jQuery('.'+topicId).hasClass('sx_44a25c');
                      if(likeStatus==true){
                          jQuery('.'+topicId).removeClass('sx_44a25c');
                          jQuery('.'+topicId).addClass('sx_44a25d');
                      }

                      jQuery('#UReactionLink-'+topicId).addClass('liked');
                    }

                  });


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

                    if(response.message=='liked'){
                        jQuery('.changeLikeColor-'+commentId).removeClass('liked');
                        jQuery('.likedStatus-'+commentId).removeClass('hide');
                        jQuery('.changeLikeColor-'+commentId).addClass('liked');


                    }else if(response.message=='unliked'){
                        jQuery('.changeLikeColor-'+commentId).removeClass('liked');
                        jQuery('.likedStatus-'+commentId).removeClass('hide');
                        jQuery('.likedStatus-'+commentId).addClass('hide');
                    }


                  });
              }
            }
      
        });


    }

jQuery(document).ready(function(){
    followLikeList();
});





// $(".event-delegate-maskDesk").click(function(){

//   if(video.paused) {
//     var newSrc='/media/mute_icon.svg';
//     $('#mutedImageId').attr('src', newSrc);
//     $('.videoPlayButtonDetails').removeClass('play-button');
//     video.play();
//   } else {
//     video.pause();
//     $('.videoPlayButtonDetails').removeClass('play-button');
//     $('.videoPlayButtonDetails').addClass('play-button');
//   }
  
// });


// $(".event-delegate-maskMob").click(function(){
// var video = document.getElementById('playerDetailsMobile');

//   if(video.paused) {
//     $('.videoPlayButtonDetails').removeClass('play-button');
//     video.play();
//   } else {
//     video.pause();
//     $('.videoPlayButtonDetails').removeClass('play-button');
//     $('.videoPlayButtonDetails').addClass('play-button');
//   }

  
// });

function likeUnlikeFeed(topicId){
    var likeStatus=jQuery('#UReactionLink-'+topicId).hasClass('liked');
    if(likeStatus==false){
       var loginStatus= check_login_status();
       if(loginStatus==false){
        document.getElementById('gotoLoginPage').click();
       }
       var likeStatus=jQuery('.'+topicId).hasClass('sx_44a25c');
       if(likeStatus==true){
            jQuery('.'+topicId).removeClass('sx_44a25c');
            jQuery('.'+topicId).addClass('sx_44a25d');
       }

        jQuery('#UReactionLink-'+topicId).addClass('liked');
        updateUserLikeStatus(topicId);
    }else{
       jQuery('#UReactionLink-'+topicId).removeClass('hide');
       updateUserLikeStatus(topicId);
       var likeStatus=jQuery('.'+topicId).hasClass('sx_44a25d');
       if(likeStatus==true){
            jQuery('.'+topicId).removeClass('sx_44a25d');
            jQuery('.'+topicId).addClass('sx_44a25c');
            jQuery('#UReactionLink-'+topicId).removeClass('liked');
       }

    }
}



// jQuery('#UReactionLink').on('click',function(){
//     var likeStatus=jQuery('#UReactionLink').hasClass('liked');
//     if(likeStatus==false){
//        var loginStatus= check_login_status();
//        if(loginStatus==false){
//         document.getElementById('gotoLoginPage').click();

//        }
//        var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25c');
//        if(likeStatus==true){
//             jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25c');
//             jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25d');
//        }

//         jQuery('#UReactionLink').addClass('liked');
//         updateUserLikeStatus();
//     }else{
//        jQuery('#UReactionLink').removeClass('hide');
//        updateUserLikeStatus();
//        var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25d');
//        if(likeStatus==true){
//             jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25d');
//             jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25c');
//             jQuery('#UReactionLink').removeClass('liked');
//        }

//     }
    
// });

  function updateUserLikeStatus(topic_id){

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
          data:{topic_id:topic_id},
          success: function(response,textStatus, xhr){
              console.log(response);
          },
          error: function(jqXHR, textStatus, errorThrown){
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
          }

    
      });


  } 

function social_share(shareType){

    var loginStatus=check_login_status();
    if(loginStatus==false){
        document.getElementById('gotoLoginPage').click();
        //document.getElementById('openLoginPopup').click();
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

jQuery(document).ready(function(){
    getElementsByPageSideBar(1);
    getSideBarData();
});

function getElementsByPageSideBar(currentPage){
    loaderBoloShowDynamicDe('_scroll_load_more_loading_user_videos');
    var playListData=[]; 
    var platlistItems;
    var listItems="";
    var itemCount=0;
    var language_id=current_language_id;

    var uri='/api/v1/get_popular_video_bytes/?page='+currentPage+'&language_id='+language_id;
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
              videoTitle=removeTags(itemVideo.title);
              content_title = videoTitle.substr(0, 40) + " ..."
            listItems += '<li><a href="/explore/'+itemVideo.slug+'/'+itemVideo.id+'" ><div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="jsx-3077367275 video-card default"><div class="jsx-3077367275 video-card-mask"><div class="jsx-1633345700 card-footer small"><div class="jsx-1633345700"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideo.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></div></div></div></a></li>';

        });

        $("#playlistTrending").append(listItems);
        loaderBoloHideDynamicDe('_scroll_load_more_loading_user_videos');

    });

}
function loaderBoloShowDynamicDe(classLoader){
    var boloLoader='<img src="/media/loader.gif">';
        $('.'+classLoader).html(boloLoader);

}

function loaderBoloHideDynamicDe(classLoader){
    var boloLoader='';
    $('.'+classLoader).html(boloLoader);
    
}

function getSideBarData(){
    loaderBoloShowDynamic('_scroll_load_more_loading_creator');
    // loaderBoloShowDynamic('_scroll_load_more_loading_discover');

    var listItems="";
    var itemCount=0;
    var language_id=1;
    language_id=current_language_id;
        // headers: {
        //   'Authorization':'Bearer '+accessToken,
        // },
    //var uri='https://www.boloindya.com/api/v1/get_popular_video_bytes/?page=1';
    var uri='/api/v1/get_category_with_video_bytes/';
    var res = encodeURI(uri);
    var page_size=10;
    jQuery.ajax({
        url:res,
        type:"GET",

        data:{'language_id':language_id,'is_with_popular':'True','popular_boloindyans':'True','page_size':page_size},
        success: function(response,textStatus, xhr){
            populaCreatorsItems="";
            populaCategoriesItems="";
            getPopularCategory="";

            var popularCategoriesList=response.category_details;
            var popularCreatorsList=response.popular_boloindyans;
            popularCreatorsList.forEach(function(itemCreator) {itemCount++;
                populaCreatorsItems +=getCreators(itemCreator);
                
                //var videoCommentList=data.results;"total_view":"3444.K",
            });
            $("#creatorId").append(populaCreatorsItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_creator');
    
            // $("#discoverId").append(populaCategoriesItems);
            // loaderBoloHideDynamic('_scroll_load_more_loading_discover');


        }
  
    });
}

function popularBoloIndyan(popularBoloIndyans){
  var popularBolo = popularBoloIndyans;
  console.log(popularBolo);
}



function getCreators(popularCreators){
    var creatorName="";
    var profilePics="";
    if(popularCreators.first_name!=''){
        creatorName=popularCreators.first_name+' '+popularCreators.last_name;
    }else{
        creatorName=popularCreators.username;
    }
    profilePics=popularCreators.userprofile.profile_pic;
    if(popularCreators.userprofile.profile_pic==""){
        profilePics='/media/user.svg';
    }

    var creatorTemplate='<li class="jsx-3959364739">\
                            <a tag="a" class="jsx-1420774184 recommend-item" href="/'+popularCreators.username+'/">\
                                <div class="jsx-2177493926 jsx-578937417 avatar round head normal" style="background-image: url('+profilePics+');"></div>\
                                <div class="jsx-1420774184 info-content">\
                                    <h4 class="jsx-1420774184">'+creatorName+'</h4>\
                                    <p class="jsx-1420774184">@'+popularCreators.username+'</p>\
                                </div>\
                                <div class="jsx-1420774184 arrow-right"></div>\
                            </a>\
                        </li>';
    return creatorTemplate;

}


function removeTags(str) {
  if ((str===null) || (str===''))
  return false;
  else
  str = str.toString();
  return str.replace( /(<([^>]+)>)/ig, '');
}



