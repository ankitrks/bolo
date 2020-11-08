from datetime import datetime
from django.contrib.humanize.templatetags.humanize import intcomma

from rest_framework import serializers

from advertisement.models import Ad, ProductReview, Order, Product, Address, OrderLine

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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'name', 'mobile', 'alternate_number', 'email', 'address1', 'address2', 'address3', 'city', 'state', 'pincode']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self._context.get('request').user
        return super(AddressSerializer, self).create(validated_data)


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ['product', 'quantity', 'amount']
        read_only_fields = ['amount']


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True)
    shipping_address = AddressSerializer()

    class Meta:
        model = Order
        fields = ('id', 'shipping_address', 'lines', 'amount' ,'state', 'payment_status', 'date')
        read_only_fields = ('id', 'state', 'payment_status', 'date')
        depth = 1

    def create(self, validated_data):
        user = self._context.get('request').user

        address_data = validated_data.pop('shipping_address')
        address_data['user'] = user
        address = Address.objects.create(**address_data)

        lines = validated_data.pop('lines')
        validated_data['user'] = user
        validated_data['shipping_address_id'] = address.id
        order = Order.objects.create(**validated_data)

        for line in lines:
            line['order_id'] = order.id
            line['amount'] = line.get('product').final_amount * line.get('quantity')
            l = OrderLine.objects.create(**line)
            order.amount += line['amount']

        order.order_number = 'ORDER_%d'%order.id
        order.save()
        return order

    def update(self, instance, validated_data):
        print "Instance", instance
        print "validated data", validated_data

        address = instance.shipping_address
        for attr, value in validated_data.pop('shipping_address').iteritems():
            setattr(address, attr, value)
        address.save()

        line = instance.lines.all()[0]
        for attr, value in validated_data.pop('lines')[0].iteritems():
            setattr(line, attr, value)
        line.amount = line.product.final_amount * line.quantity
        line.save()

        instance.amount = line.product.final_amount * line.quantity
        
        return instance


class OrderCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    address1 = serializers.CharField(required=True)
    address2 = serializers.CharField(required=False)
    address3 = serializers.CharField(required=False)
    mobile = serializers.CharField(required=True)
    pincode = serializers.IntegerField(required=True)
    city_id = serializers.CharField(required=True)
    state_id = serializers.CharField(required=True)
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

    class Meta:
        fields = ('name', 'address1', 'address2', 'address3', 'mobile', 'pincode', 'city_id', 'state_id', 'product_id', 'quantity')

    def create(self, validated_data):
        print "validated_data", validated_data
        print "context", self._context.get('request').user
        user = self._context.get('request').user

        validated_data['city'] = validated_data.pop('city_id', '')
        validated_data['state'] = validated_data.pop('state_id', '')
        validated_data['user'] = user.id

        address = AddressSerializer(data=validated_data)
        address.is_valid(raise_exception=True)
        address_instance = address.save()
        print "address_instance", address_instance

        products = Product.objects.filter(id__in=[validated_data.get('product_id')])

        if len(products) == 0:
            raise serializers.ValidationError("Product not exist")

        order = OrderSerializer(data={
            'user': user.id,
            'shipping_address': address_instance.id,
            'amount': sum([p.final_amount for p in products])
        })
        order.is_valid(raise_exception=True)
        order_instance = order.save()
        print "order instance", order_instance
        order_line_data = []

        for product in products:
            order_line_data.append({
                'product': product.id,
                'quantity': validated_data.get('quantity'),
                'amount': product.final_amount,
                'order': order_instance.id
            })
        print "order_line_data", order_line_data
        order_lines = OrderLineSerializer(data=order_line_data, many=True)
        order_lines.is_valid(raise_exception=True)
        order_lines_instance = order_lines.save()
        print "order_lines_instance", order_lines_instance
        return order_instance
        # data['shipping_address']['user'] = request.user.id
        # data['user'] = request.user.id
        # data['amount'] = Product.objects.filter(id__in=[product.get('product') for product in data['order_lines']]).aggregate(Sum('discounted_price')).get('discounted_price__sum')

