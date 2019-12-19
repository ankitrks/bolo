function loaderBoloShowDynamic(classLoader){
    var boloLoader='<img src="/media/loader.gif">';
        $('.'+classLoader).html(boloLoader);

}

function loaderBoloHideDynamic(classLoader){
    var boloLoader='';
    $('.'+classLoader).html(boloLoader);
    
}

function social_share_page(shareType,pageName){
    var shareURL="";
    if(shareType=='facebook_share'){

        shareURL='https://www.facebook.com/sharer/sharer.php?app_id=113869198637480&u=https://www.boloindya.com/'+pageName+'&display=popup&sdk=joey/';

    }else if(shareType=='twitter_share'){

        shareURL='https://twitter.com/intent/tweet?text=https://www.boloindya.com/'+pageName+'&url=https://www.boloindya.com/'+topicCreatorUsername
    }else if(shareType=='whatsapp_share'){
        shareURL='https://api.whatsapp.com/send?text=https://www.boloindya.com'+pageName;
    }
    
     window.open(shareURL, '_blank');
}

jQuery(document).ready(function($){
  var $form_modal = $('.cd-user-modal'),
    $form_login = $form_modal.find('#cd-login'),
    $form_signup = $form_modal.find('#cd-signup'),
    $form_forgot_password = $form_modal.find('#cd-reset-password'),
    $form_modal_tab = $('.cd-switcher'),
    $tab_login = $form_modal_tab.children('li').eq(0).children('a'),
    $tab_signup = $form_modal_tab.children('li').eq(1).children('a'),
    $forgot_password_link = $form_login.find('.cd-form-bottom-message a'),
    $back_to_login_link = $form_forgot_password.find('.cd-form-bottom-message a'),
    $main_nav = $('.main-nav');

    $main_nav.on('click', function(event){

    if( $(event.target).is($main_nav) ) {
      // on mobile open the submenu
      $(this).children('ul').toggleClass('is-visible');
    } else {
      // on mobile close submenu
      $main_nav.children('ul').removeClass('is-visible');
      $form_modal.addClass('is-visible'); 
      //show the selected form
      ( $(event.target).is('.cd-signup') ) ? signup_selected() : login_selected();
    }

});

  //close modal
  $('.cd-user-modal').on('click', function(event){
    if( $(event.target).is($form_modal) || $(event.target).is('.cd-close-form') ) {
      $form_modal.removeClass('is-visible');
    } 
  });
  //close modal when clicking the esc keyboard button
  $(document).keyup(function(event){
      if(event.which=='27'){
        $form_modal.removeClass('is-visible');
      }
    });

  //switch from a tab to another
  $form_modal_tab.on('click', function(event) {
    event.preventDefault();
    ( $(event.target).is( $tab_login ) ) ? login_selected() : signup_selected();
  });

  //hide or show password
  $('.hide-password').on('click', function(){
    var $this= $(this),
      $password_field = $this.prev('input');
    
    ( 'password' == $password_field.attr('type') ) ? $password_field.attr('type', 'text') : $password_field.attr('type', 'password');
    ( 'Hide' == $this.text() ) ? $this.text('Show') : $this.text('Hide');
    //focus and move cursor to the end of input field
    $password_field.putCursorAtEnd();
  });

  //show forgot-password form 
  $forgot_password_link.on('click', function(event){
    event.preventDefault();
    forgot_password_selected();
  });

  //back to login from the forgot-password form
  $back_to_login_link.on('click', function(event){
    event.preventDefault();
    login_selected();
  });

  function login_selected(){
    $form_login.addClass('is-selected');
    $form_signup.removeClass('is-selected');
    $form_forgot_password.removeClass('is-selected');
    $tab_login.addClass('selected');
    $tab_signup.removeClass('selected');
  }

  function signup_selected(){
    $form_login.removeClass('is-selected');
    $form_signup.addClass('is-selected');
    $form_forgot_password.removeClass('is-selected');
    $tab_login.removeClass('selected');
    $tab_signup.addClass('selected');
  }

  function forgot_password_selected(){
    $form_login.removeClass('is-selected');
    $form_signup.removeClass('is-selected');
    $form_forgot_password.addClass('is-selected');
  }

  //REMOVE THIS - it's just to show error messages 
  $form_login.find('input[type="submit"]').on('click', function(event){
    event.preventDefault();
    $form_login.find('input[type="email"]').toggleClass('has-error').next('span').toggleClass('is-visible');
  });
  $form_signup.find('input[type="submit"]').on('click', function(event){
    event.preventDefault();
    $form_signup.find('input[type="email"]').toggleClass('has-error').next('span').toggleClass('is-visible');
  });




});


