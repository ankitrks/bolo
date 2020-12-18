from django.contrib.auth.models import User

from rest_framework import serializers

from advertisement.models import Ad, Brand
from marketing.models import AdStats


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('title', 'created_by')

class AdStatsSerializer(serializers.ModelSerializer):
    ctr = serializers.SerializerMethodField()
    # average_install_time = serializers.SerializerMethodField()
    # average_skip_time = serializers.SerializerMethodField()
    ad = AdSerializer()

    class Meta:
        model = AdStats
        fields = '__all__'

    def get_ctr(self, instance):
        return (instance.install_count / instance.view_count) * 100

    # def get_average_install_time(self, instance):

class AdCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class AdBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')
