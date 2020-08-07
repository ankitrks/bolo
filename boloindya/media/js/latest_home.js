    var page = 1;
    var checkDataStatus=1;
    var checkDataStatusCat=1;
    var userLikeAndUnlike=[];
    var totalCountVideo =0;
    var playListData=[];
    $(window).scroll(function() {
        var scorh=Number($(window).scrollTop() + $(window).height());
        if($(window).scrollTop() + $(window).height() > Number($("#categoryIdList").height()+540)){

            if(checkDataStatusCat==0){
                page++;
                loaderBoloShowDynamic('_scroll_load_more_loading_right');
                getCategoryWithVideos(page);
            }

        }
    });

$(document).ready(function(){
    //loadMoreData(1);
    getCategoryWithVideos(1);
});

var topicList=[];
function getCategoryWithVideos(page){
    //loaderBoloShowDynamic('_scroll_load_more_loading_right');
    loaderBoloShowDynamic('_scroll_load_more_loading_left');
        var playListData=[]; 
    var platlistItems;
    checkDataStatusCat=1;
    var listItems="";
    var itemCount=0;
    var language_id=1;
    var page_size=2;
    var page_num=page;
    var uri='/api/v1/get_category_with_video_bytes/';
    var res = encodeURI(uri);
    var category_with_video_list="";
    language_id=current_language_id;

    jQuery.ajax({
        url:res,
        type:"GET",

        data:{'language_id':language_id,'is_with_popular':'True','popular_boloindyans':'True','page_size':page_size,'page':page_num},
        success: function(response,textStatus, xhr){
            populaCreatorsItems="";
            var populaCategoriesItems="";
            var populvideoItems="";
            var itemCount=0;
            var responseData=response.category_details;
            responseData.forEach(function(itemCategory) {itemCount++;
                populaCreatorsItems =popularCategoryHeading(itemCategory);
                populvideoItems="";
                var topicData=itemCategory.topics;
                populvideoItems+='<div class="_explore_feed_card">';
                var videoItemCount=0;
                topicData.forEach(function(itemVideoByte){videoItemCount++;
                    if(videoItemCount<4){
                        topicList[itemVideoByte.id]=itemVideoByte;
                        populvideoItems +=popularCategoryItem(itemVideoByte);
                    }
                });
                populvideoItems+='</div>';
                category_with_video_list='<div class="_explore_feed_item">'+populaCreatorsItems+''+populvideoItems+'</div>';

                if(itemCount % 2 == 0) {
                    loaderBoloHideDynamic('_scroll_load_more_loading_right');
                    $("#catWithVideoIdRight").append(category_with_video_list);
                }else{
                     loaderBoloHideDynamic('_scroll_load_more_loading_left');
                    $("#catWithVideoId").append(category_with_video_list);
                }
            });
            checkDataStatusCat=0;
            if(page==1){
              followLikeList();
            }

            updateFollowStatus();

        },
        error: function(jqXHR, ajaxOptions, thrownError) {
            console.log(jqXHR);
           loaderBoloHideDynamic('_scroll_load_more_loading_left');
           loaderBoloHideDynamic('_scroll_load_more_loading_right');

        }/*  end of error */

  
    });
}


function popularCategoryHeading(itemCategory){

    var category_title;
    currentLanguageName=current_language_name.toLowerCase();
    if(currentLanguageName!='english'){
        category_title=currentLanguageName+'_title';
    }else{
        category_title='title';
    }
    //follow_category
    var popular_cat_heading_template='<div class="_explore_feed_header"><div class="jsx-2836840237 _card_header_"><a class="jsx-2836840237" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_cover" style="background-image: url('+itemCategory.category_image+');"></div></a><a title="#'+itemCategory.slug+'('+itemCategory.total_view+' views)" class="jsx-2836840237 _card_header_link" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_content"><h3 class="jsx-2836840237 _card_header_title">'+itemCategory[category_title]+'</h3><strong class="jsx-2836840237 _card_header_subTitle">'+itemCategory.total_view+' views</strong></div></a><p class="jsx-2836840237 _card_header_desc_follow"><span class="unit"><button onclick="follow_category_discover('+itemCategory.id+');" class="_4jy1 _4jy4 _517h _51sy _42ft " style="float: none;" type="button" value="1"><i alt="" class="_3-8_ img sp_66mIw9cKlB9 followCategoryStatus-'+itemCategory.id+' followCheckCat sx_5da455"></i><span class="btnTextChangeCat-'+itemCategory.id+'">'+follow_trans+'</span></button></span></p><p class="seeAll"><a href="/tag/'+itemCategory.slug+'/">See All ></a></p></div></div>';
    return popular_cat_heading_template;
}

