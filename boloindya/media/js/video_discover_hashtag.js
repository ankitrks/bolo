var userLikeAndUnlike=[];
var current_video_play_index=0;
var totalDataCount=0;

var playlistWithIndex=[];
var videoItemCountIndex=-1;

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
var muteStatus=false;
var isLoading = false;
var hideErrorMsg = true;

var retryCount=0;
function video_play_using_video_js(url,backup_url,image) {
    
    var video = document.getElementById('player');

      if(Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource(backup_url);
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
        video.src = url;
        video.addEventListener('loadedmetadata',function() {
          video.play();
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

function openVideoInPopup(topicId){
  loaderShow();

  var singleItemData=topicList[topicId];
  $("#indexId").val(singleItemData.id);
  var videoFileName=singleItemData.video_cdn;
  var videoFileImage=singleItemData.question_image;
  $("#modelPopup").show();

  var newSrc='/media/mute_icon.svg';
  $('#mutedImageId').attr('src', newSrc);
    $('.videoPlayButton').removeClass('play-button');
    var preBufferDone = false;
    var preBufferDone = false;
    var video_backup="";
    var video_backup=singleItemData.question_video;
    var video_cdn=singleItemData.video_cdn;
    //var video_backup=singleItemData.question_video;
    video_play_using_video_js(video_cdn,video_backup,videoFileImage);      

    var shareURL=site_base_url+singleItemData.slug+'/'+singleItemData.id+'';

    $("#previousVideoId").val(indexId);
    $("#nextVideoId").val(indexId);
    $('.backgroundImg').css("background-image", "url(" + videoFileImage + ")");
    if(current_video_play_index>0){
        $('.arrow-left').removeClass('hide');
    }else{
        $('.arrow-left').removeClass('hide');
        $('.arrow-left').addClass('hide');
    }

    totalDataCount=playlistWithIndex.length-1;
    if(current_video_play_index>=totalDataCount){
        $('.arrow-right').removeClass('hide');
        $('.arrow-right').addClass('hide');
    }

    var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
        $("#topicID").val(singleItemData.id);
        $("#currentPlayUserId").val(singleItemData.user.userprofile.id);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("#shareInputbox").val(shareURL);
        var bigCommentLikeDet='<strong><span id="likeCountId">'+singleItemData.likes_count+'</span> '+likeTrans+' · <span id="commentCountId">'+singleItemData.comment_count+'</span> '+commentsTrans+'</strong>';
        $("#sideBarId").html(sideBarDetails);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("._video_card_big_meta_info_count").html(bigCommentLikeDet);
        $(".video-meta-title").html(singleItemData.title);

        $(".like-text").html(singleItemData.likes_count);
        $(".comment-text").html(singleItemData.comment_count);

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
        $("#profileImageUserId1").attr("src", profilePics);
        $("#profileImageUserId").css("background-image", "url(" + profilePics + ")");
        $(".shareandliketabprofileimage").attr("src", ""+profilePics+"");
        $(".userProfileURL").attr("href", ""+profileURL+"");
        $(".user-username").html(userprofileName);

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


    var page = 1;
    var checkDataStatus=1;
    var checkDataStatusCat=1;
    var userLikeAndUnlike=[];
    var totalCountVideo =0;
    var playListData=[];
    var nextpageURlVal="";
    $(window).scroll(function() {
        var scorh=Number($(window).scrollTop() + $(window).height());
        if($(window).scrollTop() + $(window).height() > Number($("#categoryIdList").height()+440)){
            //var nextpageURlVal=$("#nextpageURLId").val();
            nextpageURlVal=document.getElementById('nextpageURLId').value;
            if(checkDataStatusCat==0 && nextpageURlVal!="" && nextpageURlVal!=undefined){
                page++;
                loaderBoloShowDynamic('_scroll_load_more_loading_left');
                getLoadMoreHashWithVideos(nextpageURlVal);
            }

        }
    });


$(document).ready(function(){
    getCategoryWithVideos();
    //getHashTagList();
});

var topicList=[];

function getHashTagList(){

    loaderBoloShowDynamic('_scroll_load_more_loading_right');
    loaderBoloShowDynamic('_scroll_load_more_loading_left');
        var playListData=[]; 
    var platlistItems;

    var listItems="";
    var itemCount=0;
    var language_id=1;
    var page_size=10;
    var page=1;
    var uri='/api/v1/get_hash_discover/';
    var res = encodeURI(uri);
    var category_with_video_list="";
    language_id=current_language_id;

    jQuery.ajax({
        url:res,
        type:"GET",
        crossDomain: true,
        data:{'language_id':language_id,'is_expand':'True','page_size':page_size,'page':page},
        success: function(response,textStatus, xhr){
            populaCreatorsItems="";
            var populaCategoriesItems="";
            var populvideoItems="";
            var itemCount=0;
            //var responseData=response.category_details;
            var responseData=response.results;
            var hashtagVideoCall=0;
            var hashtagIds = [];

            responseData.forEach(function(itemCategory) {itemCount++;hashtagVideoCall++;
                populaCreatorsItems =popularCategoryHeading(itemCategory);
                populvideoItems="";
                //var topicData=itemCategory.topics;
                var hashTagId=itemCategory.tongue_twister.id;
                hashtagIds.push(hashTagId);
                populvideoItems+='<div class="_explore_feed_card">';
                var videoItemCount=0;
                if(hashtagVideoCall==2){
                    hashtagVideoCall=0;
                    var hashtagVideoList=getHashTagVideoList(hashtagIds);
                    if( hashtagVideoList!="" && hashtagVideoList!=undefined){
                        hashtagVideoList.forEach(function(itemVideoByte){videoItemCount++;
                            if(videoItemCount<4){
                                videoItemCountIndex++;
                                topicList[itemVideoByte.id]=itemVideoByte;
                                populvideoItems +=popularCategoryItem(itemVideoByte);
                                playlistWithIndex[videoItemCountIndex]=itemVideoByte;
                            }
                        });
                    }
                    hashtagIds =[];
                }
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
            var nextPage= response.next;
            if(nextPage){
                $("#nextpageURLId").val(nextPage);
                checkDataStatusCat=0;
            }
            followLikeList();

        },
        error: function(jqXHR, ajaxOptions, thrownError) {
            console.log(jqXHR);
           loaderBoloHideDynamic('_scroll_load_more_loading_left');
           loaderBoloHideDynamic('_scroll_load_more_loading_right');

        }

  
    });

}
//getHashTagVideoList(233);
function getHashTagVideoList(hashTagId){

    var listItems="";
    var itemCount=0;
    var language_id=1;
    var page_size=10;
    var page=1;
    var hashTagIds = hashTagId.join(",");
    //var hashTagIds='1614,1817';
    //var uri='/api/v1/get_popular_hash_tag/?hashtag_ids='+hashTagIds;
    var category_with_video_list="";
    language_id=current_language_id;
    var uri='/api/v1/get_popular_hash_tag/?hashtag_ids='+hashTagIds+"&language_id="+language_id;
    var res = encodeURI(uri);
    $.get(res, function (data, textStatus, jqXHR) {
        var dataList=data.results;

        if(dataList){
            dataList.forEach(function(itemVideoByte1){
               var populvideoItems ="";
               var topicListq=itemVideoByte1.topics;
               var videoItemCount=0;
                topicListq.forEach(function(itemVideoByte){videoItemCount++; 
                    if(videoItemCount<5){
                        videoItemCountIndex++;
                        topicList[itemVideoByte.id]=itemVideoByte;
                        populvideoItems +=getPopularHashTagItems(itemVideoByte);
                        playlistWithIndex[videoItemCountIndex]=itemVideoByte;
    			         if(populvideoItems!='undefined'){
                            $("#"+itemVideoByte1.id).html(populvideoItems);
                            //return populvideoItems;
    			         }
                    }
                });
            });
        }


    });
}



function getCategoryWithVideos(){
    loaderBoloShowDynamic('_scroll_load_more_loading_right');
    loaderBoloShowDynamic('_scroll_load_more_loading_left');
    var playListData=[]; 
    var platlistItems;

    var listItems="";
    var itemCount=0;
    var language_id=1;
    var page_size=10;
    var page=1;
    //var uri='/api/v1/get_popular_hash_tag/';
    var uri='/api/v1/get_hash_discover/';
    var res = encodeURI(uri);
    var category_with_video_list="";
    language_id=current_language_id;

    jQuery.ajax({
        url:res,
        type:"GET",
        dataType:'json',
        data:{'language_id':language_id,'is_with_popular':'True','popular_boloindyans':'True','page_size':page_size,'page':page},
        success: function(response,textStatus, xhr){
            populaCreatorsItems="";
            var populaCategoriesItems="";
            var populvideoItems="";
            var itemCount=0;
            var hashtagIds=[];
            var hashtagVideoCall=0;
            //var responseData=response.category_details;
            var responseData=response.results;
            responseData.forEach(function(itemCategory) {itemCount++;hashtagVideoCall++;
                //populaCreatorsItems =popularCategoryHeading(itemCategory);
                populaCreatorsItems =popularHashtagHeading(itemCategory);
                populvideoItems="";
                var topicData=itemCategory.topics;
                var videoItemCount=0;
                var hashTagId=itemCategory.tongue_twister.id;
                hashtagIds.push(hashTagId);
		populvideoItems+='<div class="_explore_feed_card" id="'+hashTagId+'">';
                if(hashtagVideoCall==2){
                    hashtagVideoCall=0;
		    var tempData =getHashTagVideoList(hashtagIds);
		   if(tempData!=undefined){
		     populvideoItems += getHashTagVideoList(hashtagIds);
		   }
                    hashtagIds =[];
                }
                populvideoItems+='</div>';
                category_with_video_list='<div class="_explore_feed_item">'+populaCreatorsItems+''+populvideoItems+'</div>';
                $("#catWithVideoId").append(category_with_video_list);
                // if(itemCount % 2 == 0) {
                //     loaderBoloHideDynamic('_scroll_load_more_loading_right');
                //     $("#catWithVideoIdRight").append(category_with_video_list);
                // }else{
                //      loaderBoloHideDynamic('_scroll_load_more_loading_left');
                //     $("#catWithVideoId").append(category_with_video_list);
                // }

            });
            var nextPage= response.next;
            if(nextPage){
                $("#nextpageURLId").val(nextPage);
                checkDataStatusCat=0;
            }
            loaderBoloHideDynamic('_scroll_load_more_loading_left');
            loaderBoloHideDynamic('_scroll_load_more_loading_right');
            followLikeList();

        },
        error: function(jqXHR, ajaxOptions, thrownError) {
            console.log(jqXHR);
           loaderBoloHideDynamic('_scroll_load_more_loading_left');
           loaderBoloHideDynamic('_scroll_load_more_loading_right');

        }/*  end of error */

  
    });
}

function getLoadMoreHashWithVideos(nextPageURL){
    //loaderBoloShowDynamic('_scroll_load_more_loading_right');
    loaderBoloShowDynamic('_scroll_load_more_loading_left');
    var playListData=[]; 
    var platlistItems;
    checkDataStatusCat=1;

    var listItems="";
    var itemCount=0;
    var language_id=1;

    var page_size=2;
    var uri=nextPageURL;
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
            //var responseData=response.category_details;
            var responseData=response.results;
            responseData.forEach(function(itemCategory) {itemCount++;
                populaCreatorsItems =popularCategoryHeading(itemCategory);
                populvideoItems="";
                var topicData=itemCategory.topics;
                populvideoItems+='<div class="_explore_feed_card">';
                var videoItemCount=0;
                topicData.forEach(function(itemVideoByte){videoItemCount++;
                    if(videoItemCount<4){
                        videoItemCountIndex++;
                        topicList[itemVideoByte.id]=itemVideoByte;
                        populvideoItems +=popularCategoryItem(itemVideoByte);
                        playlistWithIndex[videoItemCountIndex]=itemVideoByte;
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
            var nextPage= response.next;
            if(nextPage){
                $("#nextpageURLId").val(nextPage);
                checkDataStatusCat=0;
            }
            loaderBoloHideDynamic('_scroll_load_more_loading_left');
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




    function previousVideoPlay(){
        loaderShow();
        var singleItemData=[];
        current_video_play_index=current_video_play_index-1;

        //$("#indexId").val(current_video_play_index);

        $("#modelPopup").show();
        //jwplayer('player').setMute(false);
        pouseButton(video);
        var indexId=current_video_play_index;
        var newSrc='/media/mute_icon.svg';
        $('#mutedImageId').attr('src', newSrc);
        //$('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
        $('.videoPlayButton').removeClass('play-button');
        singleItemData=playlistWithIndex[indexId];
        var preBufferDone = false;
        var video_backup="";
        var video_backup=singleItemData.question_video;
        var file=singleItemData.video_cdn;
        var image=singleItemData.question_image;
        $("#indexId").val(singleItemData.id);
        video_play_using_video_js(file,video_backup,image);
        $('.backgroundImg').css("background-image", "url(" + image + ")");
        if(current_video_play_index>0){
            $('.arrow-left').removeClass('hide');
        }else{
            $('.arrow-left').removeClass('hide');
            $('.arrow-left').addClass('hide');
        }

        totalDataCount=playlistWithIndex.length;
        if(current_video_play_index==totalDataCount){
            $('.arrow-right').removeClass('hide');
            $('.arrow-right').addClass('hide');
        }


          
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

            $(".like-text").html(singleItemData.likes_count);
            $(".comment-text").html(singleItemData.comment_count);

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
           $("#profileImageUserId1").attr("src", profilePics);
            $("#profileImageUserId").css("background-image", "url(" + profilePics + ")");
            $(".shareandliketabprofileimage").attr("src", ""+profilePics+"");
            $(".userProfileURL").attr("href", ""+profileURL+"");
            $(".user-username").html(userprofileName);
            $("._video_card_big_user_info_nickname").html(userprofileName);
            $("._video_card_big_user_info_handle").html(userHandleName);
            $(".user-nickname").html(userHandleName);
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

    function nextVideoPlay(){
        loaderShow();
        var singleItemData=[];

        current_video_play_index=current_video_play_index+1;

        $("#indexId").val(current_video_play_index);

        $("#modelPopup").show();
        //jwplayer('player').setMute(false);
        pouseButton(video);
        var newSrc='/media/mute_icon.svg';
        $('#mutedImageId').attr('src', newSrc);
        //$('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
        $('.videoPlayButton').removeClass('play-button');
        var indexId=current_video_play_index;
        singleItemData=playlistWithIndex[indexId];
        $("#indexId").val(singleItemData.id);
        var preBufferDone = false;
        var video_backup="";
        var video_backup=singleItemData.question_video;
        var file=singleItemData.video_cdn;
        var image=singleItemData.question_image;
        video_play_using_video_js(file,video_backup,image);
        $('.backgroundImg').css("background-image", "url(" + image + ")");
        if(current_video_play_index>0){
            $('.arrow-left').removeClass('hide');
        }else{
            $('.arrow-left').removeClass('hide');
            $('.arrow-left').addClass('hide');
        }

        totalDataCount=playlistWithIndex.length;
        if(current_video_play_index==totalDataCount){
            $('.arrow-right').removeClass('hide');
            $('.arrow-right').addClass('hide');
        }


          
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

            $(".like-text").html(singleItemData.likes_count);
            $(".comment-text").html(singleItemData.comment_count);

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
           $("#profileImageUserId1").attr("src", profilePics);
            $("#profileImageUserId").css("background-image", "url(" + profilePics + ")");
            $(".shareandliketabprofileimage").attr("src", ""+profilePics+"");
            $(".userProfileURL").attr("href", ""+profileURL+"");
            $(".user-username").html(userprofileName);
            $("._video_card_big_user_info_nickname").html(userprofileName);
            $("._video_card_big_user_info_handle").html(userHandleName);
            $(".user-nickname").html(userHandleName);
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

    function delegetPlayStatus() {
        var video = document.getElementById('player');
        if (video.paused) {
            var newSrc='/media/mute_icon.svg';
            $('#mutedImageId').attr('src', newSrc);
            $('.videoPlayButton').removeClass('play-button');
            playButton(video);
        }
        else {
            $('.videoPlayButton').removeClass('play-button');
            $('.videoPlayButton').addClass('play-button');
            
            pouseButton(video);
        }
    }

    function pouseButton(video){
        $("#player").trigger('pause');
    }
    function playButton(video){
        $("#player").trigger('play');
    }

function muteAndUnmutePlayer1(){

    if($("video").prop('muted')){

      $("video").prop('muted', false);
        $("#mutedImageId").removeClass('muted');
    }else{
        $("video").prop('muted', true);
        $("#mutedImageId").removeClass('muted');
        $("#mutedImageId").addClass('muted');
    }
}

//==================== Hashtag Heading ==================

function popularHashtagHeading(itemCategory){

    var category_title='';
    currentLanguageName=current_language_name.toLowerCase();
    if(currentLanguageName!='english'){
        category_title=currentLanguageName+'_title';
    }else{
        category_title='title';
    }
    //style="background-image: url('+image+');"
    var itemHashtag=itemCategory.tongue_twister;
    var image ='/media/hashtag_black.svg';
    var popular_cat_heading_template='<div class="_explore_feed_header"><div class="jsx-2836840237 _card_header_"><a title="#'+itemHashtag.hash_tag+'('+itemCategory.total_views+' views)" class="jsx-2836840237 _card_header_link" href="/hashtag/'+itemHashtag.hash_tag+'/"><div class="jsx-2836840237 _card_header_content"><h3 class="jsx-2836840237 _card_header_title">#'+itemHashtag.hash_tag+'</h3><strong class="jsx-2836840237 _card_header_subTitle"></strong></div></a></div></div>';
    return popular_cat_heading_template;
}



//=========================== End =======================







function popularCategoryHeading(itemCategory){


    var category_title;
    currentLanguageName=current_language_name.toLowerCase();
    if(currentLanguageName!='english'){
        category_title=currentLanguageName+'_title';
    }else{
        category_title='title';
    }
    var image ='/media/hashtag_black.svg';
    var popular_cat_heading_template='<div class="_explore_feed_header"><div class="jsx-2836840237 _card_header_"><a class="jsx-2836840237" href="/hashtag/'+itemCategory.hash_tag+'/"><div class="jsx-2836840237 _card_header_cover" style="background-image: url('+image+');"></div></a><a title="#'+itemCategory.hash_tag+'('+itemCategory.total_views+' views)" class="jsx-2836840237 _card_header_link" href="/hashtag/'+itemCategory.hash_tag+'/"><div class="jsx-2836840237 _card_header_content"><h3 class="jsx-2836840237 _card_header_title">'+itemCategory.hash_tag+'</h3><strong class="jsx-2836840237 _card_header_subTitle">'+itemCategory.total_views+' views</strong></div></a></div></div>';
    return popular_cat_heading_template;
}
function popularCategoryHeadingOld(itemCategory){

    var category_title;
    currentLanguageName=current_language_name.toLowerCase();
    if(currentLanguageName!='english'){
        category_title=currentLanguageName+'_title';
    }else{
        category_title='title';
    }
    var popular_cat_heading_template='<div class="_explore_feed_header"><div class="jsx-2836840237 _card_header_"><a class="jsx-2836840237" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_cover " style="background-image: url('+itemCategory.category_image+');"></div></a><a title="#'+itemCategory.slug+'('+itemCategory.total_view+' views)" class="jsx-2836840237 _card_header_link" href="/tag/'+itemCategory.slug+'/"><div class="jsx-2836840237 _card_header_content"><h3 class="jsx-2836840237 _card_header_title">'+itemCategory[category_title]+'</h3><strong class="jsx-2836840237 _card_header_subTitle">'+itemCategory.total_view+' views</strong></div></a><p class="jsx-2836840237 _card_header_desc_follow"><span class="unit"><button onclick="follow_category_discover('+itemCategory.id+');" class="_4jy1 _4jy4 _517h _51sy _42ft " style="float: none;" type="button" value="1"><i alt="" class="_3-8_ img sp_66mIw9cKlB9 followCategoryStatus-'+itemCategory.id+' followCheckCat sx_5da455"></i><span class="btnTextChangeCat-'+itemCategory.id+'">'+follow_trans+'</span></button></span></p></div></div>';
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

function getPopularHashTagItems(itemVideoByte) {
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(itemVideoByte.title);
        content_title = videoTitle.substr(0, 10) + " ..."

    var popularHashTagTemplateItems ='<div class="column " style="cursor: pointer;">\
                            <div class="card" onClick="openVideoInPopup('+itemVideoByte.id+');" style="background-color: #fff; padding: 20px;">\
                            <span id="video_play_item_'+itemVideoByte.id+'" class="min-span-height">\
                                <img  id="player-'+itemVideoByte.id+'" src="'+itemVideoByte.question_image+'" class="videoCentered videoSliderPlay">\
                            </span>\
                                <div class="card-body videoRowCardBody" style="">\
                                    <div>\
                                        <h5 class="title"></h5>\
                                        <p class="desc">'+content_title+'</p>\
                                    </div>\
                                    <div style="display: inline-flex; justify-content: space-between;">\
                                        <div style="margin-right: 10px;">\
                                            <a href="#">\
                                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <path d="M17 4.5C14.9 4.5 13.05 5.55 12 7.2C10.95 5.55 9.1 4.5 7 4.5C3.7 4.5 1 7.2 1 10.5C1 16.45 12 22.5 12 22.5C12 22.5 23 16.5 23 10.5C23 7.2 20.3 4.5 17 4.5Z" fill="#ccc"></path>\
                                                </svg>\
                                            </a>\
                                        </div>\
                                        <div style="margin-right: 10px;">\
                                            <a href="#">\
                                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <g clip-path="url(#clip0)">\
                                                        <path\
                                                            d="M11.9999 1.5C5.37181 1.5 -6.28186e-05 5.86406 -6.28186e-05 11.25C-6.28186e-05 13.4812 0.93275 15.525 2.47962 17.1703C1.78119 19.0172 0.328062 20.5828 0.304625 20.6016C-0.00475032 20.9297 -0.0891253 21.4078 0.0889997 21.8203C0.267125 22.2328 0.674937 22.5 1.12494 22.5C4.00775 22.5 6.28119 21.2953 7.64525 20.3297C8.99994 20.7563 10.4624 21 11.9999 21C18.6281 21 23.9999 16.6359 23.9999 11.25C23.9999 5.86406 18.6281 1.5 11.9999 1.5ZM11.9999 18.75C10.7484 18.75 9.51088 18.5578 8.32494 18.1828L7.26087 17.8453L6.34681 18.4922C5.6765 18.9656 4.75775 19.4953 3.6515 19.8516C3.99369 19.2844 4.3265 18.6469 4.58431 17.9672L5.08119 16.65L4.11556 15.6281C3.26712 14.7234 2.24994 13.2281 2.24994 11.25C2.24994 7.11563 6.62337 3.75 11.9999 3.75C17.3765 3.75 21.7499 7.11563 21.7499 11.25C21.7499 15.3844 17.3765 18.75 11.9999 18.75Z" fill="#545454"></path>\
                                                    </g>\
                                                    <defs>\
                                                        <clipPath id="clip0">\
                                                            <rect width="24" height="24" fill="white"></rect>\
                                                        </clipPath>\
                                                    </defs>\
                                                </svg>\
                                            </a>\
                                        </div>\
                                        <div>\
                                            <a href="#">\
                                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <path d="M3 12C3 13.654 4.346 15 6 15C6.794 15 7.512 14.685 8.049 14.18L14.04 17.604C14.022 17.734 14 17.864 14 18C14 19.654 15.346 21 17 21C18.654 21 20 19.654 20 18C20 16.346 18.654 15 17 15C16.206 15 15.488 15.315 14.951 15.82L8.96 12.397C8.978 12.266 9 12.136 9 12C9 11.864 8.978 11.734 8.96 11.603L14.951 8.18C15.488 8.685 16.206 9 17 9C18.654 9 20 7.654 20 6C20 4.346 18.654 3 17 3C15.346 3 14 4.346 14 6C14 6.136 14.022 6.266 14.04 6.397L8.049 9.82C7.496 9.29468 6.76273 9.00123 6 9C4.346 9 3 10.346 3 12Z" fill="#545454"></path>\
                                                </svg>\
                                            </a>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>\
                        </div>';

    return popularHashTagTemplateItems
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





