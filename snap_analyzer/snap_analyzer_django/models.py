from django.db import models


class GeneralCluster(models.Model):
    serial_number_cluster = models.CharField(max_length=10)
    date_timestamp = models.CharField(max_length=40)
    product_name = models.CharField(max_length=40)
    type = models.CharField(max_length=40)
    code_level = models.CharField(max_length=40)
    number_of_enclosure = models.IntegerField()
