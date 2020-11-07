from datetime import datetime
from django.contrib.humanize.templatetags.humanize import intcomma

from rest_framework import serializers

from advertisement.models import Ad, ProductReview, Order, Product

class AdSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField(source='id', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_image = serializers.CharField(source='brand.company_logo', read_only=True)
    ad_video = serializers.CharField(source='video_file_url', read_only=True)
    cta = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('ad_id', 'brand_name', 'brand_image', 'ad_video', 'thumbnail', 'ad_length', 'cta', 'type')

    def get_cta(self, instance):
        return instance.cta.all().values('title', 'code', 'enable_time', 'action')

    def get_type(self, instance):
        return 'ad'


class ProductSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    product_id = serializers.CharField(source='id', read_only=True)
    product_title = serializers.CharField(source='name', read_only=True)
    product_description = serializers.CharField(source='description', read_only=True)
    discounted_price = serializers.SerializerMethodField()
    mrp = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    discount_expiry = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('product_id', 'product_title', 'product_description', 'product_images', 'rating_count', 'rating',
                    'currency', 'mrp', 'is_discounted', 'discounted_price', 'discount_expiry')

    def get_product_images(self, instance):
        return instance.images.all().values_list('compressed_image', flat=True)

    def get_rating_count(self, instance):
        return intcomma(instance.rating_count)

    def get_mrp(self, instance):
        return "Rs %s"%instance.mrp

    def get_discounted_price(self, instance):
        return "Rs %s"%instance.discounted_price

    def get_discount_expiry(self, instance):
        return datetime.strftime(instance.discount_expiry, "%d-%m-%y %H:%M:%S")


class ReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.CharField(source='id', read_only=True)

    class Meta:
        model = ProductReview
        fields = ('review_id', 'title', 'description', 'rating')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'state', 'address', 'amount')


