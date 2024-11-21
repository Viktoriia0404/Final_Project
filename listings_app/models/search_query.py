from django.contrib.auth.models import User
from django.db import models


class SearchQuery(models.Model):
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='search_query', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    rooms_min = models.FloatField(null=True, blank=True)
    rooms_max = models.FloatField(null=True, blank=True)
    property_type = models.CharField(max_length=50,
                                     choices=[
                                         ('apartment', 'Apartment'),
                                         ('house', 'House'),
                                         ('studio', 'Studio'), ],
                                     null=True, blank=True)
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('title', 'description',
                           'location', 'city', 'rooms_min',
                           'rooms_max', 'property_type', 'price_min',
                           'price_max')

    def save(self, *args, **kwargs):

        query = SearchQuery.objects.filter(
            owner=self.owner,
            title=self.title,
            description=self.description,
            location=self.location,
            city=self.city,
            rooms_min=self.rooms_min,
            rooms_max=self.rooms_max,
            property_type=self.property_type,
            price_min=self.price_min,
            price_max=self.price_max
        ).first()
        if query and query != self:
            query.count += 1
            query.save()
        else:
            super(SearchQuery, self).save(*args, **kwargs)


