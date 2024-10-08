def representation_item(instance):
    data = dict()
    data["id"] = instance.id
    data["name"] = instance.name
    data["description"] = instance.description
    data["price"] = instance.price
    data["hot_price"] = instance.hot_price
    data["thumbnail"] = instance.thumbnail
    data["created_at"] = instance.created_at
    data["updated_at"] = instance.updated_at
    data["deleted_at"] = instance.deleted_at
    data["category_id"] = instance.category_id
    data["category"] = instance.category.name

    images = [image.url for image in instance.images.all()]
    for variant in instance.variants.all():
        images.append(variant.image)
    data["images"] = images

    data["attributes"] = {
        attribute.name: [value.value for value in attribute.values.all()]
        for attribute in instance.attributes.all()
    }
    data["variants"] = [
        {
            "price": variant.price,
            "hot_price": variant.hot_price,
            "image": variant.image,
            "attributes": {
                attribute.item_attribute_value.attribute.name: attribute.item_attribute_value.value
                for attribute in variant.attributes.all()
            },
        }
        for variant in instance.variants.all()
    ]

    return data
