from django.db import models

# model for Product's Category
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='sub_categories')

    class Meta:
        unique_together = ('slug','parent')
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


