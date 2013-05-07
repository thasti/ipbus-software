import os
import webbrowser

import wx

from uhal.gui.utilities.hardware_monitoring import HardwareMonitoring
from uhal.gui.guis.hardware_tree import HardwareTree
from uhal.gui.utilities.hardware import HardwareStruct
from uhal.gui.guis.refresh_buttons_panel import RefreshButtonsPanel
from uhal.gui.guis.hardware_table_panel import HardwareTablePanel
        

class DefaultGui(wx.Frame):

    def __init__(self, parent, id, title):

        wx.Frame.__init__(self, parent, id, title, size=(500, 400))       
        
        # Attributes       
        self.__hw = None
        self.__hw_mon = None
        
        # GUIs Attributes
        self.__hw_tree = None
        self.__refresh_buttons_panel = None
        self.__hw_table_panel = None

        # Layout
        self.__create_menu_bar()
        self.__do_layout()
        self.CreateStatusBar()
        
        # Event handlers 
        self.Bind(HardwareMonitoring.EVT_HWREADY, self.__on_hw_ready)
        self.Bind(wx.EVT_CLOSE, self.__on_close_window)



    def __do_layout(self):

        self.__refresh_buttons_panel = RefreshButtonsPanel(self)
        self.__hw_table_panel = HardwareTablePanel(self)
        
        border_flags = wx.ALL
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__refresh_buttons_panel, 0, border_flags, 5)
        # sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 50)
        sizer.Add(self.__hw_table_panel, 1, border_flags | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)   
        self.SetMinSize((800, 600))



    # CREATE THE MENU BAR
    def __create_menu_bar(self):

        menu_bar = wx.MenuBar()
        for each_menu_data in self.__menu_data():
            menu_label = each_menu_data[0]
            menu_items = each_menu_data[1:]
            menu_bar.Append(self.__create_menu(menu_items), menu_label)

        self.SetMenuBar(menu_bar)



    # menu bar items
    def __menu_data(self):
        
        return (("&File",
                 ("&LoadHW", "Load HW", self.__on_load_hw),
                 ("&Quit", "Quit", self.__on_close_window)
                 ),            
                ("&Help",
                 ("&Documentation", "Documentation", self.__on_click_doc),
                 ("&Support", "Support", self.__on_click_support),
                 ("&About", "About", self.__on_click_about)               
                 )
                )



    # create individual menu objects
    def __create_menu(self, items):

        menu = wx.Menu()
        for each_label, each_status, each_handler in items:
            if not each_label:
                menu.AppendSeparator()
                continue

            menu_item = menu.Append(-1, each_label, each_status)
            self.Bind(wx.EVT_MENU, each_handler, menu_item)

        return menu



  
    def __create_hardware_tree(self, hw):
        if self.__hw_is_valid():
            self.__hw_tree = HardwareTree(self, hw)
            self.__hw_tree.Show()
        else:
            print "ERROR: could not start hardware_tree -> self.__hw is not a valid object"


    
    def __on_load_hw(self, event):

        # Right now, only a connection file picker is offered.
        # Another dialog should be displayed to cope with pycohal ConnectionManager('device_id', 'uri', 'address_table')
            
        wildcard = "XML files (*.xml)|*.xml|" \
                   "All files (*.*)|*.*"

        
        file_picker = wx.FileDialog(None, style = wx.OPEN)

        file_picker.SetMessage("Choose connection file")
        file_picker.SetDirectory(os.getcwd())
        file_picker.SetWildcard(wildcard)
        file_picker.SetFilename("gui")
    

        if file_picker.ShowModal() == wx.ID_OK:            
            file_name = file_picker.GetPath()
            
            self.__hw = HardwareStruct(file_name)                    
            self.__create_hardware_tree(self.__hw) 
            self.__hw_table_panel.draw_hw_naked_tables(self.__hw)           
            
        
        file_picker.Destroy()
        
    
    
    def __on_click_doc(self, event):
        webbrowser.open("https://svnweb.cern.ch/trac/cactus")



    def __on_click_support(self, event):
        webbrowser.open("https://svnweb.cern.ch/trac/cactus")



    def __on_click_about(self, event):        

        description = """uHAL GUI is a Python based graphical user interface 
        written using the graphical library wxPython. Bla bla bla...
        """

        licence = """uHAL GUI is free software; you can redistribute 
        it and/or modify it under the terms of the GNU General Public License as 
        published by the Free Software Foundation; either version 2 of the License, 
        or (at your option) any later version.

        uHAL GUI is distributed in the hope that it will be useful, 
        but WITHOUT ANY WARRANTY; without even the implied warranty of 
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
        See the GNU General Public License for more details. You should have 
        received a copy of the GNU General Public License along with File Hunter; 
        if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
        Suite 330, Boston, MA  02111-1307  USA
        """


        info = wx.AboutDialogInfo()
        info.SetName('uHAL GUI')
        info.SetVersion('1.0.0')
        info.SetDescription(description)
        info.SetCopyright('(C) 2013 Carlos Ghabrous')
        info.SetWebSite('http://svnweb.cern.ch/trac/cactus')
        info.SetLicence(licence)
        info.AddDeveloper('Carlos Ghabrous')
        info.AddDocWriter('Carlos Ghabrous')

        wx.AboutBox(info)



    def __on_close_window(self, event):

        msg = "Do you really want to close this GUI?"
        
        dialog = wx.MessageDialog(self, msg, "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        dialog.Destroy()

        if result == wx.ID_OK:
            self.Destroy()
          
          
          
    def __on_hw_ready(self, event):
            
        print "DEBUG: HW READY in default GUI"
        self.__hw = event.get_event_info()               
        self.__hw_table_panel.on_hw_ready(self.__hw)
        self.__hw_tree.redraw(self.__hw)
        
        
        
    def __hw_is_valid(self):
        return self.__hw is not None
    
          
    
    def start_hw_thread(self):
        print "DEBUG: Received message from refresh_buttons_panel. Should start HW thread now"
        if self.__hw_is_valid():
           
            hw_worker = HardwareMonitoring(self, self.__hw)
            hw_worker.start()
        else: 
            print "ERROR: could not start HW update thread -> self.__hw is not a valid object"
        
        
   
        
