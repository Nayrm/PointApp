from django.contrib import admin
from .models import PointPiece, RepairType, PartType, DC, Associate, Route

admin.site.register(PointPiece)
admin.site.register(RepairType)
admin.site.register(PartType)
admin.site.register(DC)
admin.site.register(Associate)
admin.site.register(Route)
# Register your models here.
