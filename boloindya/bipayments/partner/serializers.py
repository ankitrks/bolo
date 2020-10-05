from django.urls import reverse

from rest_framework import serializers

from bipayments.partner.models import Beneficiary, TopUser


class BeneficiarySerializer(serializers.ModelSerializer):
    beneficiary_link = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiary
        fields = '__all__'
        read_only_fields = ('id',)


    def get_beneficiary_link(self,instance):
        return '<a href="'+reverse('beneficiary-view', kwargs={'pk': instance.id})+'">' + instance.name + '</a>'


class TopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopUser
        fields = '__all__'