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

#UI MODULE
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, Gdk, GdkPixbuf

import os
import sys
import fcntl
import xdg.Menu

#ORIGINAL MODULE
import Config
import DesktopFile

# I18N MODULE
import gettext
gettext.install('bumblebee-ui', os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '../i18n')))

#ICON CONFIGURATION
class IconSet:
    """This small class contain the settings computed for categories"""
    def __init__(self):
        self.icon_theme= Gtk.IconTheme.get_default()
        self.icon_theme.append_search_path(Config.icon_file_directory)

    def get_uri (self, icon_name, icon_size):
        return "file://" + self.get_path(icon_name, icon_size)

    def get_pixbuf (self, icon_name, icon_size=Config.icon_size):
        try :
            return self.icon_theme.load_icon(icon_name, icon_size, 0)
        except :
            try : return GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, icon_size, icon_size)
            except : return self.icon_theme.load_icon(Config.default_icon_name, icon_size, 0)

    def get_path (self, icon_name, icon_size=Config.icon_size):
        try : return self.icon_theme.lookup_icon(icon_name, icon_size, 0).get_filename()
        except : self.get_path(Config.default_icon_name)

#TODO Factorize the init which is too long
class Applications_settings():
#TODO This initialization should be avoid or rethinked
    to_modify_file=[]
    to_configure_file={}
    to_unconfigure_file={}
    categories_iter_with_child={}
    configured_file_exist=False

    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget,args):
        if __name__=="__main__": Gtk.main_quit()
        else : self.window.destroy()

    def __init__(self):
        #FIXME Seems not to be clean or shorter enough
        self.icon_set = IconSet()

        # MAIN WINDOW
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_title(_(u"Bumblebee - Applications Settings"))
        self.window.set_border_width(0)
        self.window.set_size_request(600,500)
        # MAIN WINDOW ICON : monitor and launcher
        self.window.set_icon(self.icon_set.get_pixbuf('bumblebee', 48))

        # NOTEBOOK
        self.notebook= Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.notebook.set_border_width(10)
        self.window.add(self.notebook)

        # SELECT APPLICATION
            # LIST
        #self.app_list = Gtk.TreeStore(str,str,str,GdkPixbuf.Pixbuf,bool,bool,bool,str,bool,str,bool,str)
        self.app_list = Gtk.TreeStore(str,str,str,GdkPixbuf.Pixbuf,bool,bool,bool,bool,bool,str,bool,str)
        self.categorie_iter={}
        self.buildMenu()

            # VIEW
        self.select_app_view = Gtk.TreeView(self.app_list)
        self.treeselection = self.select_app_view.get_selection()
        self.treeselection.set_mode(Gtk.SelectionMode.NONE)
        self.select_app_view.set_rules_hint(True)
        self.select_app_view.show()
        self.build_select_view()

            # EXPAND CATEGORIES WITH CHILD
        try :
            for categorie in self.categories_iter_with_child:
                categorie_iter,count= self.categories_iter_with_child[categorie]
                self.select_app_view.expand_to_path(self.app_list.get_path(categorie_iter))
        except : self.select_app_view.expand_all()

            # PAGE
        self.select_page = self.build_notebook_page(
            tab_title = _(u"Select applications"),
            instruction_text = _(u"Choose the application you want to configure to use with the discrete graphic card."),
            view = self.select_app_view ,
            button_list = [self.action_button(stock=Gtk.STOCK_APPLY, action=self.apply_app_set)] )
            #TODO Create an apply now button which relaunch unity with unity --replace or use dynamic desktop configuration (See Ubuntu desktop specification)

        # CONFIGURE APPLICATION
            # LIST
        self.configured_apps = self.app_list.filter_new(root=None)
        self.configured_apps.set_visible_column(5)

            # VIEW
        self.config_app_view = Gtk.TreeView(self.configured_apps)
        self.config_app_view.set_rules_hint(True)
        self.build_config_view()
        self.config_app_view.show()

            # PAGE
        self.configure_page = self.build_notebook_page(
            tab_title=_(u"Configure applications"),
            instruction_text=_(u"Choose the configuration for each application. Depending on mode the discrete card will be launched: always (Performance), only when plugged (Power Save) or with launcher shortcuts (Option)") ,
            view=self.config_app_view )

