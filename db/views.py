# Create your views here.
from models import DB, DBEntry
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from jsonrpc import jsonrpc_method

@jsonrpc_method('db.update')
def update(request, db_name, dct, entry_id = None, design_mode = False):
    out = {}
    db = DB.objects.get(name = db_name)
    data = {}

    for item in dct:
        data[item['name']] = item['value']

    if design_mode:
        db.design_mode()

    form = db.as_form(data)
    if form.is_valid():
        entry = db.update_entry(form.cleaned_data, request.session['signature'], entry_id = entry_id)
        out['ok'] = 1
        out['id'] = str(entry.id)
        out['data'] = entry.data
        out['signature'] = entry.signature
    else:
        out['ok'] = 0
        out['form'] = form.as_ul()

    return out

@jsonrpc_method('db.insert_field')
def insert_field(request, db_name, dct):
    return insert(request, db_name, dct, design_mode = True)

@jsonrpc_method('db.remove')
def remove(request, db_name, entry_id, design_mode = False):
    db = DB.objects.get(name = db_name)
    if design_mode:
        db.design_mode()

    db.remove_entry(entry_id)
    return {'ok': 1}

@jsonrpc_method('db.remove_field')
def remove_field(*a, **kw):
    kw.update({'design_mode': True})
    return remove(*a, **kw)

@jsonrpc_method('form.update')
def update_form(request, db_name, entry_id, design_mode = False):
    db = DB.objects.get(name = db_name)
    if design_mode:
        db.design_mode()
    return db.form_for_entry(entry_id).as_ul()


def provide_signature(request):
    if request.method == 'GET':
        return render_to_response('signature.html', context_instance = RequestContext(request))
    if request.method == 'POST':
        request.session['signature'] = request.POST['signature']
        return HttpResponseRedirect(request.path)

def signature_first(func):
    def _func(request, *a, **kw):
        if not request.session.has_key('signature'):
            return provide_signature(request)
        return func(request, *a, **kw)
    return _func

@signature_first
def index(request):
    dbs = DB.objects()
    return render_to_response('index.html', {'dbs': dbs})

@signature_first
def db_view(request, db_name):
    db = DB.objects.get(name = db_name)
    entries = DBEntry.objects(db=db)
    return render_to_response('db_view.html', {'db': db, 'entries': entries})

@signature_first
def db_design(request, db_name):
    db = DB.objects.get_or_create(name = '%s' % db_name)[0]
    db.design_mode()
    entries = db.design_entries()
    return render_to_response('db_view.html', {'db': db, 'entries': entries, 'design_mode': True})

@signature_first
def db_create(request):
    pass
