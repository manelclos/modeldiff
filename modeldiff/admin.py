from django.contrib.gis import admin
from models import Modeldiff, Geomodeldiff
from leaflet.admin import LeafletGeoAdmin


from datetime import date

from django.contrib import admin
from django.db.models import get_app, get_models

class ModeldiffAdminListFilter(admin.SimpleListFilter):
    title = 'Model'
    parameter_name = 'model_name'

    def lookups(self, request, model_admin):
        app = get_app('salt')
        models_name = ()
        for model in get_models(app):
            if hasattr(model, 'Modeldiff') and not hasattr(model.Modeldiff, 'geom_field'):
                models_name = models_name + ((model.Modeldiff.model_name, model.Modeldiff.model_name,),)
                
        return models_name

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(model_name=self.value())
     
class GeomodeldiffAdminListFilter(ModeldiffAdminListFilter):

    def lookups(self, request, model_admin):
        app = get_app('salt')
        models_name = ()
        for model in get_models(app):
            if hasattr(model, 'Modeldiff') and hasattr(model.Modeldiff, 'geom_field'):
                models_name = models_name + ((model.Modeldiff.model_name, model.Modeldiff.model_name,),)
                
        return models_name
   

class ModeldiffAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'key', 'key_id', 'username', 'model_name',
                    'model_id', 'action', 'applied')
    search_fields = ('username', 'model_name', '=model_id',)
    list_filter = (ModeldiffAdminListFilter,)
         
admin.site.register(Modeldiff, ModeldiffAdmin)
 
 
class GeomodeldiffAdmin(LeafletGeoAdmin):
    list_display = ('date_created', 'username', 'model_name', 'model_id',
                    'action', 'applied')
    search_fields = ('username', 'model_name', '=model_id',)
    list_filter = (GeomodeldiffAdminListFilter,)
    
admin.site.register(Geomodeldiff, GeomodeldiffAdmin)
