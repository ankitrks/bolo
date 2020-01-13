
$(document).ready(function(){
    getCategoryVideos();
    getSideBarData();
});

var userLikeAndUnlike=[];

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

    jQuery.ajax({
        url:res,
        type:"GET",

        data:{'language_id':language_id,'is_with_popular':'True','popular_boloindyans':'True'},
        success: function(response,textStatus, xhr){
            populaCreatorsItems="";
            populaCategoriesItems="";
            getPopularCategory

            var popularCategoriesList=response.category_details;
            var popularCreatorsList=response.popular_boloindyans;
            popularCreatorsList.forEach(function(itemCreator) {itemCount++;
                populaCreatorsItems +=getCreators(itemCreator);
                $("#creatorId").append(populaCreatorsItems);
                //var videoCommentList=data.results;"total_view":"3444.K",
            });
            loaderBoloHideDynamic('_scroll_load_more_loading_creator');
    
            popularCategoriesList.forEach(function(itemCat) {itemCount++;
                populaCategoriesItems +=getPopularCategory(itemCat);
                $("#discoverId").append(populaCategoriesItems);
                //var videoCommentList=data.results;"total_view":"3444.K",
            });
            loaderBoloHideDynamic('_scroll_load_more_loading_discover');


        }
  
    });
}


function getCreators(popularCreators){
    var creatorName="";
    if(popularCreators.first_name!=''){
        creatorName=popularCreators.first_name+' '+popularCreators.last_name;
    }else{
        creatorName=popularCreators.username;
    }

    var creatorTemplate='<li class="jsx-3959364739">\
                            <a tag="a" class="jsx-1420774184 recommend-item" href="/'+popularCreators.username+'/">\
                                <div class="jsx-2177493926 jsx-578937417 avatar round head normal" style="background-image: url('+popularCreators.userprofile.profile_pic+');"></div>\
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
    var popular_categories='<li class="jsx-3959364739">\
                        <a tag="a" class="jsx-1420774184 recommend-item" href="/tag/'+popularCategory.slug+'/">\
                            <div class="jsx-2177493926 jsx-578937417 avatar head normal" style="background-image: url('+popularCategory.category_image+'); border-radius: 2px;"></div>\
                            <div class="jsx-1420774184 info-content">\
                                <h4 class="jsx-1420774184">'+popularCategory.title+'</h4>\
                                <p class="jsx-1420774184">'+popularCategory.total_view+' Views</p>\
                            </div>\
                            <div class="jsx-1420774184 arrow-right"></div>\
                        </a>\
                    </li>';
    return popular_categories;
}


    var playListData=[];
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
    var uri='/api/v1/get_category_detail_with_views/';
    var res = encodeURI(uri);

    jQuery.ajax({
        url:res,
        type:"POST",
        data:{'category_id':category_id,language_id:language_id},
        success: function(response,textStatus, xhr){
            userVideoItems="";
            var videoItemList=response.category_details.topics;
            var itemCount=0;
            videoItemList.forEach(function(itemCreator) {itemCount++;
                playListData[itemCreator.id]=itemCreator;
                userVideoItems +=getVideoItem(itemCreator,itemCreator.id);
                $("#categoryVideosListId").append(userVideoItems);
      
            });
            loaderBoloHideDynamic('_scroll_load_more_loading_user_videos');
            //playListData=videoItemList;

        }
  
    });
}

function getVideoItem(videoItem,itemCount){

    var userVideoItem = '<div class="jsx-1410658769 video-feed-item">\
            <div class="jsx-1410658769 _ratio_">\
                <div class="jsx-1410658769" style="padding-top: 148.438%;">\
                    <div class="jsx-1410658769 _ratio_wrapper">\
                        <a href="javascript:void(0)" onClick="openVideoInPopup(\''+videoItem.backup_url+'\',\''+videoItem.question_image+'\','+itemCount+');" class="jsx-2893588005 video-feed-item-wrapper">\
                            <div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+videoItem.question_image+');">\
                                <div class="jsx-3077367275 video-card default">\
                                    <div class="jsx-3077367275 video-card-mask">\
                                        <div class="jsx-1543915374 card-footer normal no-avatar">\
                                            <div class="jsx-1543915374"><img src="/media/download.svg" class="jsx-1543915374 like-icon"><span class="jsx-1543915374">'+videoItem.likes_count+'</span></div>\
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
      
        playerInstance.setup({
          file: file,
          controls: false,
          image:image,
          autostart:'true',
          mute:'false'
      });
      playerInstance.on('play', function() {
            loaderHide();
            preBufferDone = true;
          
      }); 

    playerInstance.on('buffer', function() {

      var time = 1;

    });   


    playerInstance.on('error', function(event) {
        loaderHide();
        var erroCode=event.code;
        playerInstance.setup({
            file: singleItemData.backup_url,
            controls: false,
            image:image,
            autostart:'true',
            mute:'false'
        });


    });

    playerInstance.on('complete', function() {
        jwplayer('player').setMute(true);

    });


    var shareURL=site_base_url+singleItemData.user.username+'/'+singleItemData.id+'';

    var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
        $("#topicID").val(singleItemData.id);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("#shareInputbox").val(shareURL);
        var bigCommentLikeDet='<strong>'+singleItemData.likes_count+' '+likeTrans+' · '+singleItemData.comment_count+' '+commentsTrans+'</strong>';
        $("#sideBarId").html(sideBarDetails);
        $("._video_card_big_meta_info_count").html(bigCommentLikeDet);

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
        history.pushState(null, null, '?video='+param1);
 }

 function muteAndUnmutePlayer(){
  jwplayer().setMute();
  var muteStatus=jwplayer('player').getMute();
  if(muteStatus==true){
    var newSrc='/media/sound_mute.svg';
    $('#mutedImageId').attr('src', newSrc);
  }else{
    var newSrc='/media/mute_icon.svg';
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

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
        });
        $(".videoCommentId").append(listCommentItems);
        var loadMoreComment='<span class="loadMoreComment"><a class="" onclick="loadMoreComments(\''+data.next+'\');" href="javascript:void(0);">Load More Comments...</a></span';
        $(".loadMoreComments").html(loadMoreComment);
        loaderBoloHide();
    });
}
function followLikeList(){
    check_login_status();

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



