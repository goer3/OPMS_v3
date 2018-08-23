from django.contrib import admin
from .models import *

# Register your models here
admin.site.register(TroubleTag)
admin.site.register(TroubleRecord)
admin.site.register(DeployRecord)
admin.site.register(OpsEvent)
