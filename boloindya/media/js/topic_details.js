
$(document).ready(function(){
    getCategoryVideos();
    getSideBarData();
});





var page = 1;
var checkDataStatus=0;
var userLikeAndUnlike=[];
var totalCountVideo =0;
var playListData=[];

function getSideBarData(){
    loaderBoloShowDynamic('_scroll_load_more_loading_creator');
    loaderBoloShowDynamic('_scroll_load_more_loading_discover');

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
            getPopularCategory

            var popularCategoriesList=response.category_details;
            var popularCreatorsList=response.popular_boloindyans;
            popularCreatorsList.forEach(function(itemCreator) {itemCount++;
                populaCreatorsItems +=getCreators(itemCreator);
                
                //var videoCommentList=data.results;"total_view":"3444.K",
            });
            $("#creatorId").append(populaCreatorsItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_creator');
    
            popularCategoriesList.forEach(function(itemCat) {itemCount++;
                populaCategoriesItems +=getPopularCategory(itemCat);
                
                //var videoCommentList=data.results;"total_view":"3444.K",
            });
            $("#discoverId").append(populaCategoriesItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_discover');


        }
  
    });
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
        profilePics='/media/demo_user.png';
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


function getPopularCategory(popularCategory){
    var category_title;
    currentLanguageName=current_language_name.toLowerCase();
    if(currentLanguageName!='english'){
        category_title=currentLanguageName+'_title';
    }else{
        category_title='title';
    }

    var popular_categories='<li class="jsx-3959364739">\
                        <a tag="a" class="jsx-1420774184 recommend-item" href="/tag/'+popularCategory.slug+'/">\
                            <div class="jsx-2177493926 jsx-578937417 avatar head normal" style="background-image: url('+popularCategory.category_image+'); border-radius: 2px;"></div>\
                            <div class="jsx-1420774184 info-content">\
                                <h4 class="jsx-1420774184">'+popularCategory[category_title]+'</h4>\
                                <p class="jsx-1420774184">'+popularCategory.total_view+' Views</p>\
                            </div>\
                            <div class="jsx-1420774184 arrow-right"></div>\
                        </a>\
                    </li>';
    return popular_categories;
}



