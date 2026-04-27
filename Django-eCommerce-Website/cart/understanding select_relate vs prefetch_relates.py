class User(models.Model):
    name = models.CharField(max_length = 50)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "carts")

class Product(models.Model):
    name = models.CharField(max_length=50)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name ="items", on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Tag(models.Model):
    name = models.CharField(max_length=50)

carts = Cart.objects.select_related("user")

users = User.objects.prefetch_related("carts")

# Remember when we use preftech_related we are able to get the carts of a specific user,
# even though the foreignkey is defined in the cart model.This is a reverse Foreign
# Key relationship.

orders = Order.objects.prefetch_related("items")

class Category(BaseModel):
    category_name = models.CharField(max_length = 100)
    slug = models.SlugField(unique=True, blank=True, null=True, max+length=200)

    class Meta:
        ver