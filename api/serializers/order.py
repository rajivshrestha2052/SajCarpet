from rest_framework import serializers
from api.models.order import Order, OrderItem
from api.models.product import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # make writable by removing read_only=True
    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'created_at', 'items']
        read_only_fields = ['customer', 'status', 'created_at']
    def validate(self, data):
        items = data.get('items', [])
        for item in items:
            product = item['product']
            quantity = item['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for product '{product.name}'. Available: {product.stock}, requested: {quantity}."
                )
        return data
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = item_data.get('price', product.price)
            # Reduce stock
            product.stock -= quantity
            product.save()
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
        return order
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update order fields except items
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            # Map existing items by product id
            existing_items = {item.product.id: item for item in instance.items.all()}

            # Track products to adjust stock after processing all items
            stock_adjustments = {}

            # Process new/updated items
            new_product_ids = set()
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                price = item_data.get('price', product.price)
                new_product_ids.add(product.id)

                existing_item = existing_items.get(product.id)

                if existing_item:
                    qty_diff = quantity - existing_item.quantity
                    if qty_diff > 0 and product.stock < qty_diff:
                        raise serializers.ValidationError(
                            f"Not enough stock for product '{product.name}'. Available: {product.stock}, additional requested: {qty_diff}."
                        )
                    # Update existing item
                    existing_item.quantity = quantity
                    existing_item.price = price
                    existing_item.save()
                    stock_adjustments[product.id] = stock_adjustments.get(product.id, 0) - qty_diff
                else:
                    # New item
                    if product.stock < quantity:
                        raise serializers.ValidationError(
                            f"Not enough stock for product '{product.name}'. Available: {product.stock}, requested: {quantity}."
                        )
                    OrderItem.objects.create(order=instance, product=product, quantity=quantity, price=price)
                    stock_adjustments[product.id] = stock_adjustments.get(product.id, 0) - quantity

            # Remove items that are not in new data
            for product_id, existing_item in existing_items.items():
                if product_id not in new_product_ids:
                    # Return stock for removed items
                    stock_adjustments[product_id] = stock_adjustments.get(product_id, 0) + existing_item.quantity
                    existing_item.delete()

            # Apply stock adjustments
            for product_id, qty_change in stock_adjustments.items():
                product = Product.objects.get(id=product_id)
                product.stock += qty_change
                product.save()

        return instance
