var userLikeAndUnlike=[];

$(document).ready(function () {
    var itemsMainDiv = ('.MultiCarousel');
    var itemsDiv = ('.MultiCarousel-inner');
    var itemWidth = "";

    $('.leftLst, .rightLst').click(function () {
        var condition = $(this).hasClass("leftLst");
        if (condition)
            click(0, this);
        else
            click(1, this)
    });

   ResCarouselSize();

    $(window).resize(function () {
        ResCarouselSize();
    });

    //this function define the size of the items
    function ResCarouselSize() {
        var incno = 0;
        var dataItems = ("data-items");
        var itemClass = ('.item');
        var id = 0;
        var btnParentSb = '';
        var itemsSplit = '';
        var sampwidth = $(itemsMainDiv).width();
        var bodyWidth = $('body').width();
        $(itemsDiv).each(function () {
            id = id + 1;
            var itemNumbers = $(this).find(itemClass).length;
            btnParentSb = $(this).parent().attr(dataItems);
            itemsSplit = btnParentSb.split(',');
            $(this).parent().attr("id", "MultiCarousel" + id);


            if (bodyWidth >= 1200) {
                incno = itemsSplit[2];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 992) {
                incno = itemsSplit[2];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 768) {
                incno = itemsSplit[1];
                itemWidth = sampwidth / incno;
            }
            else {
                incno = itemsSplit[0];
                itemWidth = sampwidth / incno;
            }
            $(this).css({ 'transform': 'translateX(0px)', 'width': itemWidth * itemNumbers });
            $(this).find(itemClass).each(function () {
                $(this).outerWidth(itemWidth);
            });

            $(".leftLst").addClass("over");
            $(".rightLst").removeClass("over");

        });
    }


    //this function used to move the items
    function ResCarousel(e, el, s) {
        var leftBtn = ('.leftLst');
        var rightBtn = ('.rightLst');
        var translateXval = '';
        var divStyle = $(el + ' ' + itemsDiv).css('transform');
        var values = divStyle.match(/-?[\d\.]+/g);
        var xds = Math.abs(values[4]);
        if (e == 0) {
            translateXval = parseInt(xds) - parseInt(itemWidth * s);
            $(el + ' ' + rightBtn).removeClass("over");

            if (translateXval <= itemWidth / 2) {
                translateXval = 0;
                $(el + ' ' + leftBtn).addClass("over");
            }
        }
        else if (e == 1) {
            var itemsCondition = $(el).find(itemsDiv).width() - $(el).width();
            translateXval = parseInt(xds) + parseInt(itemWidth * s);
            $(el + ' ' + leftBtn).removeClass("over");

            if (translateXval >= itemsCondition - itemWidth / 2) {
                translateXval = itemsCondition;
                $(el + ' ' + rightBtn).addClass("over");
            }
        }
        $(el + ' ' + itemsDiv).css('transform', 'translateX(' + -translateXval + 'px)');
    }

    //It is used to get some elements from btn
    function click(ell, ee) {
        var Parent = "#" + $(ee).parent().attr("id");
        var slide = $(Parent).attr("data-slide");
        ResCarousel(ell, Parent, slide);
    }

});

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