#FIXME : Set the focus on configure page doesn't work
        if self.configured_file_exist==True: self.notebook.set_current_page(1)
        else: self.select_app_view.expand_all()

        #SHOW ALL
        self.window.show_all()

    def build_notebook_page(self , tab_title, instruction_text , view , button_list=[]):
        # SCROLL FRAME
        scrolled_window=Gtk.ScrolledWindow()
        scrolled_window.add(view)
        # ACTION AREA
        hbox=Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_layout(Gtk.ButtonBoxStyle.START)
        hbox.set_spacing(10)
        # SPECIFIC BUTTON
        for button in button_list : hbox.add(button)
        # COMMON BUTTON
        help_button=self.action_button(stock=Gtk.STOCK_HELP, action=self.displayHelp, args=instruction_text)
        close_button=self.action_button(stock=Gtk.STOCK_CLOSE, action=self.destroy)
        for button in [help_button,close_button]:
            hbox.add(button)
            hbox.set_child_secondary(button, True)
        # CONTAINER
        vbox= Gtk.VBox(homogeneous=False)
        vbox.pack_start(scrolled_window, True, True, 10)
        vbox.pack_end(hbox, False, False, 10)
        box=Gtk.HBox(homogeneous=True)
        box.pack_start(vbox, True, True, 10)
        # NOTEBOOK PAGE
        notebook_label= Gtk.Label(tab_title)
        return self.notebook.append_page(box, notebook_label)

    def displayHelp(self,widget,args):
        dialog = Gtk.MessageDialog(self.window,
                                    Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                    Gtk.MessageType.QUESTION,
                                    Gtk.ButtonsType.CLOSE)
        dialog.set_properties(text=_("Bumblebee - Help"), secondary_text=args)
        dialog.run()
        dialog.destroy()

    def action_button(self, action, args=None, label=None, stock=None):
        button= Gtk.Button(label,stock)
        button.connect("clicked",action, args)
        return button

    def buildMenu(self, menu=xdg.Menu.parse(Config.menu_file_path), category=None):
        """Function to build the store with this columns  \
        *Application Name or Categorie Name, *File Name, *Application Categorie, \
        *Application Icon Path, Is Not Category, Configured, (Selected by default), \
        Mode,  32bits, Compression, Background display, Background color \
        for categories : Categorie Name, None, None, Icon Path, False , Has child configured, False, None, \
        """
        for entry in menu.getEntries():
            if isinstance(entry, xdg.Menu.Menu):
                if category == None :
                    main_category = entry.getName()
                    cat_info= [main_category, None, None, self.icon_set.get_pixbuf(entry.getIcon())] + 3*[False] + 3*[None]
                    iter=self.app_list.append(None, cat_info + [False, Config.to_configure_color])
                    self.categorie_iter.update({main_category:iter})
                    self.buildMenu(entry, main_category)
                else :
                    self.buildMenu(entry, category)

            elif isinstance(entry, xdg.Menu.MenuEntry):
                app_info = DesktopFile.GetDesktop(entry, category).getInfo()
                app_info[3]=self.icon_set.get_pixbuf(app_info[3])

                if app_info[2] :
                    parent_iter=self.categorie_iter.get(app_info[2])
                else :
                    parent_iter=None

                if app_info[5] == True:
                    self.configured_file_exist=True
                    print ['if: '] + app_info + [True, Config.configured_color]
                    self.app_list.append(parent_iter, app_info + [True, Config.configured_color])
                    if app_info[2] :
                        self.add_child_for_categorie(app_info[2])
                        self.app_list[parent_iter][5]=True #Used to only show the categories with configured child
                else :
                    print ['else: '] + app_info + [False, Config.to_configure_color]
                    self.app_list.append(parent_iter, app_info + [False, Config.to_configure_color])

    def build_select_view(self):
        # APPLICATION OR CATEGORIE NAME COLUMN
        self.column = Gtk.TreeViewColumn(_(u'Applications'))

        # SELECT CHECKBOX
        rendererToggle = Gtk.CellRendererToggle()
        self.column.pack_start(rendererToggle, True)
        self.column.add_attribute(rendererToggle, 'active', 6)
        self.column.add_attribute(rendererToggle, 'visible', 4)
        rendererToggle.set_property('activatable', True)
        rendererToggle.connect('toggled', self.on_select_app)

        # APPLICATION ICON
        rendererIcon=Gtk.CellRendererPixbuf()
        self.column.pack_start(rendererIcon, True)
        self.column.add_attribute(rendererIcon, 'pixbuf', 3)

        # APPLICATION NAME
        rendererText=Gtk.CellRendererText()
        self.column.pack_start(rendererText, True)
        self.column.add_attribute(rendererText, 'text', 0)

        # BACKGROUND COLOR SET
        for renderer in [rendererToggle, rendererIcon, rendererText]:
            self.column.add_attribute(renderer, "cell-background-set", 10)
            self.column.add_attribute(renderer, "cell-background", 11)
        #self.column.set_min_width(300) : cause problem with the pack start
