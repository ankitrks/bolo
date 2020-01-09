
  jQuery('#UCommentLink').on('click',function(){
      var commentBoxInputStatus=jQuery('#commentInputId').hasClass('hide');
      if(commentBoxInputStatus==true){
         var loginStatus= check_login_status();
         if(loginStatus==false){
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
  //e.preventDefault();
  var code = e.which || e.keyCode;
  console.log(code);
 var key = e.which;
 console.log(key);
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

        listCommentItems +='<div class="_video_card_big_comment_item_"><span class="_avatar_ _avatar_small" style="background-image: url('+profileImage+'); margin-right: 8px;"></span><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/'+itemVideo.user.username+'/">'+itemVideo.user.username+'</a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message">'+itemVideo.comment+'</div><div class="_video_card_big_comment_item_"><div class="_video_card_big_comment_item_content"><div class="_video_card_big_comment_item_name"><a href="/"></a><span class="_video_card_big_comment_item_label"> · author</span></div><div class="_video_card_big_comment_item_message"></div></div></div><div class="_video_card_big_comment_item_time"><span class="_6qw6" data-testid="UFI2ReactionLink/comment"><div class="_8c74 changeLikeColor-'+itemVideo.id+'"><a aria-pressed="false" class=" _6a-y _6qw5 _77yo" data-testid="UFI2ReactionLink" onclick="likeAndUnlikeComment('+itemVideo.id+');" id="commentLikeReaction" href="javascript:void();" role="button" tabindex="-1">Like<span class="likedStatus-'+itemVideo.id+' hide">d</span></a> </div></span> - '+itemVideo.date+'</div></div></div>';

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


function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;

  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      //console.log(val);
      var res = val.substring(0,1);
      
      if(res=='#' || res=='@'){}else{
        return false;
      }
      

    
      if (!val) { return false;}
      currentFocus = -1;
      autoCompleteJsonData(val);
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/

      arr.forEach(function(eachItems){
        console.log(eachItems.id);
        var nameS=eachItems.name;
        var userProfileImage="";
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          
          console.log(eachItems.profile_pic);
          if(eachItems.profile_pic!=""){
            userProfileImage=eachItems.profile_pic;
          }else{
            userProfileImage='/media/demo_user.png';
          }

          b.innerHTML += '<img class="_avatar_ _avatar_small" height="100"  src="' + userProfileImage + '" />';
          b.innerHTML += "<span class='userNameMargin'><strong>" + nameS.substr(0, val.length) + "</strong>"+nameS.substr(val.length)+"</span>";
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + nameS + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              var valuelink='<a href="javascript:void(0)">'+this.getElementsByTagName("input")[0].value;+'</a>'
              inp.value = this.getElementsByTagName("input")[0].value;
              inp.focus();
              //addTag(this.getElementsByTagName("input")[0].value);
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
  
      });

  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      
      if (x) x = x.getElementsByTagName("div");
     
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        
        addActive(x);
        

      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        
        addActive(x);
        
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/

    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}

/*An array containing all the country names in the world:*/
var countries=[];
//countries = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua & Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia & Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Cayman Islands","Central Arfrican Republic","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cuba","Curacao","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauro","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre & Miquelon","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","St Kitts & Nevis","St Lucia","St Vincent","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad & Tobago","Tunisia","Turkey","Turkmenistan","Turks & Caicos","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States of America","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];




 // function autoCompleteJsonData(x){
 //      console.log(x); 
 //      var valIn=document.getElementById("comment-input").value;
 //      var s2 = valIn.substr(1);

 //      var ge_local_data="";
 //          ge_local_data = JSON.parse(localStorage.getItem("access_data"));
 //      var accessToken=ge_local_data.access_token;
 //      var listCommentItems="";
 //      var uri='/api/v1/mention_suggestion/';
 //      var res = encodeURI(uri);
 //      jQuery.ajax({
 //          url:res,
 //          type:"POST",
 //          headers: {
 //            'Authorization':'Bearer '+accessToken,
 //          },
 //          data:{term:s2},
 //          success: function(response,textStatus, xhr){
 //            countries = response.mention_users;
 //            autocomplete(document.getElementById("comment-input"), countries); 
 //          },
 //          error: function(jqXHR, textStatus, errorThrown){
 //              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
 //          }
 //      });
 // }

 // $(function() {
 //    autocomplete(document.getElementById("comment-input"), countries);
  
 //  });


  //   var tagsArray=[];

  //   var timer;
  //   var wrap;
  //   var field;
  //   var el=document.getElementById('exist-values');
  //   var tags = '.tagged';

      
  //   function addTag(name) {


  //     name = name.toString().replace(/,/g, '').trim();

  //     if(name === '') return field.value = '';

  //     if(~tagsArray.indexOf(name)) {


  //       addClass('tag--exists', tag);
  //       return field.value = '';
  //     }
  //     var tag = createTag(name);
  //     console.log(tag);

  //     wrap = create('div', {
  //       'className': 'tags-container',
  //     });
  //     field = create('input', {
  //       'type': 'text',
  //       'className': 'tag-input',
  //       'placeholder': el.placeholder || ''
  //     });


  //     $('.lastElement').before(tag);
  //     $('#comment-input').val("");
  //     $('#comment-input').focus();

  //     tagsArray.push(name);
  //     el.value += (el.value === '') ? name : ',' + name;
  //   }

  //   function createTag(name) {
  //     var result = name.replace(" ", "_");
  //     var tag = create('div', {
  //       'className': 'tag '+result+'',
  //       'innerHTML': '<span class="tag__name">' + name + '</span>'+
  //                    '<button class="tag__remove " onclick="btnRemove(\''+result+'\');">&times;</button>'
  //     });
  //     return tag;
  //   }

  //   function btnRemove(e) {

  //       $("."+e).remove();
  //       tagsArray.splice(tagsArray.indexOf(e), 1);
  //       el.value = tagsArray.join(',')
  //       field.focus();
  //   }

  // function removeTag() {
  //   if(tagsArray.length === 0) return;

  //   var tags = $$('.tag', wrap);
  //   var tag = tags[tags.length - 1];

  //   if( ! hasClass('tag--marked', tag) ) {
  //     addClass('tag--marked', tag);
  //     return;
  //   }

  //   tagsArray.pop();

  //   wrap.removeChild(tag);

  //   el.value = tagsArray.join(',');
  // }

  // function hasClass(cls, el) {
  //   return new RegExp('(^|\\s+)' + cls + '(\\s+|$)').test(el.className);
  // }
  // function addClass(cls, el) {
  //   if( ! hasClass(cls, el) )
  //     return el.className += (el.className === '') ? cls : ' ' + cls;
  // }
  // function removeClass(cls, el) {
  //   el.className = el.className.replace(new RegExp('(^|\\s+)' + cls + '(\\s+|$)'), '');
  // }
  // function toggleClass(cls, el) {
  //   ( ! hasClass(cls, el)) ? addClass(cls, el) : removeClass(cls, el);
  // }

  //   function create(tag, attr) {
  //   var element = document.createElement(tag);
  //   if(attr) {
  //     for(var name in attr) {
  //       if(element[name] !== undefined) {
  //         element[name] = attr[name];
  //       }
  //     }
  //   }
  //   return element;
  // }


/*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/

//====================Mention and hashtag===================

    $(function () {
      var searchURI="";
      var hashTagSearch="";
      $('#comment-input').keydown(function(e){
        console.log('keyCode:'+e.keyCode);
        if (e.keyCode == 50) {
          searchURI="/api/v1/mention_suggestion/";
          hashTagSearch="";
        }else if(e.keyCode == 51){
          hashTagSearch=51;
          searchURI="/api/v1/hashtag_suggestion/";
        }
      });
      

      $('textarea.mention').mentionsInput({
        onDataRequest:function (mode, query, callback) {
            
            var uri='/api/v1/mention_suggestion/';
            var res = encodeURI(searchURI);
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

                success: function (response) {debugger;
                    if(hashTagSearch==51){
                      var responseData = response.hash_data;
                      capitals = responseData.map(function(obj) { 
                          obj['name'] = obj.hash_tag; // Assign new key  
                          obj['username'] = obj.hash_tag; // Assign new key  
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
//=====================End mentions=========================