function popularCategoryItem(itemVideoByte){
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(itemVideoByte.title);
        content_title = videoTitle.substr(0, 40) + " ..."

    var category_item_template='<div class="jsx-1410658769 _explore_feed_card_item" onClick="openVideoInPopupCat('+itemVideoByte.id+');" ><div class="jsx-1410658769 _ratio_"><div class="jsx-1410658769" style="padding-top: 148.148%;"><div class="jsx-1410658769 _ratio_wrapper"><a href="javascript:void(0)"><div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+itemVideoByte.question_image+');"><div class="jsx-3077367275 video-card default"><div class="jsx-3077367275 video-card-mask"><div class="jsx-1633345700 card-footer normal no-avatar"><div class="jsx-1633345700"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideoByte.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideoByte.likes_count+'</span></div></div></div></div></div></a></div></div></div></div>';
    return category_item_template;
}


    

    var listVideoIds=[];

    function loadMoreData(page){
    
    var platlistItems;
    checkDataStatus=1;
    var javascriptdata="<script>$('.next').on('click', function(){intslide('stop');sact('next', 0, 400);intslide('start');});</script>";
    var listItems="";
    var itemCount=0;
    var language_id=current_language_id;
    //var uri='https://www.boloindya.com/api/v1/get_popular_video_bytes/?page=1';
    var uri='/api/v1/get_popular_video_bytes/?page='+page+'&language_id='+language_id;
    var res = encodeURI(uri);
      $.ajax(
            {
                url:res,
                type: "get",
                beforeSend: function()
                {
                    $('.ajax-load').show();
                }
            })
            .done(function(data)
            {
                if(data == " "){
                    $('.ajax-load').html("No more records found");
                    return;
                }
                checkDataStatus=0;
           var topicVideoList=data.topics;
            //playListData+=topicVideoList;
            var itemCount=-1;
            var currentStatus=0;

            var sliderItemDiv="";
            var divChangeCount=0;

            sliderItemDiv +='<div id="carousel" class="owl-carousel">';
            topicVideoList.forEach(function(itemVideo) {itemCount++;totalCountVideo++;currentStatus++;
                //playListData+=itemVideo;
                divChangeCount++;
                listVideoIds.push(itemVideo.id);
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
            var current_slide='';
            if(currentStatus==1){
              current_slide='current';
            }

            listItems +='<div class="_video_feed_item1 item"><img onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+totalCountVideo+');" class="_video_card_mute _video_card_mute_left_top" id="mutedImageId" src="/media/sound_mute.svg"><video onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+totalCountVideo+');"   id="player-'+itemVideo.id+'" preload="auto" muted autoplay="false" poster="'+itemVideo.question_image+'" src="'+itemVideo.backup_url+'" class="videoCentered videoSliderPlay"></video></div>';
            //listItems +='<div class="_video_feed_item1 item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+totalCountVideo+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideo.likes_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>';
            // if(divChangeCount==4){

            //   divChangeCount=0;
            // sliderItemDiv +=listItems+'</div><div class="slideitem ">';
            // listItems="";
            // }

            });
            
              sliderItemDiv +=listItems+'</div><script>\
jQuery("#carousel").owlCarousel({\
  autoplay: true,\
  lazyLoad: true,\
  loop: true,\
  dots: false,\
  margin: 20,\
  responsiveClass: true,\
  autoHeight: true,\
  autoplayHoverPause : true,\
  autoplayTimeout: 7000,\
  smartSpeed: 800,\
  nav: true,\
  responsive: {\
    0: {\
      items: 2\
    },\
    600: {\
      items: 2\
    },\
    1024: {\
      items: 4\
    },\
    1366: {\
      items: 4\
    }\
  }\
});\
</script>';
       

                $('.ajax-load').hide();
                $("#slideshow").html(sliderItemDiv);
                // playListData.forEach(function(itemVideo){
                //   var playerId="player-"+itemVideo.id;
                //   var video_backup=itemVideo.question_video;
                //   var questionImage = itemVideo.question_image;
                //   video_play_using_video_dynamic(video_backup,video_backup,playerId);
                // });
                 
                
                
               
            })
            .fail(function(jqXHR, ajaxOptions, thrownError)
            {
                if(jqXHR.status!=201){

                }

                $('.ajax-load').html("No more records found");
            });
    }


function set_data_in_cache(popularItems) {
  localStorage.setItem('popularItems', popularItems);
}

function get_data_from_cache() {
  var listdata=localStorage.getItem('popularItems');
  return listdata;
}

function set_category_data_in_cache(popularCatItems) {
  localStorage.setItem('popularCatItems', popularCatItems);
}

