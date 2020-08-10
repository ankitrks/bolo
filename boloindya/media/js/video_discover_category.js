
$(document).ready(function(){
    getCategoryVideos();
    getSideBarData();
});





var page = 1;
var checkDataStatus=0;
var userLikeAndUnlike=[];
var totalCountVideo =0;
var playListData=[];
var current_video_play_index=0;
var totalDataCount=0;

var playlistWithIndex=[];
var videoItemCount=-1;

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
            //var itemCount=0;
            videoItemList.forEach(function(itemCreator) {videoItemCount++;
                playListData[itemCreator.id]=itemCreator;
                userVideoItems +=videoItemsTemplate(itemCreator,itemCreator.id,videoItemCount);
                //userVideoItems +=getVideoItem(itemCreator,itemCreator.id,videoItemCount);
                playlistWithIndex[videoItemCount]=itemCreator;
            });
            $("#categoryVideosListId").append(userVideoItems);
            loaderBoloHideDynamic('_scroll_load_more_loading_user_videos');
            //playListData=videoItemList;

        }
  
    });
}


var playlistWithIndex=[];
var videoItemCount=0;
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
            var userVideoItems="";
            videoItemList.forEach(function(itemCreator) {videoItemCount++;
                if(itemCreator!=""){
                    playListData[itemCreator.id]=itemCreator;
                    playlistWithIndex[videoItemCount]=itemCreator;
                    //userVideoItems +=getVideoItem(itemCreator,itemCreator.id,videoItemCount);
                    userVideoItems +=videoItemsTemplate(itemCreator,itemCreator.id,videoItemCount);
                }
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




function getVideoItem(videoItem,itemCount,indexCount){
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(videoItem.title);
        content_title = videoTitle.substr(0, 40) + " ...";
    var userVideoItem = '<div class="jsx-1410658769 video-feed-item">\
            <div class="jsx-1410658769 _ratio_">\
                <div class="jsx-1410658769" style="padding-top: 148.438%;">\
                    <div class="jsx-1410658769 _ratio_wrapper">\
                        <a href="javascript:void(0)" onClick="openVideoInPopup(\''+videoItem.question_video+'\',\''+videoItem.question_image+'\','+itemCount+','+indexCount+');" class="jsx-2893588005 video-feed-item-wrapper">\
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

function videoItemsTemplate(itemVideoByte,itemCount,indexCount) {
    var content_title="";
    var videoTitle="";
        videoTitle=removeTags(itemVideoByte.title);
        content_title = videoTitle.substr(0, 10) + " ..."


    var popularHashTagTemplateItems ='<div class="column " style="cursor: pointer;">\
                            <div class="card"  style="background-color: #fff; padding: 20px;">\
                            <span onClick="openVideoInPopup(\''+itemVideoByte.video_cdn+'\',\''+itemVideoByte.question_image+'\','+itemCount+','+indexCount+');" id="video_play_item_'+itemVideoByte.id+'" class="min-span-height">\
                                <img  id="player-'+itemVideoByte.id+'" src="'+itemVideoByte.question_image+'" class="videoCentered videoSliderPlay">\
                            </span>\
                                <div class="card-body videoRowCardBody" style="">\
                                    <div>\
                                        <h5 class="title">'+content_title+'</h5>\
                                        <p class="desc descByName">'+itemVideoByte.user.userprofile.name+'</p>\
                                    </div>\
                                    <div style="display: inline-flex; justify-content: space-between;">\
                                        <div style="margin-right: 10px;">\
                                            <a href="#">\
                                                <svg width="24" height="24" viewBox="0 0 26 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13 0.720001C4.4707 0.720001 0 7.0016 0 8C0 8.9958 4.4707 15.28 13 15.28C21.528 15.28 26 8.9958 26 8C26 7.0016 21.528 0.720001 13 0.720001ZM13 13.5991C9.8085 13.5991 7.2215 11.0927 7.2215 8C7.2215 4.9073 9.8085 2.3983 13 2.3983C16.1915 2.3983 18.7772 4.9073 18.7772 8C18.7772 11.0927 16.1915 13.5991 13 13.5991ZM13 8C12.4709 7.4189 13.8619 5.1998 13 5.1998C11.4036 5.1998 10.1101 6.4543 10.1101 8C10.1101 9.5457 11.4036 10.8002 13 10.8002C14.5951 10.8002 15.8899 9.5457 15.8899 8C15.8899 7.2889 13.4498 8.4927 13 8Z" fill="#545454"></path></svg>\
                                            </a>\
                                            <span class="viewCounterCssBig">'+itemVideoByte.view_count+'</span>\
                                        </div>\
                                        <div style="margin-right: 10px;">\
                                            <a href="javascript:void(0);" onclick="UReactionLinkLanding('+itemVideoByte.id+');">\
                                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <path class="likeStatusNotUpdate" id="path-'+itemVideoByte.id+'" d="M17 4.5C14.9 4.5 13.05 5.55 12 7.2C10.95 5.55 9.1 4.5 7 4.5C3.7 4.5 1 7.2 1 10.5C1 16.45 12 22.5 12 22.5C12 22.5 23 16.5 23 10.5C23 7.2 20.3 4.5 17 4.5Z" fill="#ccc"></path>\
                                                </svg>\
                                            </a>\
                                            <span class="viewCounterCssBig">'+itemVideoByte.likes_count+'</span>\
                                        </div>\
                                        <div>\
                                            <a href="javascript:void(0)" onclick="shareOpenAndHide('+itemVideoByte.id+',\''+content_title+'\',\''+itemVideoByte.user.userprofile.name+'\');">\
                                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <path d="M3 12C3 13.654 4.346 15 6 15C6.794 15 7.512 14.685 8.049 14.18L14.04 17.604C14.022 17.734 14 17.864 14 18C14 19.654 15.346 21 17 21C18.654 21 20 19.654 20 18C20 16.346 18.654 15 17 15C16.206 15 15.488 15.315 14.951 15.82L8.96 12.397C8.978 12.266 9 12.136 9 12C9 11.864 8.978 11.734 8.96 11.603L14.951 8.18C15.488 8.685 16.206 9 17 9C18.654 9 20 7.654 20 6C20 4.346 18.654 3 17 3C15.346 3 14 4.346 14 6C14 6.136 14.022 6.266 14.04 6.397L8.049 9.82C7.496 9.29468 6.76273 9.00123 6 9C4.346 9 3 10.346 3 12Z" fill="#545454"></path>\
                                                </svg>\
                                            </a>\
                                            <span class="viewCounterCssBig">'+itemVideoByte.share_count+'</span>\
                                        </div>\
                                    </div>\
                                </div>\
                            </div>\
                        </div>';


    // var popularHashTagTemplateItems ='<div class="column " style="cursor: pointer;">\
    //                         <div class="card" onClick="openVideoInPopup(\''+itemVideoByte.video_cdn+'\',\''+itemVideoByte.question_image+'\','+itemCount+','+indexCount+');" style="background-color: #fff; padding: 20px;">\
    //                         <span id="video_play_item_'+itemVideoByte.id+'" class="min-span-height">\
    //                             <img  id="player-'+itemVideoByte.id+'" src="'+itemVideoByte.question_image+'" class="videoCentered videoSliderPlay">\
    //                         </span>\
    //                             <div class="card-body videoRowCardBody" style="">\
    //                                 <div>\
    //                                     <h5 class="title"></h5>\
    //                                     <p class="desc">'+content_title+'</p>\
    //                                 </div>\
    //                                 <div style="display: inline-flex; justify-content: space-between;">\
    //                                     <div style="margin-right: 10px;">\
    //                                         <a href="#">\
    //                                             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
    //                                                 <path d="M17 4.5C14.9 4.5 13.05 5.55 12 7.2C10.95 5.55 9.1 4.5 7 4.5C3.7 4.5 1 7.2 1 10.5C1 16.45 12 22.5 12 22.5C12 22.5 23 16.5 23 10.5C23 7.2 20.3 4.5 17 4.5Z" fill="#ccc"></path>\
    //                                             </svg>\
    //                                         </a>\
    //                                     </div>\
    //                                     <div style="margin-right: 10px;">\
    //                                         <a href="#">\
    //                                             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
    //                                                 <g clip-path="url(#clip0)">\
    //                                                     <path\
    //                                                         d="M11.9999 1.5C5.37181 1.5 -6.28186e-05 5.86406 -6.28186e-05 11.25C-6.28186e-05 13.4812 0.93275 15.525 2.47962 17.1703C1.78119 19.0172 0.328062 20.5828 0.304625 20.6016C-0.00475032 20.9297 -0.0891253 21.4078 0.0889997 21.8203C0.267125 22.2328 0.674937 22.5 1.12494 22.5C4.00775 22.5 6.28119 21.2953 7.64525 20.3297C8.99994 20.7563 10.4624 21 11.9999 21C18.6281 21 23.9999 16.6359 23.9999 11.25C23.9999 5.86406 18.6281 1.5 11.9999 1.5ZM11.9999 18.75C10.7484 18.75 9.51088 18.5578 8.32494 18.1828L7.26087 17.8453L6.34681 18.4922C5.6765 18.9656 4.75775 19.4953 3.6515 19.8516C3.99369 19.2844 4.3265 18.6469 4.58431 17.9672L5.08119 16.65L4.11556 15.6281C3.26712 14.7234 2.24994 13.2281 2.24994 11.25C2.24994 7.11563 6.62337 3.75 11.9999 3.75C17.3765 3.75 21.7499 7.11563 21.7499 11.25C21.7499 15.3844 17.3765 18.75 11.9999 18.75Z" fill="#545454"></path>\
    //                                                 </g>\
    //                                                 <defs>\
    //                                                     <clipPath id="clip0">\
    //                                                         <rect width="24" height="24" fill="white"></rect>\
    //                                                     </clipPath>\
    //                                                 </defs>\
    //                                             </svg>\
    //                                         </a>\
    //                                     </div>\
    //                                     <div>\
    //                                         <a href="#">\
    //                                             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">\
    //                                                 <path d="M3 12C3 13.654 4.346 15 6 15C6.794 15 7.512 14.685 8.049 14.18L14.04 17.604C14.022 17.734 14 17.864 14 18C14 19.654 15.346 21 17 21C18.654 21 20 19.654 20 18C20 16.346 18.654 15 17 15C16.206 15 15.488 15.315 14.951 15.82L8.96 12.397C8.978 12.266 9 12.136 9 12C9 11.864 8.978 11.734 8.96 11.603L14.951 8.18C15.488 8.685 16.206 9 17 9C18.654 9 20 7.654 20 6C20 4.346 18.654 3 17 3C15.346 3 14 4.346 14 6C14 6.136 14.022 6.266 14.04 6.397L8.049 9.82C7.496 9.29468 6.76273 9.00123 6 9C4.346 9 3 10.346 3 12Z" fill="#545454"></path>\
    //                                             </svg>\
    //                                         </a>\
    //                                     </div>\
    //                                 </div>\
    //                             </div>\
    //                         </div>\
    //                     </div>';

    return popularHashTagTemplateItems
}




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

function video_play_using_video_js(url,backup_url,image) {
    
    var video = document.getElementById('player');

    var strUrl = url;
    var backUrl = backup_url;
    url = strUrl.replace("http://", "https://");
    backup_url = backUrl.replace("http://", "https://");    
    var posterImage = image.replace("http://", "https://");
    image = posterImage.replace("http://", "https://");
    video.poster = image;
    
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



function retryLiveStream(hls, url) {
    retrying = true;
    retryCount++;
    hls.loadSource(url);
    hls.startLoad();
    loaderHide();
}


 function openVideoInPopup(file,image,indexId,indexCount){debugger;
  loaderShow();
  var singleItemData=[];
    $("#indexId").val(indexId);
    singleItemData=playListData[indexId];
    current_video_play_index=indexCount;
  $("#modelPopup").show();
  var newSrc='/media/mute_icon.svg';
  $('#mutedImageId').attr('src', newSrc);
  //$('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
  $('.videoPlayButton').removeClass('play-button');
    var preBufferDone = false;
    var video_backup="";
    var video_backup=singleItemData.question_video;
    video_play_using_video_js(file,video_backup,image);
  
    $("#previousVideoId").val(indexId);
    $("#nextVideoId").val(indexId);
    //$('.backgroundImg').css("background-image", "url(" + image + ")");
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


    var shareURL=site_base_url+singleItemData.slug+'/'+singleItemData.id+'';

    var sideBarDetails='<div onClick="openMobileDownloadPopup();" class="jsx-2177493926 jsx-3813273378 avatar round" style="background-image: url(/media/musically_100x100.jpeg); width: 48px; height: 48px; flex: 0 0 48px;"></div><div class="jsx-949708032 boloindya-toolbar" style="margin-top: 20px;"><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-like" onClick="openMobileDownloadPopup();" style="background-image: url(/media/viewIcon.svg);"><span class="jsx-949708032">'+singleItemData.likes_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-comment" onClick="openMobileDownloadPopup();" style="background-image: url(/media/comments.svg);"><span class="jsx-949708032">'+singleItemData.comment_count+'</span></div><div class="jsx-949708032 boloindya-toolbar-section boloindya-toolbar-share" onclick="openShareTab()" style="background-image: url(/media/share.svg);"><span class="jsx-949708032">'+singleItemData.total_share_count+'</span></div></div>';
        $("#topicID").val(singleItemData.id);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("#shareInputbox").val(shareURL);
        var bigCommentLikeDet='<strong><span id="likeCountId">'+singleItemData.likes_count+'</span> '+likeTrans+' · <span id="commentCountId">'+singleItemData.comment_count+'</span> '+commentsTrans+'</strong>';
        $("#sideBarId").html(sideBarDetails);
        $("#topicCreatorUsername").val(singleItemData.user.username);
        $("._video_card_big_meta_info_count").html(bigCommentLikeDet);
        $(".video-meta-title").html(singleItemData.title);

        //===================== Comment and Like count ===============
        $(".like-text").html(singleItemData.likes_count);
        $(".comment-text").html(singleItemData.comment_count);

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
        //$('.backgroundImg').css("background-image", "url(" + image + ")");
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

    function nextVideoPlay(){debugger;
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
        //$('.backgroundImg').css("background-image", "url(" + image + ")");
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


        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 likeStatusInfo '+likeStatus+' changeLikeColor-'+itemVideo.id+' "><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" href="javascript:void(0);" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

      
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



