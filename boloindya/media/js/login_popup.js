jQuery('.backToMainLogin').on('click',function(){
    var checkMainLoginHide=$(".mainLogin").hasClass('hide');
    if(checkMainLoginHide==false){
        $(".mainLogin").removeClass('hide');
        var loginWithFbOrEmail=$(".loginWithFbOrEmail").hasClass('hide');
        var otpPanelStatus=$(".OTP_Panel").hasClass('hide');
        if(otpPanelStatus==false){
            $(".OTP_Panel").addClass('hide');
        }
        if(loginWithFbOrEmail==false){
            $(".loginWithFbOrEmail").addClass('hide');
        }
        backTomainLoginFromNumber();
    }else{
      backTomainLoginFromEmail();
      $(".mainLogin").removeClass('hide');
      $(".loginWithFbOrEmail").addClass('hide');
      //$(".mainLogin").addClass('hide');
    }
});

function validateNo() {
    var phoneNo = document.getElementById('phoneNo');
    if (phoneNo.value == "" || phoneNo.value == null) {
      //alert("Please enter your Mobile No.");
      document.getElementById('phoneNo').focus();
      return false;
    }
    if (phoneNo.value.length < 10 || phoneNo.value.length > 10) {
      $('.mobileErrorMsg').html('<span style="font-size:16px;">Mobile No. is not valid, Please Enter 10 Digit Mobile No.</span>');
      document.getElementById('phoneNo').focus();
      return false;
    }
    
    $("#phoneNo").removeClass('success');
    $("#phoneNo").addClass('success');
    $('.mobileErrorMsg').html('<span></span>');
    //$('.mobileErrorMsg').html('<span style="color:green">Great...</span>');
    //$('.mobileErrorMsg').html('<span style="color:green">Great...</span>');
    return true;
}

jQuery('.email-or-fb-signin').on('click',function(){
    $(".loginWithFbOrEmail").removeClass('hide');
    var mainLoginStatus=$(".mainLogin").hasClass('hide');
    var otpPanelStatus=$(".OTP_Panel").hasClass('hide');
    if(otpPanelStatus==false){
        $(".OTP_Panel").addClass('hide');
    }
    // if(mainLoginStatus==false){
    //     $(".mainLogin").addClass('hide');
    // }
      
});

jQuery('.OTP_Panel').on('click',function(){
    $(".OTP_Panel").removeClass('hide');
    var mainLoginStatus=$(".mainLogin").hasClass('hide');
    var loginWithFbOrEmail=$(".loginWithFbOrEmail").hasClass('hide');
    if(loginWithFbOrEmail==false){
        $(".loginWithFbOrEmail").addClass('hide');
    }
    if(mainLoginStatus==false){
        $(".mainLogin").addClass('hide');
    }

});

function dispOTPPanel(){
  $(".OTP_Panel").removeClass('hide');
    var mainLoginStatus=$(".mainLogin").hasClass('hide');
    var loginWithFbOrEmail=$(".loginWithFbOrEmail").hasClass('hide');
  if(loginWithFbOrEmail==false){
    $(".loginWithFbOrEmail").addClass('hide');
  }
  if(mainLoginStatus==false){
    $(".mainLogin").addClass('hide');
  }

}

var checkClickStatus=0;
jQuery('#phoneNo').on('click',function(){
$("#phoneNo").removeClass('success');
var errorCheckPhone=$("#phoneNo").hasClass('error');
  if(errorCheckPhone==false){
    checkClickStatus=1;
    $(".heading-text").removeClass('hide');
    $(".heading-text").addClass('hide');
    $(".phoneLogin").removeClass('hide');
    
    $(".email-or-fb-signin").removeClass('hide');
    $(".email-or-fb-signin").addClass('hide');
    $(".activeNumberMode").removeClass('hide');
    $(".dispMainLogin").addClass('hide');
    // mainLoginHeading 
    // phoneLogin
    document.getElementById('phoneNo').focus();
    $("#phoneNo").addClass('error');
  }else{
    if(checkClickStatus==0){
      $("#phoneNo").removeClass('error');
    }
  }
}); 


$('#phoneNo').on('keypress',function(evt){
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
});

$('#phoneNo').on('change',function(evt){
    var phoneNo = document.getElementById('phoneNo');
    if (phoneNo.value == "" || phoneNo.value == null) {
      //alert("Please enter your Mobile No.");
      document.getElementById('phoneNo').focus();
      return false;
    }
    if (phoneNo.value.length < 10 || phoneNo.value.length > 10) {
      $('.mobileErrorMsg').html('<span style="font-size:16px;">Mobile No. is not valid, Please Enter 10 Digit Mobile No.</span>');
      document.getElementById('phoneNo').focus();
      return false;
    }
    
    $("#phoneNo").removeClass('success');
    $("#phoneNo").addClass('success');
    //$('.mobileErrorMsg').html();
    $('.mobileErrorMsg').html('<span></span>');
    return true;
});

