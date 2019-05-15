"""
    WpSyncZip: a tool to easy maintain js_composer and revslider modules around shared hosting.
    Copyright (C) <2017>  <Michal (makyox dot aubert at gmail do com)>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    @todo: selecting wordpress from checkbox list
    
"""

import sys
sys.path.insert(0, 'libs')
import optparse
import os
import datetime
import shutil
import zipfile
import inquirer
import re
import argparse
from subprocess import Popen, PIPE
from pprint import pprint

date = datetime.datetime.now().strftime('%Y%m%d-%s')
f_date = datetime.datetime.now().strftime('%Y%m%d')
parser = argparse.ArgumentParser(description='Wordpress module updater')
parser.add_argument("t", help="Target directory", type=str)
args2 = vars(parser.parse_args())
args3 = parser.parse_args()
target = args3.t
plugins_dir = 'plugins'
base_dir = target
target_dir = target+'wp-content/plugins'


versions = {'js_composer':5,'revslider':6}
php_vars = {}

W  = '\033[0m' 
R  = '\033[31m'
G  = '\033[32m'


def list_modules(path):
    modules = os.listdir(path)
    return modules

def list_modules_full(path):
    modules = os.listdir(path)
    base_versions = []
    for item in modules:
        item2 = item.split('.')
        try:
            archive = zipfile.ZipFile('plugins/'+item, 'r')
            file = archive.open(item2[0]+'/'+item2[0]+'.php')
            try:
                lines=file.readlines()
                nl = lines[versions[item2[0]]].split(':')
                row = {item2[0]:nl[1][1:].rstrip()}
                base_versions.append(row)
            finally:
                file.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
    return base_versions


def check_source():
    print (G+'SOURCE CHECK'+W)
    for item in modules:
        item2 = item.split('.')
        print item
        try:
            archive = zipfile.ZipFile('plugins/'+item, 'r')
            file = archive.open(item2[0]+'/'+item2[0]+'.php')
            try:
                lines=file.readlines()
                nl = lines[versions[item2[0]]].split(':')
                print nl[1][1:]  
            finally:
                file.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

def check_versions():
    for item in modules:
        print ''
        print item
        if item in versions:
            f=open(target_dir+'/'+item+'/'+item+'.php')
            lines=f.readlines()
            nl = lines[versions[item]].split(':')
            print nl[1][1:]

def main(target): 
    if(os.path.isdir(target) == True):
        print ''
        target_dir = target+'wp-content/plugins'
        print (W+'Lets start!'+W)
        for item in modules:
            itemn = item[:-4]

            target_module = target_dir+'/'+itemn
            if(os.path.exists(target_module) == True):
                print(G+'removing old version of '+item+W)
                shutil.rmtree(target_module)
                print(G+'extracting '+item+W)
                with zipfile.ZipFile(plugins_dir+'/'+item,"r") as zip_ref:
                    zip_ref.extractall(target_dir)
            else:
                print(R+'target '+item+' dir not found, nothin to do here'+W)
        print(G+'DONE/DONE'+W)
        list_dirs()
    elif(target == "exit"):
        quit()
    else:
        print(R+'target dir not found :/'+W)

def update_it(stage2):
    if 'stage2' in locals():
        main(target=stage2['action'])

def list_dirs():
    base_versions = list_modules_full(plugins_dir)
    pprint(base_versions)
    print('')
    ndirs = []
    dirs = os.listdir(base_dir)
    for d in dirs:

        if(os.path.isdir(base_dir+d+'/') == True):
            if(os.path.isdir(base_dir+d+'/public_html')):
                d = d+'/public_html/'
            else:
                d = d
            d2 = os.listdir(base_dir+d+'/')
            for d3 in d2:
                if((d3.find("wordpress") != -1 or d3.find("wupe") != -1 or d3.find("beta") != -1) and os.path.isdir(base_dir+d+'/'+d3) == True):
                    print("")
                    print(d)
                    if os.path.isfile(base_dir+d+'/'+d3+'/wp-includes/version.php'):
                        f=open(base_dir+d+'/'+d3+'/wp-includes/version.php')
                        lines=f.readlines()
                        nl = lines[15].split('=')
                        print (G+"core: "+nl[1][2:-3]+W)
                        if os.path.isdir(base_dir+d+'/'+d3+'/wp-content/plugins/revslider') == True:
                            lines=open(base_dir+d+'/'+d3+'/wp-content/plugins/revslider/revslider.php').readlines()
                            nl = lines[6].split(':')
                            if(nl[1][1:-2] == base_versions[0]['revslider']):
                               print(G+"revslider: "+nl[1][1:-1]+''+W)
                            else:
                               print(R+"revslider: "+nl[1][1:-1]+''+W)
                               ndirs.append(base_dir+d+'/'+d3+'/')

                        if os.path.isdir(base_dir+d+'/'+d3+'/wp-content/plugins/js_composer') == True:
                            lines=open(base_dir+d+'/'+d3+'/wp-content/plugins/js_composer/js_composer.php').readlines()
                            nl = lines[5].split(':')
                            if(nl[1][1:-1] == base_versions[1]['js_composer']):
                               print(G+"js_composer: "+nl[1][1:-1]+''+W)
                            else:
                               print(R+"js_composer: "+nl[1][1:-1]+''+W)
                               if base_dir+d+'/'+d3+'/' not in ndirs:
                                  ndirs.append(base_dir+d+'/'+d3+'/')
                  
    ndirs.append("")                           
    ndirs.append(('Do nothing and exit!', 'exit'))                           
    questions = [
    inquirer.List('action',
        message="Select directory",
        choices=ndirs),
    ]
    if len(ndirs):
        stage2 = inquirer.prompt(questions)
        main(target=stage2['action'])

class wpsync:
    variable = "stable"
    def function(self):
            print('ok')


questions = [
    inquirer.List('action',
        message="Select operation?",
        choices=[
          ('List dirs', 'dirs'),
          ('Source plugins check', 'source'),
          ('Destination versions', 'versions'),
          ('Just sync it!', 'sync')
        ],
        default=['source']),
]

stage1 = inquirer.prompt(questions)
modules = list_modules(plugins_dir)

if(stage1['action'] == 'dirs'):
    list_dirs()
    quit()

if(stage1['action'] == 'versions'):
    check_versions()
    quit()

if(stage1['action'] == 'source'):
    check_source()
    quit()

if(stage1['action'] == 'sync'): 
    main(target=args3.t)
