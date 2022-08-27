from rest_framework.serializers import ModelSerializer

from snap_analyzer_django.models import GeneralCluster


class ClusterSerializer(ModelSerializer):
    class Meta:
        model = GeneralCluster
        fields = ['serial_number_cluster',
                  'date_timestamp',
                  'product_name',
                  'type',
                  'code_level',
                  'number_of_enclosure',
                  'id']
