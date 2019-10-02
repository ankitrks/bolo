$(document).ready(function() {
    addEvents();

});

function addEvents() {
    $(document).on('click', '.kyc_accept', kyc_accept);
    $(document).on('click', '.kyc_reject', kyc_reject);
    $(document).on('click', '.reject_submit', reject_submit);
}

function kyc_accept() {
    var kyc_type = $(this).attr("kyc_type");
    var user_id = $(this).attr("user_id");
    var that = this
    data = {
        kyc_type: kyc_type,
        user_id: user_id
    }
    $.ajax({
        url: "/jarvis/accept_kyc/",
        //contentType: false,
        dataType: "json",
        //processData: false,
        type: "GET",
        data: data,
        success: function(data) {
            toastr.success('Accepted');
            $(that).parents('.action_button').empty();
            $(that).parents('.action_button').append('<span class="btn-primary" style="padding:10px;">Accepted</span>')
        },
        error: function(data) {
            toastr.info('Error Occured: '+data);
            console.log(data)
        }
    });
}

function kyc_reject(e) {
    e.preventDefault();
    var kyc_type = $(this).attr("kyc_type");
    var kyc_id = $(this).attr("kyc_id");
    var user_id = $(this).attr("user_id");
    $($(this).attr('data-target')).find('.reject_submit').attr('kyc_type',kyc_type)
    $($(this).attr('data-target')).find('.reject_submit').attr('kyc_id',kyc_id)
    $($(this).attr('data-target')).find('.reject_submit').attr('user_id',user_id)
}

function reject_submit(){
    var kyc_reject_reason = $(this).parents('form').find('#id_reject_reason').val();
    var kyc_reject_text = $(this).parents('form').find('#id_reject_text').val();
    var kyc_type = $(this).attr("kyc_type");
    var kyc_id = $(this).attr("kyc_id");
    var user_id = $(this).attr("user_id");
    data = {
        kyc_type: kyc_type,
        kyc_id: kyc_id,
        user_id: user_id,
        kyc_reject_reason:kyc_reject_reason,
        kyc_reject_text:kyc_reject_text

    }
    $.ajax({
        url: "/jarvis/reject_kyc/",
        //contentType: false,
        dataType: "json",
        //processData: false,
        type: "GET",
        data: data,
        success: function(data) {
            toastr.error('Rejected');
            $('.close').click()
            console.log(data)
        },
        error: function(data) {
            toastr.info('Error Occured: '+data);
            $('.close').click()
            console.log(data)
        }
    });

}