function getCategoryVideos(){

    loaderBoloShowDynamic('_scroll_load_more_loading_user_videos');
    var category_id= $("#currentCatId").val();
     
    var platlistItems;

    var listItems="";
    var itemCount=0;
    var language_id=1;
    language_id=current_language_id;
    var userVideoItems="";
        // headers: {
        //   'Authorization':'Bearer '+accessToken,
        // },
        //http://www.boloindya.com/api/v1/get_vb_list/?limit=1&offset=11
    //var uri='https://www.boloindya.com/api/v1/get_popular_video_bytes/?page=1';
    var uri='/api/v1/get_category_video_bytes/';
    //var uri='/api/v1/get_category_detail_with_views/';
    var res = encodeURI(uri);

    jQuery.ajax({
        url:res,
        type:"POST",
        data:{'category_id':category_id,'language_id':language_id,'page':1},
        success: function(response,textStatus, xhr){
            userVideoItems="";
            var videoItemList=response.topics;
            //var videoItemList=response.category_details.topics;
            var itemCount=0;
            videoItemList.forEach(function(itemCreator) {itemCount++;
                playListData[itemCreator.id]=itemCreator;
                userVideoItems +=getVideoItem(itemCreator,itemCreator.id);
            });
            $("#categoryVideosListId").append(userVideoItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_user_videos');
            //playListData=videoItemList;

        }
  
    });
}

    $(window).scroll(function() {
        var scorh=Number($(window).scrollTop() + $(window).height());
        if($(window).scrollTop() + $(window).height() > $("#categoryVideosListId").height()){

            if(checkDataStatus==0){
                page++;
                loadMoreData(page);
            }

        }
    });

    function loadMoreData(page){
    
    var platlistItems;
    checkDataStatus=1;
    var category_id= $("#currentCatId").val();

    var listItems="";
    var itemCount=0;
    var language_id=current_language_id;
    //var uri='https://www.boloindya.com/api/v1/get_popular_video_bytes/?page=1';
    var uri='/api/v1/get_category_video_bytes/';
    var res = encodeURI(uri);
      $.ajax(
            {
                url:res,
                data:{'category_id':category_id,'language_id':language_id,'page':page},
                type: "POST",
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
            var videoItemList=data.topics;
            //var videoItemList=response.category_details.topics;
            var itemCount=0;
            var userVideoItems;
            videoItemList.forEach(function(itemCreator) {itemCount++;
                playListData[itemCreator.id]=itemCreator;
                userVideoItems +=getVideoItem(itemCreator,itemCreator.id);
            });
            $("#categoryVideosListId").append(userVideoItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_user_videos');

            })
            .fail(function(jqXHR, ajaxOptions, thrownError)
            {
                if(jqXHR.status!=201){

                }

                $('.ajax-load').html("No more records found");
            });
    }




function getVideoItem(videoItem,itemCount){
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(videoItem.title);
        content_title = videoTitle.substr(0, 40) + " ...";
    var userVideoItem = '<div class="jsx-1410658769 video-feed-item">\
            <div class="jsx-1410658769 _ratio_">\
                <div class="jsx-1410658769" style="padding-top: 148.438%;">\
                    <div class="jsx-1410658769 _ratio_wrapper">\
                        <a href="javascript:void(0)" onClick="openVideoInPopup(\''+videoItem.question_video+'\',\''+videoItem.question_image+'\','+itemCount+');" class="jsx-2893588005 video-feed-item-wrapper">\
                            <div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+videoItem.question_image+');">\
                                <div class="jsx-3077367275 video-card default">\
                                    <div class="jsx-3077367275 video-card-mask">\
                                        <div class="jsx-1543915374 card-footer normal no-avatar">\
                                            <div class="jsx-1543915374"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+videoItem.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+videoItem.likes_count+'</span></div>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>\
                        </a>\
                    </div>\
                </div>\
            </div>\
        </div>';

        return userVideoItem;
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


 function openVideoInPopup(file,image,indexId){
  loaderShow();
  var singleItemData=[];
    $("#indexId").val(indexId);
    singleItemData=playListData[indexId];
  $("#modelPopup").show();
  var newSrc='/media/mute_icon.svg';
  $('#mutedImageId').attr('src', newSrc);
  $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');

    var preBufferDone = false;
    var video_backup="";
    var video_backup=singleItemData.question_video;
    video_play_using_video_js(file,video_backup,image);

      
    //     playerInstance.setup({
    //       file: file,
    //       controls: false,
    //       image:image,
    //       autostart:'true',
    //       mute:'false'
    //   });
    //   playerInstance.on('play', function() {
    //         loaderHide();
    //         preBufferDone = true;
          
    //   }); 

    // playerInstance.on('buffer', function() {

    //   var time = 1;

    // });   


    // playerInstance.on('error', function(event) {
    //     loaderHide();
    //     var erroCode=event.code;
    //     playerInstance.setup({
    //         file: singleItemData.backup_url,
    //         controls: false,
    //         image:image,
    //         autostart:'true',
    //         mute:'false'
    //     });


    // });

    // playerInstance.on('complete', function() {
    //     jwplayer('player').setMute(true);

    // });


    var shareURL=site_base_url+singleItemData.slug+'/'+singleItemData.id+'';

    var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
        $("#topicID").val(singleItemData.id);
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
           profilePics= '/media/demo_user.png';
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

        $("#topicID").val(singleItemData.id);
        $("#currentPlayUserId").val(singleItemData.user.userprofile.id);

        $("#topicCreatorUsername").val(singleItemData.user.username);

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

 function muteAndUnmutePlayer(){
  // jwplayer().setMute();
  // var muteStatus=jwplayer('player').getMute();
  // if(muteStatus==true){
  //   var newSrc='/media/sound_mute.svg';
  //   $('#mutedImageId').attr('src', newSrc);
  // }else{
  //   var newSrc='/media/mute_icon.svg';
  //   $('#mutedImageId').attr('src', newSrc);
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
           profileImage='/media/demo_user.png';
        }else{
            profileImage=userProfile.profile_pic;
        }

        var likeStatus="";
        

        var likeStatusClass=jQuery(".likeStatusInfo").hasClass('liked');
        if(likeStatusClass==true){
            jQuery(".likeStatusInfo").removeClass('liked');
        }

        var countLikeStatus=userLikeAndUnlike.comment_like;

        if(undefined !==countLikeStatus && countLikeStatus.length>0){
            var likedCheck=userLikeAndUnlike.comment_like;
            var lStatus = likedCheck.includes(itemVideo.id);
            if(lStatus==true){
                likeStatus="liked";
            }
        }


        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 likeStatusInfo '+likeStatus+' changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
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
           profileImage='/media/demo_user.png';
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
function followLikeList(){
    var checkstatus=check_login_status();
    if(checkstatus==false){
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
        //all_category_follow
        if(response.all_category_follow){
            var listFollows=response.all_category_follow;

            var current_categoryId=$("#currentCatId").val();
            current_categoryId=parseInt(current_categoryId, 10);
            var statusFollow=jQuery.inArray( current_categoryId, listFollows )
            if(statusFollow>=0){
                $('#followCategoryStatus-'+current_categoryId).html(followed_trans);
                $('.followStatusChange-'+current_categoryId).removeClass('sx_5da455');
                var checkstatusBu=$('.followStatusChange-'+current_categoryId).hasClass('sx_5da456');
                if(!checkstatusBu){
                    $('.followStatusChange-'+current_categoryId).addClass('sx_5da456');
                }
            }

        }



        }
  
    });

}

jQuery(document).ready(function(){
    followLikeList();
});



