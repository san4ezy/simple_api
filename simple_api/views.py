# -*- coding: utf-8 -*-
import sys
import json
import inspect
from django.http import HttpResponse
import simple_api


def test(request):
    response = simple_api.send_response(status='ok', data='It works')
    return HttpResponse(response, content_type="application/json")


def manual(request):
    text = [u'SimpleAPI manual']
    #for model in inspect.getmembers(sys.modules[simple_api.dispatcher.models[0].__name__], inspect.isclass):
    for model in simple_api.dispatcher.models:
        if hasattr(model[1], 'simple_api_id'):
            text.append(u"\n\n{} - {}:".format(model[0], model[1].description))
            model = model[1](None)
            for p in [attr for attr in dir(model) if hasattr(model.__getattribute__(attr), 'simple_api_variable')]:
                a = model.__getattribute__(p)
                line = u"\t<{}>\t{}\t\t[{}]\t(default: {})  \t- {}.".format(
                    a.data_type, p, 'optional ' if a.blank else 'mondatory', a.default, a.description
                )
                line += "\tchoices: {}".format(str(a.choices)) if hasattr(a, 'choices') and a.choices else ""
                text.append(line)
    return HttpResponse(u"\n".join(text), content_type="text/plain")


def action(request, method):
    response = simple_api.send_response(status='error', data='Unknown method %s' % method)
    for model in simple_api.dispatcher.models:
        if hasattr(model[1], 'simple_api_id'):
            if model[0].lower() == method:
                model = model[1](method)
                response = model.get_response(request)
                break
    return HttpResponse(response, content_type="application/json")


def model_action(request, model_class, method):
    response = simple_api.send_response(status='error', data='Unknown method %s' % method)
    for model in simple_api.dispatcher.models:
        if hasattr(model[1], 'simple_api_model_id'):
            if model[0].lower() == model_class:
                model = model[1](method)
                response = model.router(request)
                break
    return HttpResponse(response, content_type="application/json")