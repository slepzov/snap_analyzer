from django.contrib import admin
from snap_analyzer_django.models import GeneralCluster, EnclosureModel, DriveModel, NodeModel

admin.site.register(GeneralCluster)
admin.site.register(EnclosureModel)
admin.site.register(NodeModel)
admin.site.register(DriveModel)
