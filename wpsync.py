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
    else:
        print(R+'target dir not found :/'+W)

class wpsync:
    variable = "stable"
    def function(self):
            print('ok')


questions = [
    inquirer.List('action',
        message="Select operation?",
        choices=[
          ('List dirs', 'dirs'),
          ('List dirs + select', 'dirs2'),
          ('Source plugins check', 'source'),
          ('Destination versions', 'versions'),
          ('Just sync it!', 'sync')
        ],
        default=['source']),
]

stage1 = inquirer.prompt(questions)

# myar = ('test','test')+('test2','test2'),+('test3')

# hosts = [
#     inquirer.List('action2',
#         message="Select operation?",
#         choices=[myar],
#         default=['source']),
# ]

# stage2 = inquirer.prompt(hosts)

modules = list_modules(plugins_dir)

if(stage1['action'] == 'dirs2'):
    
    ndirs = []
    dirs = os.listdir('../')
    for d in dirs:
        if(os.path.isdir('../'+d+'/public_html/') == True):
            d2 = os.listdir('../'+d+'/public_html/')
            for d3 in d2:
                if(d3.find("wordpress") != -1 and os.path.isdir('../'+d+'/public_html/'+d3) == True): 
                    if os.path.isfile('../'+d+'/public_html/'+d3+'/wp-includes/version.php'):
                        f=open('../'+d+'/public_html/'+d3+'/wp-includes/version.php')
                        lines=f.readlines()
                        nl = lines[6].split('=')
                        # ndirs.append(tuple({d+' ('+nl[1][2:-3]+')','../'+d+'/public_html/'+d3}))
                        ndirs.append('../'+d+'/public_html/'+d3)
    questions = [
    inquirer.List('action2',
        message="Select directory",
        choices=ndirs),
    ]
    stage1 = inquirer.prompt(questions)
    pprint(stage1)


if(stage1['action'] == 'dirs'):
    base_versions = list_modules_full(plugins_dir)
    pprint(base_versions)
    print('')
    ndirs = []
    dirs = os.listdir('../')
    for d in dirs:
        if(os.path.isdir('../'+d+'/public_html/') == True):
            d2 = os.listdir('../'+d+'/public_html/')
          
            for d3 in d2:
                if(d3.find("wordpress") != -1 and os.path.isdir('../'+d+'/public_html/'+d3) == True):
                    print("")
                    print(d)
                    if os.path.isfile('../'+d+'/public_html/'+d3+'/wp-includes/version.php'):
                        f=open('../'+d+'/public_html/'+d3+'/wp-includes/version.php')
                        lines=f.readlines()
                        nl = lines[6].split('=')
                        print (G+"core: "+nl[1][2:-3]+W)
                        if os.path.isdir('../'+d+'/public_html/'+d3+'/wp-content/plugins/revslider') == True:
                            lines=open('../'+d+'/public_html/'+d3+'/wp-content/plugins/revslider/revslider.php').readlines()
                            nl = lines[6].split(':')
                            if(nl[1][1:-2] == base_versions[0]['revslider']):
                               print(G+"revslider: "+nl[1][1:-1]+''+W)
                            else:
                               print(R+"revslider: "+nl[1][1:-1]+''+W)
                               ndirs.append('../'+d+'/public_html/'+d3+'/')

                        if os.path.isdir('../'+d+'/public_html/'+d3+'/wp-content/plugins/js_composer') == True:
                            lines=open('../'+d+'/public_html/'+d3+'/wp-content/plugins/js_composer/js_composer.php').readlines()
                            nl = lines[5].split(':')
                            if(nl[1][1:-1] == base_versions[1]['js_composer']):
                               print(G+"js_composer: "+nl[1][1:-1]+''+W)
                            else:
                               print(R+"js_composer: "+nl[1][1:-1]+''+W)
                               ndirs.append('../'+d+'/public_html/'+d3+'/')
                               
    questions = [
    inquirer.List('action',
        message="Select directory",
        choices=ndirs),
    ]
    if len(ndirs):
        stage2 = inquirer.prompt(questions)

if(stage1['action'] == 'versions'):
    check_versions()
    quit()

if(stage1['action'] == 'source'):
    check_source()
    quit()

if(stage1['action'] == 'sync'): 
    main(target=args3.t)

if 'stage2' in locals():
    main(target=stage2['action'])