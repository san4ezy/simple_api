# -*- coding: utf-8 -*-
import json
import signals
import django
from time import time
import datetime
#from django.db.models import query
#from django.core.serializers import serialize


def json_serialize(data, values=()):
    if isinstance(data, django.db.models.query.QuerySet):
        pass
    elif isinstance(data, django.db.models.Model):
        data = [data]
    else:
        return data
    response = []
    fields = data[0]._meta.get_all_field_names()
    for item in data:
        response_item = {}
        for field in fields:
            if (values and field in values) or not values:
                try:
                    v = item.__getattribute__(field)
                    if isinstance(v, datetime.date) or isinstance(v, datetime.time):
                        v = v.strftime('%d.%m.%Y')
                    elif isinstance(v, django.db.models.Model):
                        v = v.pk
                    response_item[field] = v
                except:
                    pass
        response.append(response_item)
    return response


class SimpleAPI(object):
    simple_api_id = "simple_api_id"
    description = "Simple API method"
    get = None

    def __init__(self, method=None):
        #signals.init_api_model.send(sender=self.__class__, name="SomeName")
        pass

    def get_response(self, request):
        response = None
        self.get = request.GET
        errs = self.validate_errors()
        if not errs:
            runtime = time()
            response = self.method()
            response = json_serialize(response)
            #if isinstance(response, django.db.models.query.QuerySet):
            #    response = django.core.serializers.serialize('json', response)
            #elif isinstance(response, django.db.models.Model):
            #    response = django.core.serializers.serialize('json', [response])
            #print response, type(response)
            runtime = round(time() - runtime, 3)
            response = send_response(status="ok", data=response, runtime=runtime)
        else:
            response = send_response(status="error", data=errs)
        return response

    def method(self):
        # it must returns a data
        return None

    def validate_errors(self):
        variables = [attr for attr in dir(self) if hasattr(self.__getattribute__(attr), 'simple_api_variable')]
        #get = request.GET
        keys = []
        for key, val in self.get.iteritems():
            if key in variables:
                key_obj = self.__getattribute__(key)
                if key_obj.is_type(val):
                    if key_obj.is_choices(val):
                        keys.append(key)
                        key_obj.set(val)
                    else:
                        return u"Unknown parameter`s value for %s" % key
                else:
                    return u"Wrong data type of '%s'" % key
            else:
                return u"Unknown parameter '%s'" % key
        for key in list(set(variables) - set(keys)):
            key_obj = self.__getattribute__(key)
            if not key_obj.blank:
                return u"Expected parameter '%s'" % key
            if key_obj.has_default():
                key_obj.set(key_obj.default)
        return None


def send_response(status, data=None, runtime=None):
    response = {
        "status": status,
        "data": data,
    }
    if runtime is not None:
        response['runtime'] = runtime
    return json.dumps(response)


