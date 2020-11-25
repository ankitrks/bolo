from datetime import datetime
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.models import User

from rest_framework import serializers

from advertisement.models import Ad, ProductReview, Order, Product, Address, OrderLine, Brand, Tax


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'company_logo', 'poc', 'phone_number', 'email', 
                        'signed_contract_doc_file_url', 'signed_other_doc_file_url', 
                        'signed_nda_doc_file_url')
        read_only_fields = ('poc', 'phone_number', 'email', 
                        'signed_contract_doc_file_url', 'signed_other_doc_file_url', 
                        'signed_nda_doc_file_url')

class AdSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField(source='id', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_image = serializers.CharField(source='brand.company_logo', read_only=True)
    ad_video = serializers.CharField(source='video_file_url', read_only=True)
    cta = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    price = serializers.FloatField(source='product.final_amount', read_only=True)
    start_date = serializers.SerializerMethodField(read_only=True)
    end_date = serializers.SerializerMethodField(read_only=True)
    frequency = serializers.SerializerMethodField(read_only=True)
    brand_obj_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ad
        fields = ('ad_id', 'brand_name', 'brand_image', 'ad_video', 'thumbnail', 'ad_length', 'cta', 'type', 
                    'title', 'start_date', 'end_date', 'frequency', 'frequency_type', 'product_id', 'product_name', 
                    'price', 'ad_type', 'state', 'is_deleted', 'brand_obj_id')

    def get_cta(self, instance):
        return list(instance.cta.all().values('title', 'code', 'enable_time', 'action'))

    def get_type(self, instance):
        return 'ad'

    def get_start_date(self, instance):
        return datetime.strftime(instance.start_time, '%d-%m-%Y')

    def get_end_date(self, instance):
        if instance.end_time:
            return datetime.strftime(instance.end_time, '%d-%m-%Y')

    def get_frequency(self, instance):
        return list(instance.frequency.all().values('scroll', 'sequence'))

    def get_brand_obj_id(self, instance):
        return instance.brand.id

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ('name', 'percentage')

class ProductSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    product_id = serializers.CharField(source='id', read_only=True)
    product_title = serializers.CharField(source='name', read_only=True)
    product_description = serializers.CharField(source='description', read_only=True)
    rating_count = serializers.SerializerMethodField()
    discount_expiry = serializers.SerializerMethodField()
    brand = BrandSerializer()
    tax = TaxSerializer(source='taxes', many=True)

    class Meta:
        model = Product
        fields = ('product_id', 'product_title', 'product_description', 'product_images', 'rating_count', 'rating',
                    'currency', 'mrp', 'is_discounted', 'discounted_price', 'discount_expiry', 'brand', 'tax',
                    'amount_including_tax', 'total_tax')

        read_only_fields = ('amount_including_tax', 'total_tax')

    def get_product_images(self, instance):
        return list(instance.images.all().values_list('original_image', flat=True))

    def get_rating_count(self, instance):
        return intcomma(instance.rating_count)

    def get_discount_expiry(self, instance):
        if instance.discount_expiry:
            return datetime.strftime(instance.discount_expiry, "%d-%m-%y %H:%M:%S")
        return ''

    def to_representation(self, instance):
        data = super(ProductSerializer, self).to_representation(instance)
        review_count = instance.reviews.count()
        data.update({
            'rating': float(instance.rating),
            'mrp': float(instance.mrp),
            'discounted_price': float(instance.discounted_price),
            'rating_count': intcomma(review_count),
            'rating': sum([float(r.rating) for r in instance.reviews.all()])/review_count if review_count !=0 else 0
        })
        tax = data.get('tax')
        for t in data.get('tax'):
            t['value'] = instance.get_tax_value(t.get('percentage'))
        return data


class ReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = ProductReview
        fields = ('review_id', 'title', 'description', 'rating')

    def to_representation(self, instance):
        data = super(ReviewSerializer, self).to_representation(instance)
        data.update({
            'rating': float(instance.rating),
        })
        return data


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

    def to_representation(self, instance):
        data = super(OrderLineSerializer, self).to_representation(instance)
        data.update({
            'product': ProductSerializer(instance.product).data,
        })
        return data


class OrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True)
    shipping_address = AddressSerializer()
    user = UserSerializer(read_only=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'shipping_address', 'lines', 'amount' ,'state', 'payment_status', 'date', 'user')
        read_only_fields = ('id', 'payment_status', 'date', 'user')
        depth = 1

    def get_date(self, instance):
        return datetime.strftime(instance.date, '%d-%m-%Y')


    def create(self, validated_data):
        user = self._context.get('request').user

        address_data = validated_data.pop('shipping_address')
        address_data['user'] = user
        address = Address.objects.create(**address_data)

        lines = validated_data.pop('lines')
        validated_data['user'] = user
        validated_data['shipping_address_id'] = address.id
        order = Order.objects.create(**validated_data)

        order.amount = 0.0
        for line in lines:
            line['order_id'] = order.id
            line['amount'] = line.get('product').final_amount * line.get('quantity')
            l = OrderLine.objects.create(**line)
            order.amount += float(line['amount'])

        order.order_number = 'ORDER_%d'%order.id
        order.state = 'order_placed'
        order.save()
        return order

    def update(self, instance, validated_data):
        print "Instance", instance
        print "validated data", validated_data

        if validated_data.get('shipping_address'):
            address = instance.shipping_address
            for attr, value in validated_data.pop('shipping_address').iteritems():
                setattr(address, attr, value)
            address.save()

        if validated_data.get('lines'):
            line = instance.lines.all()[0]
            for attr, value in validated_data.pop('lines')[0].iteritems():
                setattr(line, attr, value)
            line.amount = line.product.final_amount * line.quantity
            line.save()

            instance.amount = line.product.final_amount * line.quantity
            instance.payment_gateway_order_id = None

        for attr, value in validated_data.iteritems():
            setattr(instance, attr, value)

        instance.save()
        
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
        fields = ('name', 'address1', 'address2', 'address3', 'mobile', 'pincode', 'city_id', 'state_id', 'product_id', 'quantity', 'email')

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