function get_data_from_category_cache() {
  var listCatData=localStorage.getItem('popularCatItems');
  return listCatData;
}

function updateFollowStatus(response){

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

            var countFollowStatusCat=userLikeAndUnlike.all_category_follow;
            if(undefined !==countFollowStatusCat && countFollowStatusCat.length>0){
                var followListCat=userLikeAndUnlike.all_category_follow;
                followListCat.forEach(function(followId){
                    followStatusCat=jQuery('.followCheckCat').hasClass('followCategoryStatus-'+followId);
                    if(followStatusCat==true){
                        jQuery('.followCategoryStatus-'+followId).removeClass('sx_5da455');
                        jQuery('.followCategoryStatus-'+followId).addClass('sx_5da456');
                        jQuery('.btnTextChangeCat-'+followId).text(followed_trans);
                    }

                });
            }
}

function openVideoInPopupSlider(divId,videoURL,backup_url,posterImage) {debugger;
    //var status=$(".videoSliderPlay").prop('muted', true);
    muteAllPlayingVideos();
    var statusMuteSrcId='.muteSrcId_'+divId;
    var playerId="#player-"+divId;
    var muteStatusD=$(playerId).prop('muted');
   if(muteStatusD){
    //mute_icon
    $(playerId).prop('muted', false);
    var newSrc='/media/mute_icon.svg';
    $(statusMuteSrcId).attr('src', newSrc);
  }else{

      $(playerId).prop('muted', true);
      var newSrc='/media/sound_mute.svg';
      $(statusMuteSrcId).attr('src', newSrc);
  }
}

function openVideoInPopupSlider1(divId,videoURL,backup_url,posterImage) {debugger;
    //var status=$(".videoSliderPlay").prop('muted', true);
    var statusMuteSrcId='.muteSrcId_'+divId;
    var playerId="#player-"+divId;
    var muteStatusD=$(playerId).prop('muted');
   if(muteStatusD==false){
    //mute_icon
    //muteAllPlayingVideos();
        $(playerId).prop('muted', true);
        var newSrc='/media/sound_mute.svg';
        $(statusMuteSrcId).attr('src', newSrc);


  }else{
        muteAllPlayingVideos();
        $(playerId).prop('muted', false);
        var newSrc='/media/mute_icon.svg';
        $(statusMuteSrcId).attr('src', newSrc);
  }
}



    function muteAllPlayingVideos(){
        $("video").prop('muted', true);
        var newSrc='/media/sound_mute.svg';
        $('._video_card_mute').attr('src', newSrc);
    }



function openVideoInPopupCat(topicId){
  loaderShow();

  var singleItemData=topicList[topicId];
  $("#indexId").val(singleItemData.id);
  var videoFileName=singleItemData.video_cdn;
  var videoFileImage=singleItemData.question_image;
  $("#modelPopup").show();

  var newSrc='/media/mute_icon.svg';
  $('#mutedImageId').attr('src', newSrc);

    var preBufferDone = false;
    var preBufferDone = false;
    var video_backup="";
    var video_backup=singleItemData.question_video;
    //var video_backup=singleItemData.question_video;
    video_play_using_video_js(video_backup,video_backup,videoFileImage);      

    var shareURL=site_base_url+singleItemData.slug+'/'+singleItemData.id+'';

    var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
        $("#topicID").val(singleItemData.id);
        $("#currentPlayUserId").val(singleItemData.user.userprofile.id);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("#shareInputbox").val(shareURL);
        var bigCommentLikeDet='<strong><span id="likeCountId">'+singleItemData.likes_count+'</span> '+likeTrans+' · <span id="commentCountId">'+singleItemData.comment_count+'</span> '+commentsTrans+'</strong>';
        $("#sideBarId").html(sideBarDetails);
        $("._video_card_big_meta_info_count").html(bigCommentLikeDet);
        $(".video-meta-title").html(singleItemData.title);
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
        if(undefined !==likedCheck && likedCheck.length>0){
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



        var profileURL='/'+userHandleName+'/';
        $("#profileImageUserId").css("background-image", "url(" + profilePics + ")");
        $(".shareandliketabprofileimage").attr("src", ""+profilePics+"");
        $(".userProfileURL").attr("href", ""+profileURL+"");
        $("._video_card_big_user_info_nickname").html(userprofileName);
        $("._video_card_big_user_info_handle").html(userHandleName);
        $("._video_card_big_meta_info_title_video").html(videoTitle);

        loaderBoloShow();
        listCommentsById(singleItemData);

        var sideBarCommentDetails="";
        var origin   = window.location.origin;
        param1=singleItemData.slug;
        param2=singleItemData.id;
        history.pushState(null, null, '?video='+param1+'/'+param2);
        followLikeList();

 }

 $('._global_modal_cancel').click(function(){
    //history.pushState(null, null, '?'+param1);
 });




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

    var language_id=current_language_id;



        // error: function(jqXHR, textStatus, errorThrown){

        //   jQuery(".commentErrorStatus").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
        //   console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        // }
    $("figure").mouseleave(
      function () {
        $(this).removeClass("hover");
      }
    );
    

    var sideBarDetails="";
    var sideBarCommentDetails="";
    var muteStatus=false;
    var isLoading = false;
    var hideErrorMsg = true;
    
    var retryCount=0;

function video_play_using_video_js_old(url,backup_url,image) {
    
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
      else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = backup_url;
        video.addEventListener('loadedmetadata',function() {
          video.play();
          loaderHide();
        });
      }


}

