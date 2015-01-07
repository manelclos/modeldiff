from django.contrib.gis.db import models

from models import SaveGeomodeldiffMixin, SaveModeldiffMixin

class PersonModel(SaveModeldiffMixin, models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    surname = models.CharField(max_length=50, null=True, blank=True)

    objects = models.GeoManager()

    class Modeldiff:
        model_name = 'modeldiff.PersonModel'
        fields = ('name', 'surname',)

       
class PersonGeoModel(SaveGeomodeldiffMixin, models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    surname = models.CharField(max_length=50, null=True, blank=True)
    the_geom = models.PointField(srid=4326, null=True, blank=True)

    objects = models.GeoManager()

    class Modeldiff:
        model_name = 'modeldiff.PersonGeoModel'
        fields = ('name', 'surname',)
        geom_field = 'the_geom'
        geom_precision = 8


class TypeModel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)    

   
class ModelModel(models.Model):
    code = models.CharField(max_length=50, blank=False, null=False, 
                              unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)


class SensorModel(SaveModeldiffMixin, models.Model):
    model_code = models.ForeignKey(ModelModel, to_field="code", 
                                   db_column="model_code", null=True, 
                                   blank=True)
    type = models.ForeignKey(TypeModel, null=True, blank=True)

    class Modeldiff:
        model_name = 'modeldiff.SensorModel'
        fields = ('model_code', 'type')


class SensorGeoModel(SaveGeomodeldiffMixin, models.Model):
    model_code = models.ForeignKey(ModelModel, to_field="code", 
                                   db_column="model_code", null=True, 
                                   blank=True)
    type = models.ForeignKey(TypeModel, null=True, blank=True)
    the_geom = models.PointField(srid=4326, null=True, blank=True)

    objects = models.GeoManager()

    class Modeldiff:
        model_name = 'modeldiff.SensorGeoModel'
        fields = ('model_code', 'type')
        geom_field = 'the_geom'
        geom_precision = 8


class SensorObservationModel(SaveModeldiffMixin, models.Model):
    sensor = models.ForeignKey(SensorModel)
    value = models.IntegerField()
    
    class Modeldiff:
        model_name = 'modeldiff.SensorObservationModel'
        fields = ('sensor', 'value')
        parent_field = 'sensor'


class SensorObservationGeoModel(SaveModeldiffMixin, models.Model):
    sensor = models.ForeignKey(SensorGeoModel)
    value = models.IntegerField()
    
    class Modeldiff:
        model_name = 'modeldiff.SensorObservationGeoModel'
        fields = ('sensor', 'value')
        parent_field = 'sensor'
            