jQuery.fn.putCursorAtEnd = function() {
  return this.each(function() {
      // If this function exists...
      if (this.setSelectionRange) {
          // ... then use it (Doesn't work in IE)
          // Double the length because Opera is inconsistent about whether a carriage return is one character or two. Sigh.
          var len = $(this).val().length * 2;
          this.setSelectionRange(len, len);
      } else {
        // ... otherwise replace the contents with itself
        // (Doesn't work in Google Chrome)
          $(this).val($(this).val());
      }
  });
};

jQuery("#boloSideMenu").click(function(e){
      e.stopPropagation();

      var checClass="";
       checClass=jQuery(".boloSideMenuClass").hasClass('hamburger-menu-active');
        if(checClass){
            jQuery(".boloSideMenuClass").removeClass('hamburger-menu-active');  
            jQuery(".drawerOpenAndClose").removeClass('drawer-enter drawer-enter-active');
            jQuery(".drawerOpenAndClose").addClass('drawer-exit drawer-exit-active');  
            jQuery(".drawer-enter-done").addClass('hide');
      }else {
            jQuery(".boloSideMenuClass").addClass('hamburger-menu-active'); 
            jQuery(".boloSideMenuClass").removeClass('drawer-exit drawer-exit-active');
            jQuery(".drawerOpenAndClose").addClass('drawer-enter drawer-enter-active');
            jQuery(".drawer-enter-done").removeClass('hide');
      }

});
jQuery('body,html').click(function(e){

      var checClass="";
       checClass=jQuery(".boloSideMenuClass").hasClass('hamburger-menu-active');
        if(checClass){
            jQuery(".boloSideMenuClass").removeClass('hamburger-menu-active');  
            jQuery(".drawerOpenAndClose").removeClass('drawer-enter drawer-enter-active');
            jQuery(".drawerOpenAndClose").addClass('drawer-exit drawer-exit-active');  
            jQuery(".drawer-enter-done").addClass('hide');
      }
});

$(document).ready(function() {
  loaderHide();
  loginDataByUser();
});

function loaderShow(){
    $(".LoaderBalls").show();
 }
function loaderHide(){
    $(".LoaderBalls").hide();
 }

function loaderBoloShow(){
    var boloLoader='<div id="loading-bar-spinner" class="spinner"><div class="spinner-icon"></div></div>';
        $('._scroll_load_more_loading').html(boloLoader);

}

function loaderBoloHide(){
    var boloLoader='';
    $('._scroll_load_more_loading').html(boloLoader);
    
}



//==============Global Popup Close=============

 $("._global_modal_cancel").click(function(){
  jwplayer('player').setMute(true);
    $("#modelPopup").hide();
 });
 //=================End=======================


function copyShareLink() {
  var copyText = document.getElementById("shareInputbox");
  copyText.select();
  copyText.setSelectionRange(0, 99999)
  document.execCommand("copy");

}

