from django.urls import reverse

from rest_framework import serializers

from payment.partner.models import Beneficiary, TopUser
from payment.paytm_api import verify_beneficiary, generate_order_id


class BeneficiarySerializer(serializers.ModelSerializer):
    beneficiary_link = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiary
        fields = '__all__'
        read_only_fields = ('id',)


    def get_beneficiary_link(self,instance):
        return '<a href="'+reverse('payment:beneficiary-view', kwargs={'pk': instance.id})+'">' + instance.name + '</a>'

    def validate(self, data):
        if data.get('payment_method') == 'account_transfer' and (not data.get('bank_ifsc') or not data.get('bank_ifsc')):
            raise serializers.ValidationError("Bank IFSC is also required")

            response = verify_beneficiary(generate_order_id(), data.get('bank_ifsc'), data.get('bank_ifsc'))

            if not response.get('status') in ['SUCCESS', 'ACCEPTED']:
                raise serializers.ValidationError("Bank Account detail not correct!!")
        elif data.get('payment_method') == 'paytm_wallet' and not data.get('paytm_number'):
                raise serializers.ValidationError("Paytm Number is required")
        elif data.get('payment_method') == 'upi' and not data.get('upi'):
                raise serializers.ValidationError("UPI is required")

        return data


class TopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopUser
        fields = '__all__'