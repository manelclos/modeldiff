from django.contrib.gis.db import models
from django.db import models as models_non_contrib
from django.contrib.gis.utils.wkt import precision_wkt

import json


class ModeldiffMixin(models.Model):
    """
    Base model to save the changes to a model
    """
    date_created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=20, blank=True, null=True)
    key_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    model_id = models.IntegerField(blank=True, null=True)
    action = models.CharField(max_length=6)
    old_data = models.TextField()
    new_data = models.TextField()
    applied = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Modeldiff(ModeldiffMixin, models.Model):
    pass


class Geomodeldiff(ModeldiffMixin, models.Model):
    the_geom = models.GeometryField(srid=4326, null=True, blank=True)
    objects = models.GeoManager()


class SaveModeldiffMixin(models.Model):
    """
    Use real=True to access the real save function
    otherwise the Modeldiff logic will apply
    """
    def save(self, *args, **kwargs):
        # see if we need to save the object (real = True)
        # or should generate a Modeldiff (real = False)
        real = kwargs.get('real', False)

        if real:
            # call original handler
            kwargs.pop('real')
            super(SaveModeldiffMixin, self).save(*args, **kwargs)
            return

        fields = self.Modeldiff.fields

        diff = Modeldiff()
        diff.model_name = self.Modeldiff.model_name
        if hasattr(self, 'username'):
            diff.username = self.username

        if self.pk:
            diff.model_id = self.pk
            diff.action = 'update'
            # get original object in database
            original = self.__class__.objects.get(pk=self.pk)

            # compare original and current (self)
            old_values = {}
            new_values = {}
            for k in fields:
                old_value = getattr(original, k)
                new_value = getattr(self, k)               
                
                field_conf = self._meta.get_field_by_name(k)
                if isinstance(field_conf[0], models_non_contrib.fields.related.ForeignKey):
                    if len(field_conf[0].to_fields)>0:
                        old_value = getattr(old_value, field_conf[0].to_fields[0])
                        new_value = getattr(new_value, field_conf[0].to_fields[0])
                    else:
                        old_value =  old_value.pk
                        new_value =  new_value.pk
                
                old_values[k] = old_value               
                if not new_value == old_value:
                    new_values[k] = new_value

            diff.old_data = json.dumps(old_values)
            diff.new_data = json.dumps(new_values)
            diff.save()
        else:
            diff.action = 'add'
            # save all new values
            new_values = {}
            for k in fields:
                new_value = getattr(self, k)
                                               
                field_conf = self._meta.get_field_by_name(k)
                if isinstance(field_conf[0], models_non_contrib.fields.related.ForeignKey):
                    if len(field_conf[0].to_fields)>0:
                        new_value = getattr(new_value, field_conf[0].to_fields[0])
                    else:
                        new_value =  new_value.pk
                
                new_values[k] = new_value
                
            diff.new_data = json.dumps(new_values)
            diff.save()

        super(SaveModeldiffMixin, self).save(*args, **kwargs)
        if diff.model_id is None and self.pk:
            diff.model_id = self.pk
            diff.save()

    class Meta:
        abstract = True


class SaveGeomodeldiffMixin(models.Model):
    """
    Use real=True to access the real save function
    otherwise the Modeldiff logic will apply
    """
    def save(self, *args, **kwargs):
        # see if we need to save the object (real = True)
        # or should generate a Modeldiff (real = False)
        real = kwargs.get('real', False)

        if real:
            # call original handler
            kwargs.pop('real')
            super(SaveGeomodeldiffMixin, self).save(*args, **kwargs)
            return

        fields = self.Modeldiff.fields
        geom_field = self.Modeldiff.geom_field
        geom_precision = self.Modeldiff.geom_precision

        diff = Geomodeldiff()
        diff.model_name = self.Modeldiff.model_name
        if hasattr(self, 'username'):
            diff.username = self.username

        if self.pk:
            diff.model_id = self.pk
            diff.action = 'update'
            # get original object in database
            original = self.__class__.objects.get(pk=self.pk)

            # compare original and current (self)
            old_values = {}
            new_values = {}
            for k in fields:
                old_value = getattr(original, k)
                new_value = getattr(self, k)
                                
                field_conf = self._meta.get_field_by_name(k)
                if isinstance(field_conf[0], models_non_contrib.fields.related.ForeignKey):
                    if len(field_conf[0].to_fields)>0:
                        old_value = getattr(old_value, field_conf[0].to_fields[0])
                        new_value = getattr(new_value, field_conf[0].to_fields[0])
                    else:
                        old_value =  old_value.pk
                        new_value =  new_value.pk
                        
                old_values[k] = old_value
                if not new_value == old_value:
                    new_values[k] = new_value

            # save original geometry
            geom = getattr(original, geom_field)
            if geom:
                old_values[geom_field] = precision_wkt(geom, geom_precision)
            else:
                old_values[geom_field] = None

            # compare original and new geometry
            new_geom = getattr(self, geom_field)
            diff.the_geom = new_geom
            if new_geom:
                new_geom_value = precision_wkt(new_geom, geom_precision)
            else:
                new_geom_value = None

            if not new_geom_value == old_values[geom_field]:
                new_values[geom_field] = new_geom_value
            
            print old_values
            
            diff.old_data = json.dumps(old_values)
            diff.new_data = json.dumps(new_values)
            diff.save()
        else:
            diff.action = 'add'
            # save all new values
            new_values = {}
            for k in fields:
                
                new_value = getattr(self, k)
                                               
                field_conf = self._meta.get_field_by_name(k)
                if isinstance(field_conf[0], models_non_contrib.fields.related.ForeignKey):
                    if len(field_conf[0].to_fields)>0:
                        new_value = getattr(new_value, field_conf[0].to_fields[0])
                    else:
                        new_value =  new_value.pk
                
                new_values[k] = new_value
                        
                
            new_geom = getattr(self, geom_field)
            diff.the_geom = new_geom
            if new_geom:
                new_values[geom_field] = precision_wkt(new_geom,
                                                       geom_precision)
            diff.new_data = json.dumps(new_values)
            diff.save()

        super(SaveGeomodeldiffMixin, self).save(*args, **kwargs)
        if diff.model_id is None and self.pk:
            diff.model_id = self.pk
            diff.save()

    def delete(self, *args, **kwargs):
        real = kwargs.get('real', False)

        if real:
            # call original handler
            kwargs.pop('real')
            super(SaveGeomodeldiffMixin, self).delete(*args, **kwargs)
            return

        fields = self.Modeldiff.fields
        geom_field = self.Modeldiff.geom_field
        geom_precision = self.Modeldiff.geom_precision

        diff = Geomodeldiff()
        diff.model_name = self.Modeldiff.model_name
        if hasattr(self, 'username'):
            diff.username = self.username

        if self.pk:
            diff.model_id = self.pk
            diff.action = 'delete'
            # get original object in database
            original = self.__class__.objects.get(pk=self.pk)

            # save old values
            old_values = {}
            for k in fields:
                old_value = getattr(self, k)
                old_values[k] = old_value

            # save geometry
            geom = getattr(self, geom_field)
            diff.the_geom = geom
            if geom:
                old_values[geom_field] = precision_wkt(geom, geom_precision)
            else:
                old_values[geom_field] = None

            diff.old_data = json.dumps(old_values)
            diff.save()

        super(SaveGeomodeldiffMixin, self).delete(*args, **kwargs)

    class Meta:
        abstract = True
