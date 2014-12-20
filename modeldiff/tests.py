from django.test import TestCase
from django.contrib.gis.utils.wkt import precision_wkt

import json

from test_models import PersonModel, PersonGeoModel
from test_models import TypeModel, ModelModel, SensorModel, SensorGeoModel
from models import Modeldiff, Geomodeldiff


class ModeldiffTests(TestCase):

    def setUp(self):
                               
        PersonModel.objects.create(name='Foo', surname='Doe')
        PersonGeoModel.objects.create(name='Foo', surname='Doe', 
                                   the_geom='POINT (0 0)')
        
        type = TypeModel.objects.create(name='AAA')                
        model = ModelModel.objects.create(code="123ABC", name='Arduino')
        SensorModel.objects.create(model_code=model, type=type)
        
        SensorGeoModel.objects.create(model_code=model, type=type,
                                   the_geom='POINT (0 0)')

    def print_diff(self, diff):
        import sys
        print >> sys.stderr, '  ---------'
        print >> sys.stderr, '  id:', diff.id
        print >> sys.stderr, '  date_created:', diff.date_created
        print >> sys.stderr, '  action:', diff.action
        print >> sys.stderr, '  model_id:', diff.model_id
        print >> sys.stderr, '  model_name:', diff.model_name
        print >> sys.stderr, '  old_data:', diff.old_data
        print >> sys.stderr, '  new_data:', diff.new_data
        if hasattr(diff, 'the_geom'):
            print >> sys.stderr, '  the_geom:', diff.the_geom
        print >> sys.stderr, '  ---------'


    def test_creation_diff_exists(self):
        diff = Modeldiff.objects.get(pk=1)
        self.assertEqual(diff.id, 1)
        self.assertEqual(diff.action, 'add')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(diff.model_name, 'modeldiff.PersonModel')
        self.assertEqual(diff.old_data, '')
        self.assertEqual(json.loads(diff.new_data),
                         {'name': 'Foo', 'surname': 'Doe'})
            
    def test_creation_foreignkey_diff_exists(self):
        diff = Modeldiff.objects.get(pk=2)
        self.assertEqual(diff.id, 2)
        self.assertEqual(diff.action, 'add')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(diff.model_name, 'modeldiff.SensorModel')
        self.assertEqual(diff.old_data, '')
          
        self.assertEqual(json.loads(diff.new_data),
                         {u'model_code': u'123ABC', u'type': 1})
  
    def test_creation_geo_diff_exists(self):
        diff = Geomodeldiff.objects.get(pk=1)
        self.assertEqual(diff.id, 1)
        self.assertEqual(diff.action, 'add')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(diff.model_name, 'modeldiff.PersonGeoModel')
        self.assertEqual(diff.old_data, '')
        self.assertEqual(json.loads(diff.new_data),
                         {'name': 'Foo', 'surname': 'Doe',
                          'the_geom': 'POINT(0.00000000 0.00000000)'})
        self.assertEqual(precision_wkt(diff.the_geom, 8),
                         'POINT(0.00000000 0.00000000)')
                
    def test_creation_geo_foreignkey_diff_exists(self):
        diff = Geomodeldiff.objects.get(pk=2)
        self.assertEqual(diff.id, 2)
        self.assertEqual(diff.action, 'add')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(diff.model_name, 'modeldiff.SensorGeoModel')
        self.assertEqual(diff.old_data, '')
          
        self.assertEqual(json.loads(diff.new_data),
                         {u'model_code': u'123ABC', u'type': 1,
                          'the_geom': 'POINT(0.00000000 0.00000000)'})
        self.assertEqual(precision_wkt(diff.the_geom, 8),
                         'POINT(0.00000000 0.00000000)')    
         
 
    def test_modify_model(self):
        person = PersonModel.objects.get(pk=1)
        self.assertEqual(person.pk, 1)
        
        person.name = 'Bar'
        person.save()
  
        diff = Modeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'name': u'Foo', u'surname': u'Doe'})
        self.assertEqual(json.loads(diff.new_data), {'name': 'Bar'})
  
        person.name = 'John'
        person.save()
        
        diff = Modeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {'name': 'Bar', 'surname': 'Doe'})
        self.assertEqual(json.loads(diff.new_data), {'name': 'John'})
 
 
    def test_modify_model_foreignkey(self):
        sensor = SensorModel.objects.get(pk=1)
        self.assertEqual(sensor.pk, 1)
        sensor.type = TypeModel.objects.create(name='BBB')                
        sensor.model_code = ModelModel.objects.create(code="456ABC", name='Arduino2')
        sensor.save()
          
        diff = Modeldiff.objects.latest('id')         
          
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
          
        self.assertEqual(json.loads(diff.old_data),
                         {u'model_code': u'123ABC', u'type': 1})
        self.assertEqual(json.loads(diff.new_data),
                         {u'model_code': u'456ABC', u'type': 2})

        
    def test_modify_geo_model(self):
        person = PersonGeoModel.objects.get(pk=1)
        self.assertEqual(person.pk, 1)
        
        person.name = 'Bar'
        person.save()

  
        diff = Geomodeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'name': u'Foo', u'surname': u'Doe',
                          u'the_geom': u'POINT(0.00000000 0.00000000)'})
        self.assertEqual(json.loads(diff.new_data), {'name': 'Bar'})
  
        person.name = 'John'
        person.save()
        
        diff = Geomodeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {'name': 'Bar', 'surname': 'Doe',
                          u'the_geom': u'POINT(0.00000000 0.00000000)'})
        self.assertEqual(json.loads(diff.new_data), {'name': 'John'})
 
    def test_modify_geo_model_foreignkey(self):
        sensor = SensorGeoModel.objects.get(pk=1)
        self.assertEqual(sensor.pk, 1)
        sensor.type = TypeModel.objects.create(name='BBB')                
        sensor.model_code = ModelModel.objects.create(code="456ABC", name='Arduino2')
        sensor.save()
  
        diff = Geomodeldiff.objects.latest('id')
         
        self.assertEqual(diff.action, 'update')
        self.assertEqual(diff.model_id, 1)
 
        self.assertEqual(json.loads(diff.old_data),
                         {u'model_code': u'123ABC', u'type': 1,
                          u'the_geom': u'POINT(0.00000000 0.00000000)'
                          })
        self.assertEqual(json.loads(diff.new_data),
                         {u'model_code': u'456ABC', u'type': 2
                          })

    def test_delete_model(self):
        person = PersonModel.objects.get(pk=1)
        self.assertEqual(person.pk, 1)
        person.delete()
  
        diff = Modeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'delete')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'name': u'Foo', u'surname': u'Doe'})
        self.assertEqual(diff.new_data, '')
         
    def test_delete_geo_model(self):
        person = PersonGeoModel.objects.get(pk=1)
        self.assertEqual(person.pk, 1)
        person.delete()
   
        diff = Geomodeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'delete')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'name': u'Foo', u'surname': u'Doe',
                          u'the_geom': u'POINT(0.00000000 0.00000000)'})
        self.assertEqual(diff.new_data, '')
 
    def test_delete_model_foreignkey(self):
        sensor = SensorModel.objects.get(pk=1)
        self.assertEqual(sensor.pk, 1)
        sensor.delete()
  
        diff = Modeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'delete')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'model_code': u'123ABC', u'type': 1
                          })
        self.assertEqual(diff.new_data, '')
        
    def test_delete_geo_model_foreignkey(self):
        sensor = SensorGeoModel.objects.get(pk=1)
        self.assertEqual(sensor.pk, 1)
        sensor.delete()
    
        diff = Geomodeldiff.objects.latest('id')
        self.assertEqual(diff.action, 'delete')
        self.assertEqual(diff.model_id, 1)
        self.assertEqual(json.loads(diff.old_data),
                         {u'model_code': u'123ABC', u'type': 1,
                          u'the_geom': u'POINT(0.00000000 0.00000000)'})
        self.assertEqual(diff.new_data, '')
        