function copyShareLinkMobile() {
  var copyText = document.getElementById("shareInputboxMobile");
  copyText.select();
  copyText.setSelectionRange(0, 99999)
  document.execCommand("copy");
  jQuery('.linkCopies').html('<span style="color:green">Link Copied...</span>').fadeOut(2000);

}


    function openMobileDownloadPopup(){
        $('.mobileDownPopup').toggleClass('hide');
        console.log('asdasd');
    }


    function check_login_status(){
      var access_data="";
        access_data = JSON.parse(localStorage.getItem("access_data"));
        if (!access_data){
          return false; 
        } else {
          return true;
        }
      }
    

    function sendOTP(){
      $("#lastFourdigit").html("");
      validateNo();
      var mobileNumber = document.getElementById('phoneNo').value;
      var rowId = document.getElementById('rowId').value;
      var data= "rowId="+rowId+"&mobileNumber="+mobileNumber;
      var elem = document.getElementById('some_div');
      elem.innerHTML ='Please wait...';
      var otpDetailsList=[];
      otpDetailsList.push({name: 'mobile_no', value: mobileNumber});
      console.log(otpDetailsList);

      jQuery.ajax({
        url:"/api/v1/otp/send/",
        type:"POST",
        data:{'mobile_no':mobileNumber},
        success: function(response,textStatus, xhr){
          console.log(textStatus);
          console.log(xhr);
          if(xhr.status==201){
            mobileNum=response.mobile_no;
            var lastFour = mobileNumber.substring(mobileNumber.length-4);
            $("#lastFourdigit").html(lastFour);
            dispOTPPanel();
          }else{
            $('.errorMess').html('<span>Please Try another number or Resend</span>');
            return false;
          }

        }

      });
    }


  function otp_verification(){
 
      var mobileNumber = document.getElementById('phoneNo').value;
      var rowId = document.getElementById('rowId').value;
      var data= "rowId="+rowId+"&mobileNumber="+mobileNumber;
      var elem = document.getElementById('some_div');
      elem.innerHTML ='Please wait...';
      var otpDetailsList=[];
      var data = jQuery('form#optForm').serializeArray();
      data.push({name: 'rowId', value: rowId});
      data.push({name: 'mobile_no', value: mobileNumber});
      console.log(data);
      var userOtp = document.getElementById('userOtp');
      console.log(data);
      var otpConcat="";
      for(var otpCount=1;otpCount<7;otpCount++){
       var otpData= jQuery('input[name="digit-'+otpCount+'"]').val();
        if(otpData!=""){
          otpConcat +=otpData;
        }
      }
      var userOTP="";
      if(otpConcat.length==6){

      userOTP=otpConcat;      
      jQuery.ajax({
        url:"/api/v1/otp/verify/",
        type:"POST",
        data:{'mobile_no':mobileNumber,'otp':userOTP,'is_reset_password':false,'is_for_change_phone':false},
        success: function(response,textStatus, xhr){

          access_data = response;
          localStorage.setItem("access_data",JSON.stringify(access_data));
          jQuery('#commentInputId').removeClass('hide');
          $("form#optForm")[0].reset();
          window.location.hash = '#comment';
           $("#modelPopup").hide();
        },
        error: function(jqXHR, textStatus, errorThrown){
          $("form#optForm")[0].reset();
          jQuery(".otpError").html('<span style="color:red;">Invalid Mobile No / OTP</span>').fadeOut(8000);
          console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
        }


      });
    }else{
      $("form#optForm")[0].reset();
      $('#conOTPVerify').prop('disabled', true);
      jQuery(".otpError").html('<span style="color:red;">Opps! Invalid OTP, Please Try again</span>').fadeOut(8000);
      return false;
    }
  }


function loginDataByUser(){
	var url='/api/v1/user/user_data/';
	var user_id = userLoginStatus;
	var loginStatus=check_login_status();
	if(loginStatus==false && user_id!="" && user_id!='None'){
	    $.ajax({
	        type: 'POST',
	        url: url,
	        data: {user_id: user_id},
	    }).done(function(data, textStatus, jqXHR) {
	        access_data = data;
	        if(access_data){
          		localStorage.setItem("access_data",JSON.stringify(access_data));
          	}
	    });
	}
}


function follow_user(user_following_id){
	var user_id = userLoginStatus;
	var followUrl='/api/v1/follow_user/';
	var user_following_id = user_following_id;
	var loginStatus=check_login_status();
	if(loginStatus==true){
		var ge_local_data="";
        ge_local_data = JSON.parse(localStorage.getItem("access_data"));
        var accessToken=ge_local_data.access_token;
        jQuery.ajax({
            url:followUrl,
            type:"POST",
            headers: {
              'Authorization':'Bearer '+accessToken,
            },
            data:{user_following_id:user_following_id},
            success: function(response,textStatus, xhr){
 
               checkFollowStatus=jQuery('.followStatusChange-'+user_following_id).hasClass('sx_5da456');
               if(checkFollowStatus==false){
	               	jQuery('.followStatusChange-'+user_following_id).removeClass('sx_5da455');
	               	jQuery('.followStatusChange-'+user_following_id).addClass('sx_5da456');
	               	jQuery('.btnTextChange-'+user_following_id).text(response.message);
               }else{
	               	jQuery('.followStatusChange-'+user_following_id).removeClass('sx_5da456');
	               	jQuery('.followStatusChange-'+user_following_id).addClass('sx_5da455');
	               	jQuery('.btnTextChange-'+user_following_id).text('Follow');
               }

            },
            error: function(jqXHR, textStatus, errorThrown){
              jQuery(".followError").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
            }


        });
	}else{
		document.getElementById('openLoginPopup').click();
	}
}