function video_play_using_video_js(url,backup_url,image) {
    
    var video = document.getElementById('player');
    var strUrl = url;
    var backUrl = backup_url;
    url = strUrl.replace("http://", "https://");
    backup_url = backUrl.replace("http://", "https://");
    
    fetch(url)
    .then(_ => {
      video.src = url;
      return video.play();
    })
    .then(_ => {
        console.log('playback started');
        // Video playback started ;)
    })
    .catch(e => {
        console.log('failed started');
 
      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
          video.play();
          loaderHide();
      });
     }

      else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = backup_url;
        video.addEventListener('loadedmetadata',function() {
          video.play();
          loaderHide();
        });
      }

    })

}



function video_play_using_video_dynamic(url,backup_url,playerId) {
    
    var videoPla = document.getElementById(playerId);

      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(url);
        hls.attachMedia(videoPla);
        hls.on(Hls.Events.MANIFEST_PARSED,function() {
          video.play();
          loaderHide();
      });
     }
      else if (videoPla.canPlayType('application/vnd.apple.mpegurl')) {
        videoPla.src = backup_url;
        videoPla.addEventListener('loadedmetadata',function() {
          videoPla.play();
          loaderHide();
        });
      }


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

        //$('.videoSliderPlay')
        muteAllPlayingVideo();
        unmutePlayingVideo();
          
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

    function muteAllPlayingVideo(){
        $("video").prop('muted', true);
        var newSrc='/media/sound_mute.svg';
        $('#mutedImageId').attr('src', newSrc);
        // if($("video").prop('muted')){

        //   $("video").prop('muted', false);
        //   var newSrc='/media/mute_icon.svg';
        //   $('#mutedImageId').attr('src', newSrc);
        // }else{
        //     $("video").prop('muted', true);
        //     var newSrc='/media/sound_mute.svg';
        //     $('#mutedImageId').attr('src', newSrc);
        // }
    }
    function unmutePlayingVideo(){

        if($("#player").prop('muted')){

          $("#player").prop('muted', false);
          var newSrc='/media/mute_icon.svg';
          $('#mutedImageId').attr('src', newSrc);
        }else{
            $("#player").prop('muted', true);
            var newSrc='/media/sound_mute.svg';
            $('#mutedImageId').attr('src', newSrc);
        }
    }

    function muteAndUnmutePlayerSlider(id){
    var videoP = document.getElementById('player-'+id);
      videoP.muted = true;


      // var mutestatus=$("#player-"+id).prop('muted');

      //   if($("#player-"+id).prop('muted')){

      //     $("#player-"+id).prop('muted', false);
      //     var newSrc='/media/mute_icon.svg';
      //     $('#mutedImageId').attr('src', newSrc);
      //   }else{
      //       $("#player-"+id).prop('muted', true);
      //       var newSrc='/media/sound_mute.svg';
      //       $('#mutedImageId').attr('src', newSrc);
      //   }
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

    function pouseAllVideo(){

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
            if(data.next!="" && data.next!='null'){
                var loadMoreComment='<span class="loadMoreComment"><a onclick="loadMoreComments(\''+data.next+'\');" class="" href="javascript:void(0);">Load More Comments...</a></span';
            }
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
            if(data.next!="" && data.next!='null'){
                var loadMoreComment='<span class="loadMoreComment"><a class="" onclick="loadMoreComments(\''+data.next+'\');" href="javascript:void(0);">Load More Comments...</a></span';
            }
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
            //var videoCommentList=data.results;
            }
      
        });


    }

jQuery(document).ready(function(){
    followLikeList();
});

function removeTags(str) {
  if ((str===null) || (str===''))
  return false;
  else
  str = str.toString();
  return str.replace( /(<([^>]+)>)/ig, '');
}






