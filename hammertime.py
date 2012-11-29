#!/usr/bin/env python
"""
The MacHammer Runtime
"""
import re
import plistlib
import json, urllib2, sys, subprocess

def upload(path, url):
    path = 'file=@%s' % path
    subprocess.call(['/usr/bin/curl', '-F', path, url])

def sysctl(param):
    # Returns a value of sysctl variable
    return subprocess.check_output(['/usr/sbin/sysctl', '-b', param])

class Request(object):
    def __init__(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'HammerTime/0.1')
        self.r = urllib2.urlopen(req)
        self.data = json.loads(self.r.read())
        return

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

    print "Connected to %s" % url
    
    while True:
        line = raw_input('mh > ')
        
        if line == '.quit':
            print "Bye!"
            break
        
        if line == 'scripts':
            r = Request("%s/scripts/" % url)
            for s in r.data:
                print "%s\t%s" % (s['id'], s['title'])

        if re.match(r'^scripts \d$', line):
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
