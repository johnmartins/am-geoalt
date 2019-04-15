import wx
import sys
from handle_stl import search_and_solve
from numpy import pi

class StdoutRedirector(object):
    '''
    Used to redirect STDout to wherever..
    '''

    def __init__(self, text_ctrl, end='\n', flush=False, prefix=""):
        self.output = text_ctrl
        self.prefix = prefix

    def write(self, string, end='\n', flush=False):
        self.output.AppendText(self.prefix + " " + string)

    def flush(self):
        pass
    
    def end(self):
        pass

class GeoAltGUI(wx.Frame): 
   
    def __init__(self, parent, title, size): 
        super(GeoAltGUI, self).__init__(parent, title = title, size=size) 
             
        self.InitUI() 
        self.Centre() 
        self.Show()      
         
    def InitUI(self): 
       
        panel = wx.Panel(self) 
        sizer = wx.GridBagSizer(hgap=5, vgap=5)
        # Angle spinner
        ang_l = wx.StaticText(panel, label='Angle:')
        sizer.Add(ang_l, pos=(0, 0), flag =wx.ALL, border=5)

        self.ang_ct = wx.SpinCtrl(panel)
        self.ang_ct.SetRange(10,80)
        self.ang_ct.SetValue(45)
        sizer.Add(self.ang_ct, pos=(0,1), span = (1, 2), flag = wx.EXPAND|wx.ALL, border = 5)

        # STDOUT text box
        out_l = wx.StaticText(panel, label = "Output") 
        sizer.Add(out_l, pos = (3, 0), flag = wx.ALL, border = 5) 

        out_tb = wx.TextCtrl(panel,style =  wx.TE_MULTILINE) 
        out_tb.AppendText("---STANDARD OUT---\n")
        sizer.Add(out_tb, pos = (3,1), span = (1,12), flag = wx.EXPAND|wx.ALL, border = 5) 
        sizer.AddGrowableRow(3) 
        sys.stdout = StdoutRedirector(out_tb)
        sys.stderr = StdoutRedirector(out_tb, prefix="ERROR: ")

        # Bot buttons
        exec_btn = wx.Button(panel, label = "Ok")
        self.Bind(wx.EVT_BUTTON, self.exec_geoalt, exec_btn) 
        buttonClose = wx.Button(panel, label = "Close" ) 

        sizer.Add(exec_btn, pos = (4, 2),flag = wx.ALL, border = 5) 
        sizer.Add(buttonClose, pos = (4, 3), flag = wx.ALL, border = 5)

        panel.SetSizerAndFit(sizer)

    def exec_geoalt(self, event):
        angle = int(self.ang_ct.GetValue())*pi/180
        search_and_solve('models/u_shape_arc.stl', 'fixed_models/u_shape_arc.stl', overwrite_output=True, phi_min=angle, fixed_orientation=[0,0])

app = wx.App() 
GeoAltGUI(None, title = 'GeoAlt', size=(800, 600)) 
app.MainLoop()