class ModelAPI(SimpleAPI):
    simple_api_model_id = "simple_api_model_id"
    description = "Simple API model method"
    model = None
    action = None
    fields = []
    #use_model_blank = True
    #blank = []
    #not_blank = []

    def __init__(self, method):
        super(ModelAPI, self).__init__()
        self.action = method

    def router(self, request):
        if self.action == 'get':
            self.make_model_variables(False, [], ['id'])
            response =  super(ModelAPI, self).get_response(request)
        elif self.action == 'edit':
            self.make_model_variables(False, [], ['id'])
            response =  super(ModelAPI, self).get_response(request)
        elif self.action == 'make':
            self.make_model_variables(True, ['id'], [])
            response =  super(ModelAPI, self).get_response(request)
        elif self.action == 'delete':
            self.make_model_variables(False, [], ['id'])
            response =  super(ModelAPI, self).get_response(request)
        else:
            response = send_response(status='error', data='Unknown method %s for model %s' % (self.action, self.model))
        return response

    def make_model_variables(self, use_model_blank=True, blank=[], not_blank=[]):
        self.fields = self.model._meta.get_all_field_names()
        for attr in self.fields:
            field = self.model._meta.get_field_by_name(attr)[0]
            if attr in blank:
                _blank = True
            elif attr in not_blank:
                _blank = False
            #blank = False if attr == 'id' or attr == 'pk' else True
            elif use_model_blank:
                _blank = field.blank if hasattr(field, 'blank') else True
            else:
                _blank = True
            if isinstance(field, django.db.models.IntegerField) or \
            isinstance(field, django.db.models.AutoField) or \
            isinstance(field, django.db.models.fields.related.RelatedObject):
                setattr(self, attr, IntegerVariable(blank=_blank))
            elif isinstance(field, django.db.models.CharField) or \
            isinstance(field, django.db.models.TextField):
                setattr(self, attr, CharVariable(blank=_blank))
            elif isinstance(field, django.db.models.BooleanField):
                setattr(self, attr, BooleanVariable(blank=_blank))
            # ForeinKey and ManyToManyKey ?

    def method(self):
        if self.action == 'get':
            data = self.get_item()
        elif self.action == 'edit':
            data = self.edit_item()
        elif self.action == 'make':
            data = self.make_item()
        elif self.action == 'delete':
            data = self.delete_item()
        else:
            data = send_response(status='error', data='Unknown method %s for model %s' % (self.action, self.model))
        return data

    def get_item(self):
        try:
            data = self.model.objects.get(pk=self.id.value)
        except:
            data = 'The %s instance with id=%s does not exists' % (self.model.__name__, self.id.value)
        return data

    def edit_item(self):
        try:
            obj = self.model.objects.get(pk=self.id.value)
            for key, val in self.get.iteritems():
                if key in self.fields:
                    if not key == 'id' and not key == 'pk':
                        obj.__dict__[key] = self.__getattribute__(key).get()
            obj.save()
            data = 'The %s instance with id=%s was edited' % (self.model.__name__, self.id.value)
        except:
            data = 'The %s instance with id=%s does not exists' % (self.model.__name__, self.id.value)
        return data

    def make_item(self):
        obj = self.model()
        for key, val in self.get.iteritems():
            if key in self.fields:
                if not key == 'id' and not key == 'pk':
                    obj.__dict__[key] = self.__getattribute__(key).get()
        obj.save()
        data = 'The new %s instance was maked' % self.model.__name__
        return data

    def delete_item(self):
        try:
            self.model.objects.get(pk=self.id.value).delete()
            data = 'The %s instance with id=%s was deleted' % (self.model.__name__, self.id.value)
        except:
            data = 'The %s instance with id=%s does not exists' % (self.model.__name__, self.id.value)
        return data


class APIVariable():
    simple_api_variable = None
    method = "GET"
    value = None
    description = "API variable"
    data_type = None
    choices = []

    def set_parameter(self, value, default, dict):
        return dict[value] if value in dict else default

    def is_choices(self, value):
        if hasattr(self, 'choices'):
            if self.choices:
                if value in self.choices:
                    return True
                else:
                    return False
        return True

    def case(self, i):  # returns True or False if value is exists in choices in i place, or returns None if value does not exists
        if self.value in self.choices:
            if self.value == self.choices[i]:
                return True
            else:
                return False
        else:
            return None

    def has_default(self):
        pass

    def is_type(self, value):
        pass

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class IntegerVariable(APIVariable):
    def __init__(self, **kwargs):
        self.default = self.set_parameter("default", None, kwargs)
        self.blank = self.set_parameter("blank", False, kwargs)
        self.choices = self.set_parameter("choices", [], kwargs)
        self.data_type = 'integer'

    def is_type(self, value):
        try:
            value = int(value)
        except:
            value = False
        return value

    def has_default(self):
        return False if self.default is None else True


class CharVariable(APIVariable):
    def __init__(self, **kwargs):
        self.default = self.set_parameter("default", "", kwargs)
        self.blank = self.set_parameter("blank", False, kwargs)
        self.choices = self.set_parameter("choices", [], kwargs)
        self.data_type = 'string'

    def is_type(self, value):
        try:
            value = str(value)
        except:
            value = False
        return value

    def has_default(self):
        return False if self.default is "" else True


class BooleanVariable(APIVariable):
    def __init__(self, **kwargs):
        self.default = self.set_parameter("default", False, kwargs)
        self.blank = self.set_parameter("blank", False, kwargs)
        self.data_type = 'boolean'

    def is_type(self, value):
        if value == u"True" or value == u"False" or value == u"true" or value == u"false" or value == u"1" or value == u"0":
            return True
        else:
            return False

    def has_default(self):
        return True

    def case(self, i):
        return None

    def set(self, value):
        if value in ('0', 'false', 'False', ):
            self.value = False
        elif value in ('1', 'true', 'True', ):
            self.value = True


class Dispatcher():
    models = []

    def __init__(self):
        pass

    def register(self, model, **options):
        import inspect, sys
        for mod in inspect.getmembers(sys.modules[model.__name__], inspect.isclass):
            self.models.append(mod)


dispatcher = Dispatcher()