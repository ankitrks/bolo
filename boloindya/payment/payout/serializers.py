
from rest_framework import serializers


from payment.payout.models import ScheduledPayment, Transaction


class ScheduledPaymentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledPayment
        fields = '__all__'
        read_only_fields = ('id',)

    def get_created_by_name(self, instance):
        return instance.created_by and instance.created_by.username or ''


class TransactionSerializer(serializers.ModelSerializer):
    beneficiary_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'


    def get_beneficiary_name(self, instance):
        return instance.beneficiary.name


class PaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'