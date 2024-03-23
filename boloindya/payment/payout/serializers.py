from datetime import datetime

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

    def to_representation(self, instance):
        data = super(ScheduledPaymentSerializer, self).to_representation(instance)
        data['created_at'] = datetime.strftime(instance.created_at, '%B %d, %Y %I:%M %p')
        return data


class TransactionSerializer(serializers.ModelSerializer):
    beneficiary_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'


    def get_beneficiary_name(self, instance):
        return instance.beneficiary.name

    def to_representation(self, instance):
        data = super(TransactionSerializer, self).to_representation(instance)
        data['transaction_date'] = datetime.strftime(instance.transaction_date, '%B %d, %Y %I:%M %p')
        return data


class PaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'