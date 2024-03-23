from forum.userkyc.models import UserKYC

def run():
    UserKYC.objects.filter(is_kyc_completed=True,is_kyc_accepted=False).update(is_kyc_accepted = True,is_kyc_basic_info_accepted = True,is_kyc_document_info_accepted = True,is_kyc_pan_info_accepted = True,is_kyc_selfie_info_accepted = True,is_kyc_additional_info_accepted = True,is_kyc_bank_details_accepted = True)
        