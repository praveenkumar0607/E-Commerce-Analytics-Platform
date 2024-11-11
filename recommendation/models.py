from django.db import models

class Rating(models.Model):
    user_id = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)
    rating = models.FloatField()

    def __str__(self):
        return f'User: {self.user_id}, Product: {self.product_id}, Rating: {self.rating}'
