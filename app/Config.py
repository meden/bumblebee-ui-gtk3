#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
#
# This file is part of bumblebee-ui.
#
# bumblebee-ui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bumblebee-ui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bumblebee-ui. If not, see <http://www.gnu.org/licenses/>.
#
### END LICENSE

import os
from gi.repository import Gtk
import sys
import gettext

### APPLICATIONS MENU CONFIG ###

#BUMBLEBEE DEFAULT CONFIGURATION
config_file_path='/etc/bumblebee/bumblebee.conf'
optirun_installation_path='/usr/bin/optirun'
#With KDE, you might need to change this value to the menu file you need
menu_file_path=None
#ICONS FILE PATH
#icon_file_directory = '/usr/share/bumblebee-ui/icons/'
icon_file_directory = './icons/'
active_icon = 'bumblebee-indicator-active.svg'
unactive_icon = 'bumblebee-indicator.svg'

#TEST IF OPTIRUN IS INSTALLED
def check_install(name, path):
    try :
        os.path.exists(path)
        os.access(path, os.X_OK)
    except :
        print "Install check : {0} is lacking or don't have the good right at this adress {1}".format(name, path)
        quit()

check_install('Bumblebee configuration file', config_file_path)
check_install('Optirun',optirun_installation_path)

#ICONS FILE PATH
#icon_file_directory = '/usr/share/bumblebee-ui/icons/'
icon_file_directory = os.path.abspath(os.path.dirname(sys.argv[0])) + '/icons/'

#LOCALISATION FILE PATH
#FIXME: the argv[0] thing has to be temporary (as ANY plumbed path)
gettext.install('bumblebee-ui', os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'i18n')))

#ACCEPTED COMPRESSION
compression_list=['jpeg','proxy','rgb','yuv','xv']

#MODE LIST
mode_keys={'perf':"Performance",
    'eco':"Power Save",
    'option':"Optional"}

#ICON FILES THEME
icon_size=24
default_icon_name='application-x-executable'

#APP SETTINGS COLOR THEME
configured_color='#00FF33'
to_configure_color='#FFFF33'
to_unconfigure_color='#FF0033'

#GET BUMBLEBEE CONFIGURATION VALUE
def get_config_value(variable_name):
    """Function to get configuration value inside a shell script"""
    for line in open(config_file_path):
        if variable_name + '=' in line:
            return line.split('=',1)[1].replace("\n","")

default_compression= get_config_value('VGL_COMPRESS')
vgl_display= get_config_value('VirtualDisplay').replace(":","")

### INDICATOR SETTINGS ###
#DEFAULT APPLICATIONS IN THE PREFERRED APP MENU :
applications_setting_path='app/AppSettings.py'
if applications_setting_path :
     check_install('Bumblebee - Applications Settings', applications_setting_path)
default_preferred_apps =[ ['Glxgears', ['glxgears']] ,
                        ['Glxspheres', ['glxspheres']] ]

#NOTIFICATION MESSAGES :
#TODO Revert when the possibility to turn off the card is back
active_label=_(u"Bumblebee : ON")
active_comment=_(u"Bumblebee is in use")
unactive_label=_(u"Bumblebee : OFF")
unactive_comment=_(u"Bumblebee is not used anymore")

#FIXME There must be a better way to store config using MODEL desktop file

if __name__=="__main__" :
    print "Config.py can't run as a standalone application"
    quit()

