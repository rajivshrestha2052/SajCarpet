from rest_framework import serializers
from api.models.product import Product, ProductImage
from django.db import transaction

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class ProductPublicSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name',
            'description', 'price', 'discount_price', 'images'
        ]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'description', 'price', 'discount_price', 'stock',
            'is_active', 'created_at', 'updated_at', 'images'
        ]

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Selective image update logic
        if images_data is not None:
            existing_image_ids = []
            for image_data in images_data:
                image_id = image_data.get('id', None)

                if image_id:
                    # Update existing image
                    try:
                        image_instance = instance.images.get(id=image_id)
                        for attr, value in image_data.items():
                            setattr(image_instance, attr, value)
                        image_instance.save()
                        existing_image_ids.append(image_id)
                    except ProductImage.DoesNotExist:
                        pass
                else:
                    # Create new image
                    ProductImage.objects.create(product=instance, **image_data)

            # Delete images not included in the update payload
            instance.images.exclude(id__in=existing_image_ids).delete()

        return instance