#FIXME : the style must be refined in order to have a better display for the user : size if the icon, name of the application and categorie display
#FIXME : there must be a better way also to change the row color depending on state (this color can be changed by a color id that can be used to know the state of the application ??? in order to have a smoother treestore
        self.column.set_max_width(350)

        #FILE NAME COLUMN
        self.select_app_view.append_column(self.column)
        rendererText2=Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn(_(u'File Name'),rendererText2, text=1)
        column1.add_attribute(rendererText2, "cell-background-set",10)
        column1.add_attribute(rendererText2, "cell-background",11)
        self.select_app_view.append_column(column1)
        self.select_app_view.set_level_indentation(10)

    def on_select_app(self, cell, row):
#TODO : Find a better way to manage row color change
        self.app_list[row][6] = not self.app_list[row][6]
        Configured, Selected= self.app_list[row][5], self.app_list[row][6]
        if Configured==True and Selected==False : #The app will be Unconfigured
            self.app_list[row][10],self.app_list[row][11]=True,Config.to_unconfigure_color
            self.to_unconfigure_file.update({self.app_list[row][1]:self.app_list.get_iter(row)})
        elif Configured==True and Selected==True : #The configured app is reselected: Nothing to apply
            self.app_list[row][10],self.app_list[row][11]=True,Config.configured_color
            del self.to_unconfigure_file[self.app_list[row][1]]
        elif Configured==False and Selected==True : #The app will be Configured
            self.app_list[row][10],self.app_list[row][11]=True,Config.to_configure_color
            self.to_configure_file.update({self.app_list[row][1]:self.app_list.get_iter(row)})
        elif Configured==False and Selected==False : #The app is not configured and unselected: Nothing to apply
            self.app_list[row][10]=False
            del self.to_configure_file[self.app_list[row][1]]

    def build_config_view(self):
        """Function to create a setting list for applications configured for Bumblebee"""
        # APPLICATION NAME COLUMNS
        self.column=Gtk.TreeViewColumn(_(u'Applications'))

        rendererIcon=Gtk.CellRendererPixbuf()
        self.column.pack_start(rendererIcon, False)
        self.column.add_attribute(rendererIcon, 'pixbuf', 3)
        rendererText=Gtk.CellRendererText()
        self.column.pack_start(rendererText, False)
        self.column.add_attribute(rendererText, 'text', 0)

        self.config_app_view.append_column(self.column)

        # MODE, DRIVER AND COMPRESSION COLUMN
        self.build_combo_column(_(u"Mode"), 7, Config.mode_keys.values())

        self.build_config_column (_(u"32bits Driver"), 8)

        self.build_combo_column(_(u"Compression"), 9, ["default"] + Config.compression_list)

        self.config_app_view.set_level_indentation(20)
        self.config_app_view.expand_all()
        self.config_app_view.set_show_expanders(False)

    def build_combo_column(self, column_name, column_id, value_list):
        """Function to build the columns with selection from a list"""
        # COMBOBOX CELL
        combo_list = Gtk.ListStore(str)
        for value in value_list: combo_list.append([value])
        rendererCombo = Gtk.CellRendererCombo()
        rendererCombo.set_properties(model=combo_list, editable=True)
        rendererCombo.set_property("has-entry", False)
        rendererCombo.set_property("text-column", 0)
        rendererCombo.connect("edited", self.on_combo_edit, column_id)
        # COMBOBOX COLUMN
        column = Gtk.TreeViewColumn(column_name)
        column.pack_start(rendererCombo, False)
        column.add_attribute(rendererCombo, "text", column_id)
        column.add_attribute(rendererCombo, "visible", 4)
        self.config_app_view.append_column(column)

    def on_combo_edit(self, cell , path , new_text, column_id):
        filter_iter = self.configured_apps.get_iter(path)
        iter = self.configured_apps.convert_iter_to_child_iter(filter_iter)
        self.app_list[iter][column_id] = new_text
        DesktopFile.SetDesktop(self.app_list[iter][1]).setOptirun(self.app_list[iter][7],self.app_list[iter][8],self.app_list[iter][9])
        #DesktopFile(self.app_list[iter][1]).set_exec_config(self.app_list[iter][7],self.app_list[iter][8],self.app_list[iter][9])

    def build_config_column(self, column_name, column_id):
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.set_property('activatable', True)
        rendererToggle.connect('toggled', self.on_config_check ,(self.configured_apps, column_id))

        column = Gtk.TreeViewColumn(column_name, rendererToggle, active=column_id, visible=4)
        self.config_app_view.append_column(column)

    def on_config_check(self, cell, row, user_data):
        model, column = user_data
        iter = model.convert_iter_to_child_iter(model.get_iter(row))
        self.app_list[iter][column] = not self.app_list[iter][column]
        DesktopFile.SetDesktop(self.app_list[iter][1]).setOptirun(self.app_list[iter][7],self.app_list[iter][8],self.app_list[iter][9])
        #DesktopFile(self.app_list[iter][1]).set_exec_config(self.app_list[iter][7],self.app_list[iter][8],self.app_list[iter][9])

    def apply_app_set (self,widget,data=None):
        for file_name, iter in self.to_configure_file.iteritems(): #The app is to configure
            self.apply_app_change ( iter, [DesktopFile.SetDesktop(file_name).setEntry, self.add_child_for_categorie],
                                    True, Config.mode_keys['option'], True, Config.configured_color)
        self.to_configure_file.clear()
        for file_name, iter in self.to_unconfigure_file.iteritems(): #The app is to unconfigure
            self.apply_app_change ( iter, [DesktopFile.SetDesktop(file_name).unsetEntry, self.remove_child_for_categorie],
                                    False, False, False, Config.to_configure_color)
        self.to_unconfigure_file.clear()
        self.config_app_view.expand_all()

    def apply_app_change (self, iter, actions, configured, mode, display_bg, bg_color):
        actions[0]()
        self.app_list.set(iter, 5, configured, 7, mode, 10, display_bg, 11, bg_color)
        actions[1](self.app_list.get_value(iter,2))

#TODO There must be thing done to deal with categories having configured child : simplify this function
    def add_child_for_categorie(self,categorie_name):
        if self.categories_iter_with_child.has_key(categorie_name):
            parent_iter, count=self.categories_iter_with_child[categorie_name]
            child_count= count+1
        else: child_count=1
        self.categories_iter_with_child.update({categorie_name:[self.categorie_iter[categorie_name], child_count]})
        self.app_list.set(self.categorie_iter[categorie_name], 5, True)

    def remove_child_for_categorie(self,categorie_name):
        if self.categories_iter_with_child.has_key(categorie_name):
            parent_iter, count=self.categories_iter_with_child[categorie_name]
            child_count= count-1
            self.categories_iter_with_child.update({categorie_name:[parent_iter, child_count]})
            if child_count==0 :
                del self.categories_iter_with_child[categorie_name]
                self.app_list.set(self.categorie_iter[categorie_name], 5, False)

    def main(self):
        Gtk.main()
        return 0

if __name__ == "__main__":
    pid_file = 'bumblebee-app-settings.pid'
    fp = open(pid_file, 'w')
    app_settings = Applications_settings()
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        app_settings.main()
    except IOError:
        print "Another instance of bumblebee-app-settings is running : Quit"
        quit()

