from django.contrib.gis.db import models

from models import SaveGeomodeldiffMixin, SaveModeldiffMixin


class PersonModel(SaveGeomodeldiffMixin, models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    surname = models.CharField(max_length=50, null=True, blank=True)
    employment = models.ForeignKey(EmploymentModel, null=True, blank=True)
    car_number = models.ForeignKey(Carrer, to_field="number", 
                                   db_column="car_number", null=True, 
                                   blank=True)
    the_geom = models.PointField(srid=4326, null=True, blank=True)

    objects = models.GeoManager()

    class Modeldiff:
        model_name = 'modeldiff.PersonModel'
        fields = ('name', 'surname',)
        geom_field = 'the_geom'
        geom_precision = 8
        

class EmploymentModel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    
                
class CarModel(models.Model):
    number = models.CharField(max_length=50, blank=False, null=False, 
                              unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
