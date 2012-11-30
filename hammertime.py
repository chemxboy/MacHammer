#!/usr/bin/env python
"""
The MacHammer Runtime
"""
import re
import plistlib
import os, os.path
import json, urllib2, sys, subprocess

def upload(path, url):
    path = 'file=@%s' % path
    subprocess.call(['/usr/bin/curl', '-F', path, url])

def sysctl(param):
    # Returns a value of sysctl variable
    return subprocess.check_output(['/usr/sbin/sysctl', '-b', param])

class Repo(object):
    def __init__(self, url, mount_point='/tmp/mh_repo'):
        self.url = url
        self.mount_point = mount_point

        self.scripts = os.path.join(self.mount_point, "Scripts")
        self.masters = os.path.join(self.mount_point, "Masters")
        self.recovery = os.path.join(self.mount_point, "Recovery")

    def mount(self):
        if not os.path.exists(self.mount_point):
            os.mkdir(self.mount_point)
        
        subprocess.call(['/sbin/mount_afp', '-o', 'nobrowse', self.url, 
            self.mount_point])
    
    def umount(self):
        subprocess.call(['/sbin/umount', self.mount_point])
        if os.path.exists(self.mount_point):
            os.rmdir(self.mount_point)

    def script(self, name, *args):
        path = os.path.join(self.scripts, name)
        destination = os.path.join(self.recovery, 'disk1.img')
        subprocess.call([path, '/dev/disk1', destination])

class Request(object):
    def __init__(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'HammerTime/0.1')
        self.r = urllib2.urlopen(req)
        self.data = json.loads(self.r.read())

class Storage(object):
    def __init__(self):
        proc = subprocess.Popen(['/usr/sbin/diskutil', 'list', '-plist'], 
            stdout=subprocess.PIPE)
        plist = plistlib.readPlist(proc.stdout)
        print plist

class SystemProfile(object):
    def __init__(self):
        proc = subprocess.Popen(['system_profiler', 'SPHardwareDataType', '-xml'], 
            stdout=subprocess.PIPE)
        self.plist = plistlib.readPlist(proc.stdout)

        for l in self.plist:
            if l['_dataType'] == 'SPHardwareDataType':
                for i in l['_items']:
                    for k, v in i.items():
                        setattr(self, k, v)

    def save(self, path):
        fh = open(path, "w")
        plistlib.writePlist(self.plist, fh)
        return fh

if __name__ == "__main__":
    url = sys.argv[1].rstrip("/")
    Request(url)

    # get config
    r = Request("%s/settings/" % url)
    repo = Repo(r.data['repo_url'])
    repo.mount()
    
    while True:
        line = raw_input('mh > ')
        
        if line == '.quit':
            repo.umount()
            print "Bye!"
            break
        
        if line == 'recover':
            repo.script('ddrescue')

        if line == 'scripts':
            r = Request("%s/scripts/" % url)
            for s in r.data:
                print "%s\t%s" % (s['id'], s['title'])

        if re.match(r'^scripts (\d)$', line):
            print "Run script!"

        if line == 'specs':
            model = sysctl("hw.model")
            print model
            # /specs/MacBookPro3,1

        if line == 'profile':
             """Collect system profile and upload to MH server"""
             p = SystemProfile()
             path = "/tmp/%s.spx" % p.serial_number
             spx = p.save(path)
             upload(path, "%s/macs/new/" % url)

        if line == 'storage':
            Storage()
