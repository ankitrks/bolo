$(document).ready(function(){
      addEvents();
});


function addEvents() {
      $('.form-group').on('keyup',"#id_amount_pay",showninttostring);
      $(document).on('click','.user_pay',pay_user);
      $(document).on('click','.submit_payment',submit_payment);

}

function showninttostring(){
  var int_amount = $("input[id=id_amount_pay]").val();
  console.log(int_amount);
  var string_amount = $.wordMath.toString(int_amount);
  $(".string_amount").text(string_amount);
}
function pay_user(){
  var user_pay_id=$(this).attr('user_pay_id');
  var for_month=$(this).attr('for_month');
  var for_year=$(this).attr('for_year');
  $('#user_pay_id').val(user_pay_id);
  $('.for_month_year').html("<strong>"+for_month+"/"+for_year+"</strong>");
}

function submit_payment(e){
  e.preventDefault();
  var user_pay_id = $("#user_pay_id").val();
  var amount_pay = $("#id_amount_pay").val();
  var transaction_id = $("#id_transaction_id").val();
  var csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val();
  console.log(user_pay_id,amount_pay,transaction_id)

  data = {
        user_pay_id: user_pay_id,
        amount_pay: amount_pay,
        transaction_id:transaction_id,
        csrfmiddlewaretoken:csrfmiddlewaretoken
    }
    $.ajax({
        url: "/jarvis/add_user_pay/",
        //contentType: false,
        dataType: "json",
        //processData: false,
        type: "POST",
        data: data,
        success: function(data) {
          if (data.is_success =='success'){
            toastr.success('Payment Made');
            location.reload();
          }
          else if(data.is_success =='fail'){
            toastr.info('Error Occured: '+data.reason);
          }
        },
        error: function(data) {
            toastr.info('Error Occured: '+data);
            console.log(data)
        }
    });
}
