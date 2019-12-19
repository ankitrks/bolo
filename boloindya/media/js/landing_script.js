    var page = 1;
    var checkDataStatus=0;
    var userLikeAndUnlike=[];
    $(window).scroll(function() {
        var scorh=Number($(window).scrollTop() + $(window).height());
        console.log('Scol+he '+scorh);
        //if($(window).scrollTop() + $(window).height() >= $(document).height()-800 && $(window).scrollTop() + $(window).height()<$(document).height()) {
           
        if($(window).scrollTop() + $(window).height() > $("#playlist").height()){

            if(checkDataStatus==0){
                page++;
                loadMoreData(page);
            }

        }
        console.log('documentHe- '+$(document).height());
    });

    function loadMoreData(page){
    var playListData=[]; 
    var platlistItems;
    checkDataStatus=1;

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
            playListData=topicVideoList;
            var itemCount=-1;
            topicVideoList.forEach(function(itemVideo) {itemCount++;
              var isPlaying="";
              var isPlayIconDis="none";
              if(itemCount==1){
                isPlaying='is-playing';
                isPlayIconDis="block";
              }

            listItems +='<div class="_video_feed_item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+itemCount+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><span class="_avatar_ _avatar_respond" style="background-image: url('+itemVideo.question_image+');"></span><span class="_video_card_footer_likes"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>';
            });

                $('.ajax-load').hide();
                $("#playlist").append(listItems);
            })
            .fail(function(jqXHR, ajaxOptions, thrownError)
            {
                if(jqXHR.status!=201){

                }

                  $('.ajax-load').html("No more records found");
            });
    }

$(window).scroll(function () {
    // End of the document reached?
    console.log($(document).height() - $(this).height()-600);
    if ($(document).height() - $(this).height()-600 == $(this).scrollTop()) {
        //getElementsByPage(page);
        //console.log('ad');
       // console.log($(this).scrollTop());
    }
    console.log('scroll'+$(this).scrollTop())
}); 

     var language_id=current_language_id;
    var playListData=[]; 
    var platlistItems;
    (function() {
        var listItems="";
        var itemCount=0;

        var uri='/api/v1/get_popular_video_bytes/?page=1&language_id='+language_id;
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

              listItems +='<div class="_video_feed_item"><div class="_ratio_"><div style="padding-top: 148.148%;"><div class="_ratio_wrapper"><a onClick="openVideoInPopup(\''+itemVideo.video_cdn+'\',\''+itemVideo.question_image+'\','+itemCount+');"  class="js-video-link playlist-item '+isPlaying+'" data-mediaid="'+itemVideo.id+'"  href="javascript:void(0);"><div class="_image_card_" style="border-radius: 4px; background-image: url('+itemVideo.question_image+');"><div class="_video_card_play_btn_ _video_card_play_btn_dark _image_card_playbtn_wraaper"></div><div class="_video_card_footer_ _video_card_footer_respond _image_card_footer_wraaper"><span class="_avatar_ _avatar_respond" style="background-image: url('+itemVideo.question_image+');"></span><span class="_video_card_footer_likes"><img src="/media/download.svg" alt="likes"> '+itemVideo.likes_count+'</span></div></div></a></div></div></div></div>'; 

            });
            $("#playlist").append(listItems);
            $("_scroll_load_more_loading").append(listItems);
            
        });


    })();



    $("figure").mouseleave(
      function () {
        $(this).removeClass("hover");
      }
    );
    

    var sideBarDetails="";
    var sideBarCommentDetails="";

    function openVideoInPopup(file,image,indexId){
        loaderShow();
        var singleItemData=[];
        $("#indexId").val(indexId);

        $("#modelPopup").show();
        jwplayer('player').setMute(false);
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

        });

        playerInstance.on('complete', function() {
        jwplayer('player').setMute(true);
        });

        singleItemData=playListData[indexId];
        console.log(singleItemData);
        var shareURL='/'+singleItemData.user.username+'/'+singleItemData.id+'';
        var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
            $("#topicID").val(singleItemData.id);
            $("#currentPlayUserId").val(singleItemData.user.userprofile.id);

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
                                jQuery('.btnTextChangePopup').text('Followed');
                            }else{
                                jQuery('.followStatusChangePopup').removeClass('sx_5da456');
                                jQuery('.followStatusChangePopup').addClass('sx_5da455');
                                jQuery('.btnTextChangePopup').text('Follow');
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
                var likeTxt="Like";
                

                var likeStatusClass=jQuery(".likeStatusInfo").hasClass('liked');
                if(likeStatusClass==true){
                    jQuery(".likeStatusInfo").removeClass('liked');
                }

                if(undefined != userLikeAndUnlike.comment_like){debugger;
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



