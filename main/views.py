import urllib, plistlib
from main.models import *
from django.shortcuts import render
from django import forms
from django.core.cache import cache

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
    return render(request, "index.html")

def updates(request, product_id=None, lang="English"):
    from operator import attrgetter
    conf = Configuration.objects.get(pk=1)

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

    if request.method == "POST":
        form = SettingsForm(request.POST, instance=conf)
        form.save()

    form = SettingsForm(instance=conf)
    return render(request, "settings.html", {'form': form})
