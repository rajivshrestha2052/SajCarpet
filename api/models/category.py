from django.db import models

# model for Product's Category
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
       
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


