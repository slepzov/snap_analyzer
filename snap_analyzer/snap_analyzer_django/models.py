from django.db import models


class GeneralCluster(models.Model):
    serial_number_cluster = models.CharField(max_length=10)
    date_timestamp = models.CharField(max_length=40)
    product_name = models.CharField(max_length=40)
    type = models.CharField(max_length=40)
    code_level = models.CharField(max_length=40)
    number_of_enclosure = models.IntegerField()


class EnclosureModel(models.Model):
    serial_number_cluster = models.CharField(max_length=10)
    date_timestamp = models.CharField(max_length=40)
    id_enclosure = models.CharField(max_length=40)
    type = models.CharField(max_length=40)
    temperature = models.CharField(max_length=40)
    total_PSUs = models.CharField(max_length=40)
    product_MTM_enclosure = models.CharField(max_length=40)
    serial_number_enclosure = models.CharField(max_length=40)
    status_enclosure = models.CharField(max_length=40)
    online_PSUs = models.CharField(max_length=40)
    drive_slots = models.CharField(max_length=40)
    fault_LED = models.CharField(max_length=40)
    identify_LED = models.CharField(max_length=40)
    total_canisters = models.CharField(max_length=40)
    online_canisters = models.CharField(max_length=40)
    cluster = models.ForeignKey(GeneralCluster, on_delete=models.CASCADE, null=True)
