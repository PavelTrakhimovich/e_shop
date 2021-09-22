from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()
#используем того юзера который указан у нас в settings.AUTH_USER_MODEL

#category
#product
#cartproduct
#cart
#order
#customer

def get_url_product(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model':ct_model, 'slug' : obj.slug})


class LatestProductManager:

    @staticmethod
    def get_products_for_mainpage(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products =[]
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),reverse=True)
        return products


class LatestProducts:

    objects = LatestProductManager()


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Name Category')
    slug = models.SlugField(unique=True) #/category/nootebook <-- its slug

    def __str__(self): # for admin
        return self.name


class Product(models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)# Связь с категорией(ForeignKey внешний ключ)(on_delete)иструкция на случай удаления продукта(CASCADE удаляет все связи)
    title = models.CharField(max_length=255, verbose_name='Title')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Image')
    description = models.TextField(verbose_name='Description', null=True)
    price = models.DecimalField( max_digits=9, decimal_places=2, verbose_name='Price')#decimal_places - цифры после запятой
    
    def __str__(self):
        return self.title


class Notebook(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Type display')
    precessor_freq = models.CharField(max_length=255, verbose_name='Processor freq')
    ram = models.CharField(max_length=255,verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Time without charge')
 
    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_url_product(self, 'product_detail')
    

class SmartPhone(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Type display')
    resolution = models.CharField(max_length=255, verbose_name='Resolution')
    accum_volume = models.CharField(max_length=255, verbose_name='Accum volue')
    ram = models.CharField(max_length=255,verbose_name='RAM')
    sd = models.BooleanField(default=True)
    sd_volume_max = models.CharField(max_length=255, verbose_name='Max volume sdcard')
    main_cam_mp = models.CharField(max_length=255, verbose_name='MP of main camera')
    front_cam_mp = models.CharField(max_length=255, verbose_name='MP of front camera')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_url_product(self, 'product_detail')


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Customer', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveBigIntegerField(default=1)# сколько товаров по умолчанию
    final_price = models.DecimalField( max_digits=9, decimal_places=2, verbose_name='Final price')

    def __str__(self):
        return "Product {}".format(self.product.title)#для корзины


class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Owner', on_delete=models.CASCADE)
    prodeuct = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveBigIntegerField(default=0)#количество уникальных обьекстов в корзине
    final_price =  models.DecimalField( max_digits=9, decimal_places=2, verbose_name='Final price')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Phone number')
    address = models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return "User {}".format(self.user.first_name, self.user.last_name) # находится в класс User
