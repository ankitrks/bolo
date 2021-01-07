from datetime import datetime

from django.contrib.auth.models import User

from rest_framework import serializers

from forum.category.models import Category
from advertisement.models import Ad, Brand
from booking.models import Event, EventBooking
from marketing.models import AdStats, EventStats


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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class EventUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='st.name', read_only=True)
    phone_number = serializers.CharField(source='st.mobile_no', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'phone_number')


class EventSerializer(serializers.ModelSerializer):
    creator = EventUserSerializer()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'creator', 'title', 'category_name', 'price')


class EventBookingSerializer(serializers.ModelSerializer):
    user = EventUserSerializer()
    event = EventSerializer()

    class Meta:
        model = EventBooking
        fields = '__all__'

    def to_representation(self, instance):
        data = super(EventBookingSerializer, self).to_representation(instance)
        data['created_at'] = datetime.strftime(instance.created_at, '%B %d, %Y %I:%M %p')
        return data


class EventStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStats
        fields = '__all__'