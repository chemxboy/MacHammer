import json
import urllib, plistlib
from main.models import *
from django import forms
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

class ScriptForm(forms.ModelForm):
    class Meta:
        model = Task

class SpecForm(forms.ModelForm):
    class Meta:
        model = Spec

    tabs = {'General': ['title', 'model_id', 'introduced', 'discontinued', 'model_number', 'order_number', 'photo'],
    'Processor': ['cpu', 'cpu_speed', 'cpu_arch', 'cpu_cores', 'cpu_cache', 'cpu_bus']}

class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Configuration

class Update(object):
    def __init__(self, smd_url, lang="English", product_id=None):
        self.packages = list()
        fh = urllib.urlopen(smd_url)
        p = plistlib.readPlist(fh)
        loc = p['localization'][lang]

        self.title = loc['title']
        self.description = loc['description']
        self.version = p['CFBundleShortVersionString']
        self.product_id = product_id

    def get_absolute_url(self):
        return "/updates/%s/" % self.product_id

class Package(object):
    def __init__(self, pkg):
        self.size = pkg['Size']
        self.url = pkg['URL']

    def filename(self):
        import os.path
        from urlparse import urlparse
        o = urlparse(self.url)
        return os.path.basename(o.path)

def index(request):
    if request.META['HTTP_USER_AGENT'] == 'HammerTime/0.1':
        return HttpResponse(json.dumps("OK"))

    return render(request, "index.html")

def updates(request, product_id=None, lang="English"):
    from operator import attrgetter
    conf = Configuration.objects.get(pk=1)
    updates = []

    if request.GET.get("lang"):
        lang = request.GET['lang']

    langs = ['Dutch', 'English', 'French', 'German', 'Italian', 'Japanese', 'Spanish']

    fh = urllib.urlopen(conf.sus_url)
    p = plistlib.readPlist(fh)

    if product_id:
        prod = p['Products'][product_id]
        update = Update(prod['ServerMetadataURL'], lang, product_id)

        for p in prod['Packages']:
            update.packages.append(Package(p))

        return render(request, "updates_detail.html", {'update': update})

    if not request.GET.get('resync'):
        updates = cache.get("updates-%s" % lang)
    
    if not updates:
        updates = []

        for k, v in p['Products'].items():
            try:
                update = Update(v['ServerMetadataURL'], lang, k)
                update.date = v['PostDate']
                for p in v['Packages']:
                    update.packages.append(Package(p))

                updates.append(update)
            except KeyError:
                continue

    updates = sorted(updates, key=attrgetter('date'), reverse=True)
    cache.set("updates-%s" % lang, updates, 60*60*24)

    return render(request, "updates_list.html", {
        'updates': updates,
        'lang': lang,
        'langs': langs
        })

def settings(request):
    conf = Configuration.objects.get_or_create(pk=1)[0]

    if request.META['HTTP_USER_AGENT'] == 'HammerTime/0.1':
        data = dict(repo_url=conf.repo_url)
        return HttpResponse(json.dumps(data), content_type='application/json') 
        
    if request.method == "POST":
        form = SettingsForm(request.POST, instance=conf)
        form.save()

    form = SettingsForm(instance=conf)
    return render(request, "settings.html", {'form': form})

def specs(request, spec_id=None):
    specs = Spec.objects.all()

    if spec_id:
        spec = Spec.objects.get(pk=spec_id)
        return render(request, "specs_detail.html", {
            'spec': spec,
            'specs': specs,
            'categories': Spec.CATEGORIES
        })

    if request.GET.get("c"):
        specs = specs.filter(category=request.GET['c'])

    return render(request, "specs_list.html", {'specs': specs, 
        'categories': Spec.CATEGORIES})

def edit_spec(request, spec_id):
    form = SpecForm()
    spec = Spec()
    
    if spec_id != "new":
        spec = Spec.objects.get(pk=spec_id)
        form = SpecForm(instance=spec)

    if request.method == "POST":
        form = SpecForm(request.POST, request.FILES, instance=spec)
        if form.is_valid():
            spec = form.save()
            return redirect(spec)

    return render(request, "specs_edit.html", {'form': form})

def workflows(request, wf_id=None):
    return render(request, "workflows_list.html")

def edit_workflow(request, wf_id):
    form = WorkflowForm()
    return render(request, "workflows_edit.html", {'form': form})

@csrf_exempt
def edit_mac(request, sn=None):
    plist = plistlib.readPlist(request.FILES['file'])
    m = Mac()
    print plist

def scripts(request, script_id=None):
    scripts = Task.objects.all()

    if script_id:
        scripts = scripts.filter(pk=script_id)

    if request.META['HTTP_USER_AGENT'] == 'HammerTime/0.1':
        out = list()
        for t in scripts:
            out.append(dict(id=t.pk, title=t.title))

        return HttpResponse(json.dumps(out), content_type='application/json')

    if script_id:
        form = ScriptForm(instance=scripts[0])
        return render(request, "scripts_edit.html", {'form': form})

    return render(request, "scripts_list.html", {'scripts': scripts})

def edit_script(request):
    form = ScriptForm()

    if request.method == "POST":
        form = ScriptForm(request.POST)
        form.save()

    return render(request, "scripts_edit.html", {'form': form})

def get_hammered(request):
    fh = open("hammertime.py", "r")
    return HttpResponse(fh.read())
