from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, help_text="Lucide icon name")
    description = models.CharField(max_length=255, blank=True)
    trending = models.BooleanField(default=False)

    DEFAULT_CATEGORIES = [
        {
            'name': 'Ilmiy va Akademik xizmatlar',
            'slug': 'ilmiy-va-akademik-hizmatlar',
            'icon': 'book-open',
            'description': 'Tadqiqot, yozuv va akademik xizmatlar.',
            'trending': True,
        },
        {
            'name': 'Dizayn',
            'slug': 'dizayn',
            'icon': 'palette',
            'description': 'Logotip, brending va UI dizayn yechimlari.',
            'trending': True,
        },
        {
            'name': 'Dasturlash xizmatlari',
            'slug': 'dasturlash-xizmatlari',
            'icon': 'code',
            'description': 'Web, mobil va backend dasturlash.',
            'trending': True,
        },
        {
            'name': '3D Dizayn va Vizualizatsiya',
            'slug': '3d-dizayn-va-vizualizatsiya',
            'icon': 'cube',
            'description': '3D modellar, animatsiya va vizualizatsiya.',
            'trending': True,
        },
        {
            'name': 'Marketing va SMM',
            'slug': 'marketing-va-smm',
            'icon': 'megaphone',
            'description': 'Raqamli marketing, reklama va ijtimoiy media.',
            'trending': True,
        },
        {
            'name': 'Audio va Video',
            'slug': 'audio-va-video',
            'icon': 'video',
            'description': 'Ovoz, video montaj va multimedia xizmatlari.',
            'trending': True,
        },
        {
            'name': 'Biznes',
            'slug': 'biznes',
            'icon': 'briefcase',
            'description': 'Konsalting, biznes-reja va moliyaviy xizmatlar.',
            'trending': False,
        },
        {
            'name': 'AI xizmatlari',
            'slug': 'ai-xizmatlari',
            'icon': 'cpu',
            'description': 'Sun’iy intellekt va avtomatlashtirish xizmatlari.',
            'trending': True,
        },
        {
            'name': 'Telegram botlar',
            'slug': 'telegram-botlar',
            'icon': 'message-circle',
            'description': 'Telegram bot ishlab chiqish va integratsiyalar.',
            'trending': False,
        },
        {
            'name': 'Mobil ilovalar',
            'slug': 'mobil-ilovalar',
            'icon': 'smartphone',
            'description': 'iOS, Android va cross-platform mobil dasturlar.',
            'trending': False,
        },
        {
            'name': 'Web saytlar',
            'slug': 'web-saytlar',
            'icon': 'monitor',
            'description': 'Web saytlar, portallar va e-commerce tizimlar.',
            'trending': False,
        },
        {
            'name': 'UI/UX Dizayn',
            'slug': 'ui-ux-dizayn',
            'icon': 'layout',
            'description': 'Tajribali va zamonaviy UI/UX dizayn ishlari.',
            'trending': False,
        },
        {
            'name': 'AI Promptlar',
            'slug': 'ai-promptlar',
            'icon': 'sparkles',
            'description': 'AI uchun maxsus promptlar va kontent yaratish.',
            'trending': False,
        },
        {
            'name': 'Video kurslar',
            'slug': 'video-kurslar',
            'icon': 'play-circle',
            'description': 'Online kurslar va ta’lim materiallari.',
            'trending': False,
        },
        {
            'name': 'Source code',
            'slug': 'source-code',
            'icon': 'code',
            'description': 'Kod namunalari va dasturiy taʼminot yechimlari.',
            'trending': False,
        },
        {
            'name': 'Pluginlar',
            'slug': 'pluginlar',
            'icon': 'puzzle',
            'description': 'Integratsiya va plagin yechimlari.',
            'trending': False,
        },
        {
            'name': 'Scriptlar',
            'slug': 'scriptlar',
            'icon': 'terminal',
            'description': 'Avtomatlashtirish va skript yozish xizmatlari.',
            'trending': False,
        },
    ]

    DEFAULT_SUBCATEGORIES = {
        'dasturlash-xizmatlari': [
            {'name': 'Web dasturlash', 'slug': 'web-dasturlash', 'description': 'Web ilovalar va saytlar yaratish.'},
            {'name': 'Backend xizmatlari', 'slug': 'backend-xizmatlari', 'description': 'Server va API arxitekturasi.'},
            {'name': 'Frontend dizayn', 'slug': 'frontend-dizayn', 'description': 'Interfeys va tajriba dizayni.'},
        ],
        'web-saytlar': [
            {'name': 'E-commerce saytlar', 'slug': 'e-commerce-saytlar', 'description': 'Onlayn savdo va do‘kon saytlar.'},
            {'name': 'Portfolio saytlar', 'slug': 'portfolio-saytlar', 'description': 'Shaxsiy va brend saytlar.'},
            {'name': 'Landing sahifalar', 'slug': 'landing-sahifalar', 'description': 'Sotuvga yo‘naltirilgan sahifalar.'},
        ],
        'ui-ux-dizayn': [
            {'name': 'Mobil UI/UX', 'slug': 'mobil-ui-ux', 'description': 'Mobil ilovalar uchun dizayn.'},
            {'name': 'Veb UI/UX', 'slug': 'veb-ui-ux', 'description': 'Veb tajriba va dizayn.'},
        ],
        'ai-xizmatlari': [
            {'name': 'Chatbotlar', 'slug': 'chatbotlar', 'description': 'Soha uchun sun’iy intellekt yechimlari.'},
            {'name': 'AI integratsiyalar', 'slug': 'ai-integratsiyalar', 'description': 'Tizimlarga AI integratsiyalari.'},
        ],
        'telegram-botlar': [
            {'name': 'Xabar botlari', 'slug': 'xabar-botlari', 'description': 'Telegram xabar yuborish botlari.'},
            {'name': 'Ma’lumot botlari', 'slug': 'malumot-botlari', 'description': 'Qidiruv va ma’lumot botlari.'},
        ],
    }

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @classmethod
    def seed_default_categories(cls):
        for category_data in cls.DEFAULT_CATEGORIES:
            category, created = cls.objects.get_or_create(
                slug=category_data['slug'],
                defaults={
                    'name': category_data['name'],
                    'icon': category_data['icon'],
                    'description': category_data['description'],
                    'trending': category_data['trending'],
                }
            )
            if not created:
                updated = False
                for field in ['name', 'icon', 'description', 'trending']:
                    if getattr(category, field) != category_data[field]:
                        setattr(category, field, category_data[field])
                        updated = True
                if updated:
                    category.save()

            for sub_data in cls.DEFAULT_SUBCATEGORIES.get(category.slug, []):
                Subcategory.objects.get_or_create(
                    category=category,
                    slug=sub_data['slug'],
                    defaults={
                        'name': sub_data['name'],
                        'description': sub_data['description'],
                    }
                )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Subkategoriya"
        verbose_name_plural = "Subkategoriyalar"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Product(models.Model):
    class ProductType(models.TextChoices):
        SOURCE_CODE = "SOURCE_CODE", "Source Code"
        DESIGN = "DESIGN", "Design"
        TEMPLATE = "TEMPLATE", "Template"
        MODEL_3D = "MODEL_3D", "3D Model"
        AI_PROMPT = "AI_PROMPT", "AI Prompt"
        COURSE = "COURSE", "Video Course"
        EBOOK = "EBOOK", "E-book"
        MOBILE_APP = "MOBILE_APP", "Mobile App"
        WEB_SCRIPT = "WEB_SCRIPT", "Web Script"
        BOT = "BOT", "Bot"
        PLUGIN = "PLUGIN", "Plugin"

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    preview_image = models.ImageField(upload_to="products/previews/")
    demo_url = models.URLField(blank=True, null=True)
    
    tags = models.CharField(max_length=255, help_text="Comma separated tags")
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_sold = models.BooleanField(default=False)
    sales_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def _generate_unique_slug(self):
        slug_base = slugify(self.title)
        slug = slug_base
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="products/files/")
    version = models.CharField(max_length=20, default="1.0.0")
    changelog = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot fayli"
        verbose_name_plural = "Mahsulot fayllari"

    def __str__(self):
        return f"{self.product.title} - {self.version}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    notify_on_discount = models.BooleanField(default=True)
    notify_on_update = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Istaklar ro'yxati"
        verbose_name_plural = "Istaklar ro'yxati"

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"
