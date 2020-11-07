from rest_framework import serializers

from advertisement.models import Ad, ProductReview, Order, Product

class AdSerializer(serializers.ModelSerializer):
    ad_id = serializers.CharField(source='id', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_image = serializers.CharField(source='brand.image', read_only=True)
    cta = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('ad_id', 'brand_name', 'brand_image', 'ad_video', 'thumbnail', 'ad_length')

    def get_cta(self, instance):
        return instance.cta.all().values('title', 'code', 'enable_time', 'action')


class ProductSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    product_id = serializers.CharField(source='id', read_only=True)
    product_title = serializers.CharField(source='title', read_only=True)
    product_description = serializers.CharField(source='description', read_only=True)
    discounted_price = serializers.CharField(source='price', read_only=True)

    class Meta:
        model = Product
        fields = ('product_id', 'product_title', 'product_description', 'product_images', 'rating_count', 'rating',
                    'currency', 'mrp', 'is_discounted', 'discounted_price', 'discount_expiry')

    def get_product_images(self, instance):
        return instance.images.all().values_list('url')


class ReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.CharField(source='id', read_only=True)

    class Meta:
        model = ProductReview
        fields = ('review_id', 'title', 'description', 'rating')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'state', 'address', 'amount')