function video_play_using_video_js(url,backup_url,image) {
    
    var video = document.getElementById('player');

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



function openVideoInPopup(topicId){
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

 function muteAndUnmutePlayer(){

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
           profileImage='/media/user.svg';
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


        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 likeStatusInfo '+likeStatus+' changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.topic+','+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
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

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.topic+','+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
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


$(document).ready(function(){
    getCategoryWithVideos();
});

var topicList=[];
function getCategoryWithVideos(){
    loaderBoloShowDynamic('_scroll_load_more_loading_right');
    loaderBoloShowDynamic('_scroll_load_more_loading_left');
        var playListData=[]; 
    var platlistItems;

    var listItems="";
    var itemCount=0;
    var language_id=1;
    var page_size=10;
    var uri='/api/v1/get_category_with_video_bytes/';
    var res = encodeURI(uri);
    var category_with_video_list="";
    language_id=current_language_id;

    jQuery.ajax({
        url:res,
        type:"GET",

        data:{'language_id':language_id,'is_with_popular':'True','popular_boloindyans':'True','page_size':page_size},
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

            followLikeList();

        },
        error: function(jqXHR, ajaxOptions, thrownError) {
            console.log(jqXHR);
           loaderBoloHideDynamic('_scroll_load_more_loading_left');
           loaderBoloHideDynamic('_scroll_load_more_loading_right');

        }/*  end of error */

  
    });
}

function getCreators(popularCreators){
    var creatorName="";
    if(popularCreators.first_name!=''){
        creatorName=popularCreators.first_name+' '+popularCreators.last_name;
    }else{
        creatorName=popularCreators.username;
    }

    var creatorTemplate='<li class="jsx-3102177358 _user_carousel_list-item item" style="width: 243.118px;">\
        <a tag="a" title="Nisha Guragain(@nishaguragain)" class="jsx-3102177358" href="/@nishaguragain">\
            <div class="_user_carousel_avatar round" style=""></div>\
            <h2 class="_user_carousel_title">Nisha Guragain</h2>\
            <h3 class="_user_carousel_sub-title">@nishaguragain</h3>\
            <p class="_user_carousel_followers">20.1m<span class="_user_carousel_followers-text">followers</span></p>\
            <p class="_user_carousel_description">Instagram iamnishaguragain</p>\
        </a>\
    </li>';


    return creatorTemplate;

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
    var popular_cat_heading_template='<div class="_explore_feed_header"><div class="jsx-2836840237 _card_header_"><a class="jsx-2836840237" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_cover" style="background-image: url('+itemCategory.category_image+');"></div></a><a title="#'+itemCategory.slug+'('+itemCategory.total_view+' views)" class="jsx-2836840237 _card_header_link" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_content"><h3 class="jsx-2836840237 _card_header_title">'+itemCategory[category_title]+'</h3><strong class="jsx-2836840237 _card_header_subTitle">'+itemCategory.total_view+' views</strong></div></a><p class="jsx-2836840237 _card_header_desc_follow"><span class="unit"><button onclick="follow_category_discover('+itemCategory.id+');" class="_4jy1 _4jy4 _517h _51sy _42ft " style="float: none;" type="button" value="1"><i alt="" class="_3-8_ img sp_66mIw9cKlB9 followCategoryStatus-'+itemCategory.id+' followCheckCat sx_5da455"></i><span class="btnTextChangeCat-'+itemCategory.id+'">'+follow_trans+'</span></button></span></p></div></div>';
    return popular_cat_heading_template;
}

function popularCategoryItem(itemVideoByte){
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(itemVideoByte.title);
        content_title = videoTitle.substr(0, 40) + " ..."

    var category_item_template='<div class="jsx-1410658769 _explore_feed_card_item" onClick="openVideoInPopup('+itemVideoByte.id+');" ><div class="jsx-1410658769 _ratio_"><div class="jsx-1410658769" style="padding-top: 148.148%;"><div class="jsx-1410658769 _ratio_wrapper"><a href="javascript:void(0)"><div class="jsx-1464109409 image-card" style="border-radius: 4px; background-image: url('+itemVideoByte.question_image+');"><div class="jsx-3077367275 video-card default"><div class="jsx-3077367275 video-card-mask"><div class="jsx-1633345700 card-footer normal no-avatar"><div class="jsx-1633345700"><p class="video_card_title">'+content_title+'</p><p><span class="_video_card_footer_likes">'+itemVideoByte.view_count+'</span></p><span class="_video_card_footer_likes1"><img src="/media/download.svg" alt="likes"> '+itemVideoByte.likes_count+'</span></div></div></div></div></div></a></div></div></div></div>';
    return category_item_template;
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

        //var videoCommentList=data.results;
        }
  
    });

}


jQuery(document).ready(function(){
    followLikeList();

});





