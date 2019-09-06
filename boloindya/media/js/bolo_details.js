$(document).ready(function(){
      addEvents();
});


function addEvents() {
      $('.form-group').on('keyup',"#id_amount",showninttostring);
      $(document).on('click','.encash_bolo',encash_bolo);

}

function showninttostring(){
  var int_amount = $("input[id=id_amount]").val();
  console.log(int_amount);
  var string_amount = $.wordMath.toString(int_amount);
  $(".string_amount").text(string_amount);
}
function encash_bolo(){
  var encashable_id=$(this).attr('encashable_id')
  $('#id_enchashable_detail').val(encashable_id);
}


