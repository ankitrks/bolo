  jQuery('#UCommentLink').on('click',function(){
      var commentBoxInputStatus=jQuery('#commentInputId').hasClass('hide');
      if(commentBoxInputStatus==true){debugger;
         var loginStatus= check_login_status();
         if(loginStatus==false){debugger;
          if( jwplayer('player').getState() == "playing"){
              jwplayer('player').pause();
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
  });

  function downloadAppLink(){
    var appLink='';
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
      var topicId=$("#topicID").val();
      if(likeStatus==false){
         var loginStatus= check_login_status();
         if(loginStatus==false){
          if( jwplayer('player').getState() == "playing"){
              jwplayer('player').pause();
          }
          
          document.getElementById('openLoginPopup').click();
         }
         var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25c');
         if(likeStatus==true){
              jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25c');
              jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25d');
         }
 
          jQuery('#UReactionLink').addClass('liked');
          updateUserLikeStatus(topicId);
      }else{
         jQuery('#UReactionLink').removeClass('hide');
         updateUserLikeStatus(topicId);
         var likeStatus=jQuery('.sp_ddXiTdIB8vm').hasClass('sx_44a25d');
         if(likeStatus==true){
              jQuery('.sp_ddXiTdIB8vm').removeClass('sx_44a25d');
              jQuery('.sp_ddXiTdIB8vm').addClass('sx_44a25c');
              jQuery('#UReactionLink').removeClass('liked');
         }

      }
      
  });

$("#jwBox").click(function(){
  var plaerState=jwplayer('player').getState();

  if( jwplayer('player').getState() == "playing" || jwplayer(this).getState() == "buffering" ) {
          jwplayer('player').pause();
          $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
          $('.videoPlayButton').addClass('_video_card_playbtn_wraaper');
          
      }else{
        var newSrc='/media/mute_icon.svg';
        $('#mutedImageId').attr('src', newSrc);
        jwplayer('player').play(true);
        jwplayer('player').setMute(false);
        $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
      }
  
});

$('.videoPlayButton').click(function(){
      var newSrc='/media/mute_icon.svg';
      $('#mutedImageId').attr('src', newSrc);
      $('.videoPlayButton').removeClass('_video_card_playbtn_wraaper');
      jwplayer('player').setMute(false);
      jwplayer('player').play(true);
});

function social_share(shareType){
    check_login_status();
    var topicId=$("#topicID").val();
    var topicCreatorUsername=$("#topicCreatorUsername").val();
    var shareURL="";
    if(shareType=='facebook_share'){

        shareURL='https://www.facebook.com/sharer/sharer.php?app_id=113869198637480&u=https://www.boloindya.com/'+topicCreatorUsername+'/'+topicId+'&display=popup&sdk=joey/';

    }else if(shareType=='twitter_share'){

        shareURL='https://twitter.com/intent/tweet?text=https://www.boloindya.com/'+topicCreatorUsername+'/'+topicId+'/&url=https://www.boloindya.com/'+topicCreatorUsername+'/'+topicId+'/'
    }else if(shareType=='whatsapp_share'){
        shareURL='https://api.whatsapp.com/send?text=https://www.boloindya.com/'+topicCreatorUsername+'/'+topicId+'/';
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
    //$('input[name = butAssignProd]').click();
      
  }
});


    function create_comment(inputComment){

        check_login_status();
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

        var topicID = document.getElementById('topicID').value;
        var elem = document.getElementById('some_div');
        var data=[];
        data.push({name: 'topic_id', value: topicID});
        data.push({name: 'language_id', value: language_id});
        data.push({name: 'comment', value: comment_html});
        data.push({name: 'mobile_no', value: mobile_no});
        data.push({name: 'thumbnail', value: thumbnail});
        data.push({name: 'media_duration', value: '90'});
        var accessToken=ge_local_data.access_token;
          
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

    function current_comment(videoCommentList){debugger;
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

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+'"><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.topic+','+itemVideo.id+');" id="commentLikeReaction" href="javascript:void();" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

        $("#currentCommentId").append(listCommentItems);
    }
  function likeAndUnlikeComment(topicId,commentId){debugger;
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
          data:{topic_id:topicId,comment_id:commentId},
          success: function(response,textStatus, xhr){debugger;
            //response.message=='liked'
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

 var player;
 var playerInstance = jwplayer("player");
 $(document).ready(function() {
    playerInstance.play();
});

  function updateUserLikeStatus(topic_id){debugger;

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
          success: function(response,textStatus, xhr){debugger;
              console.log(response);
          },
          error: function(jqXHR, textStatus, errorThrown){
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
          }

    
      });


  }  