function follow_user_by_popup(){
	var user_following_id=$("#currentPlayUserId").val();
	if(user_following_id==""){
		return false;
	}
	var user_id = userLoginStatus;
	var followUrl='/api/v1/follow_user/';
	var user_following_id = user_following_id;
	var loginStatus=check_login_status();
	if(loginStatus==true){
		var ge_local_data="";
        ge_local_data = JSON.parse(localStorage.getItem("access_data"));
        var accessToken=ge_local_data.access_token;
        jQuery.ajax({
            url:followUrl,
            type:"POST",
            headers: {
              'Authorization':'Bearer '+accessToken,
            },
            data:{user_following_id:user_following_id},
            success: function(response,textStatus, xhr){
 
               checkFollowStatus=jQuery('.followStatusChange-'+user_following_id).hasClass('sx_5da456');
               if(checkFollowStatus==false){
	               	jQuery('.followStatusChangePopup').removeClass('sx_5da455');
	               	jQuery('.followStatusChangePopup').addClass('sx_5da456');
	               	jQuery('.btnTextChangePopup').text(response.message);
               }else{
	               	jQuery('.followStatusChangePopup').removeClass('sx_5da456');
	               	jQuery('.followStatusChangePopup').addClass('sx_5da455');
	               	jQuery('.btnTextChangePopup').text('Follow');
               }

            },
            error: function(jqXHR, textStatus, errorThrown){
              jQuery(".followError").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
            }


        });
	}else{
		document.getElementById('openLoginPopup').click();
	}
}


function follow_category(following_id){

	var followUrl='/api/v1/follow_sub_category/';
	var following_id = following_id;
	var loginStatus=check_login_status();
	var user_id = userLoginStatus;
	if(loginStatus==true){
		var ge_local_data="";
        ge_local_data = JSON.parse(localStorage.getItem("access_data"));
        var accessToken=ge_local_data.access_token;
        jQuery.ajax({
            url:followUrl,
            type:"POST",
            headers: {
              'Authorization':'Bearer '+accessToken,
            },
            data:{sub_category_id:following_id},
            success: function(response,textStatus, xhr){
 
               checkFollowStatus=jQuery('.followStatusChange-'+following_id).hasClass('sx_5da456');
               if(checkFollowStatus==false){
	               	jQuery('.followStatusChange-'+following_id).removeClass('sx_5da455');
	               	jQuery('.followStatusChange-'+following_id).addClass('sx_5da456');
	               	jQuery('.btnTextChange-'+following_id).text(response.message);
               }else{
	               	jQuery('.followStatusChange-'+following_id).removeClass('sx_5da456');
	               	jQuery('.followStatusChange-'+following_id).addClass('sx_5da455');
	               	jQuery('.btnTextChange-'+following_id).text('Follow');
               }

            },
            error: function(jqXHR, textStatus, errorThrown){
              jQuery(".followError").html('<span style="color:red;">Please Try Again...</span>').fadeOut(8000);
              console.log(textStatus + ": " + jqXHR.status + " " + errorThrown);
            }


        });
	}else{
		document.getElementById('openLoginPopup').click();
	}
}




	// var localStorageKey='access_data';
		// localStorage.removeItem(localStorageKey);



// $('#language-list a').on('click', function(event) {
//     event.preventDefault();
//     var target = $(event.target);
//     var url = target.attr('href');
//     var language_code = target.data('language-code');
//     $.ajax({
//         type: 'POST',
//         url: url,
//         data: {language: language_code},
//         headers: {"X-CSRFToken": getCookie('csrftoken')}
//     }).done(function(data, textStatus, jqXHR) {
//         reload_page();
//     });
// });

// function getCookie(name) {
//     var value = '; ' + document.cookie,
//         parts = value.split('; ' + name + '=');
//     if (parts.length == 2) return parts.pop().split(';').shift();
// }

// function reload_page() {
//     window.location.reload(true);
// }