$('#emailID').on('change',function(evt){
    var emailID = document.getElementById('emailID');
    if (emailID.value == "" || emailID.value == null) {
      //alert("Please enter your Mobile No.");
      document.getElementById('emailID').focus();
      return false;
    }
    var statusEmail=emailValidation();
    if(statusEmail==false){
      $("#emailID").addClass('error');
      $("#emailID").removeClass('success');

      return false;
    }    
    $("#emailID").removeClass('success');
    $("#emailID").addClass('success');
    $('.mail_vali_error').html('<span></span>');
    return true;
});

function emailValidation(){
  var emailid=$("#emailID").val();
  var emailRegex = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if(!emailRegex.test(emailid)){
      $("#emailID").focus();
      $(".mail_vali_error").html('<span style="font-size:16px;">Please enter valid email id</span>');
       return false;
    }
    return true;
   
}

var checkClickEmailStatus=0;
jQuery('#emailID').on('click',function(){

var errorCheckPhone=$("#emailID").hasClass('error');
  if(errorCheckPhone==false){
    checkClickEmailStatus=1;
    $(".activeEmailMode").removeClass('hide');
    $(".deActiveEmailMode").addClass('hide');
    // mainLoginHeading 
    // phoneLogin
    document.getElementById('emailID').focus();
    $("#emailID").addClass('error');
  }else{
    if(checkClickEmailStatus==0){
      $("#emailID").removeClass('error');
    }
  }
});


function backTomainLoginFromNumber(){
      var numActive=$(".activeNumberMode").hasClass('hide');
      if(numActive==false){
        $(".activeNumberMode").addClass('hide');
        $(".dispMainLogin").removeClass('hide');
        $(".heading-text").removeClass('hide');
        $(".phoneLogin").addClass('hide');
        $("#phoneNo").removeClass('error');
        $(".activeEmailMode").addClass('hide');
        $(".deActiveEmailMode").removeClass('hide');
        $("#emailID").removeClass('error');
    }

}

function backTomainLoginFromEmail(){
      var emailActive=$(".activeEmailMode").hasClass('hide');
      if(emailActive==false){
        $(".activeNumberMode").addClass('hide');
        $(".dispMainLogin").removeClass('hide');
        $(".heading-text").removeClass('hide');
        $(".phoneLogin").addClass('hide');
        $("#phoneNo").removeClass('error');
        $(".activeEmailMode").addClass('hide');
        $(".deActiveEmailMode").removeClass('hide');
        $("#emailID").removeClass('error');
    }

}
function generateOTP() { 
          
    // Declare a digits variable  
    // which stores all digits 
    var digits = '0123456789'; 
    let OTP = ''; 
    for (let i = 0; i < 4; i++ ) { 
        OTP += digits[Math.floor(Math.random() * 10)]; 
    } 
    return OTP; 
} 
  
//===========================================================


$('.single-otp-input').on('keypress',function(evt){
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    $('.digit-group').find('input').each(function() {
      $(this).attr('maxlength', 1);
      $(this).on('keyup', function(e) {
        var parent = $($(this).parent());
        
        if(e.keyCode === 8 || e.keyCode === 37) {
          var prev = parent.find('input#' + $(this).data('previous'));
          
          if(prev.length) {
            $(prev).select();
          }
        } else if((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 65 && e.keyCode <= 90) || (e.keyCode >= 96 && e.keyCode <= 105) || e.keyCode === 39) {
          var next = parent.find('input#' + $(this).data('next'));
          
          if(next.length) {
            $(next).select();
          } else {
            $('#conOTPVerify').prop('disabled', false);
            $('#conOTPVerify').removeClass('grey-btn');
            $('#some_div').hide();
            // if(parent.data('autosubmit')) {
            //   parent.submit();
            // }
          }
        }
      });
    });
});

jQuery(".resendCode").hide();
jQuery(".resendOTP").hide();
    var timeLeftResend = 120;
        var elemResend = document.getElementById('some_div');
        
        var timerIdResend = setInterval(countdownResend, 2000);
        
        function countdownResend() {
          if (timeLeftResend == 0) {
            jQuery(".resendOTP").show();
            jQuery(".resendCode").show();
            elemResend.innerHTML="";
          } else {
            var timeLeftTotal=timeLeftResend-1;
            elemResend.innerHTML = 'Resend code in: 00:'+timeLeftTotal;
            timeLeftResend--;
          }
        }

function showResendButton() {
  jQuery(".resendOTP").hide();
}



function getResendOTPSTatus(){

    var mobileNumber = document.getElementById('mobileNumberId').value;
      var rowId = document.getElementById('rowId').value;
      var data= "rowId="+rowId+"&mobileNumber="+mobileNumber;
      var elem = document.getElementById('some_div');
      elem.innerHTML ='Please wait...';

    jQuery.ajax({
        url:"cuser/resendOTP",
        type:"POST",
        data:data,
        success: function(response){
          if(response==1){
            jQuery("#some_div").html('<span style="color:green;">Success! Please check yoour device</span>');
            resendStatus=0;
          }
        }

    });
} 


