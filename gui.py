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
   
    def __init__(self, parent, title): 
        super(GeoAltGUI, self).__init__(parent, title = title) 
             
        self.InitUI() 
        self.Centre() 
        self.Show()      
         
    def InitUI(self): 
       
        panel = wx.Panel(self) 
        hlayout = wx.BoxSizer()
    
        
        left_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        # Angle spinner
        ang_l = wx.StaticText(panel, label='Angle')
        left_sizer.Add(ang_l, pos=(0, 0), flag =wx.ALL, border=5)

        self.ang_ct = wx.SpinCtrl(panel)
        self.ang_ct.SetRange(10,80)
        self.ang_ct.SetValue(45)
        left_sizer.Add(self.ang_ct, pos=(0,1), span = (1, 2), flag = wx.EXPAND|wx.ALL, border = 5)

        # Max iterations
        imax_l = wx.StaticText(panel, label='Max iterations')
        left_sizer.Add(imax_l, pos=(1,0), flag=wx.ALL,border=5)
        self.imax_ct = wx.SpinCtrl(panel)
        self.imax_ct.SetRange(0,2000)
        self.imax_ct.SetValue(0)
        left_sizer.Add(self.imax_ct, pos=(1,1), span = (1,2), flag=wx.EXPAND|wx.ALL, border=5)
        
        # Orientation
        or_l = wx.StaticText(panel, label='Orientation:')
        left_sizer.Add(or_l, pos=(2,0), flag=wx.ALL, border=5)

        self.opt_or = wx.CheckBox(panel, label="Analyze optimal orientation")
        left_sizer.Add(self.opt_or, pos=(3,0), span=(1,2), flag=wx.ALL, border=5)
        self.opt_or.SetValue(wx.CHK_CHECKED)
        self.Bind(wx.EVT_CHECKBOX, self.on_toggle_orientation_optimization, self.opt_or)


        x_spin_l = wx.StaticText(panel, label='X rotation')
        self.x_spin = wx.SpinCtrl(panel)
        self.x_spin.SetRange(0,180)
        self.x_spin.SetValue(0)
        self.x_spin.Enable(False)
        left_sizer.Add(x_spin_l, pos=(4, 0), flag =wx.ALL, border=5)
        left_sizer.Add(self.x_spin, pos=(4,1), span=(1,2), flag=wx.EXPAND|wx.ALL,border=5)

        y_spin_l = wx.StaticText(panel, label='Y rotation')
        self.y_spin = wx.SpinCtrl(panel)
        self.y_spin.SetRange(0,180)
        self.y_spin.SetValue(0)
        self.y_spin.Enable(False)
        left_sizer.Add(y_spin_l, pos=(5, 0), flag =wx.ALL, border=5)
        left_sizer.Add(self.y_spin, pos=(5,1), span=(1,2), flag=wx.EXPAND|wx.ALL,border=5)
        

        # Bot buttons
        exec_btn = wx.Button(panel, label = "Run")
        self.Bind(wx.EVT_BUTTON, self.exec_geoalt, exec_btn) 

        left_sizer.Add(exec_btn, pos = (11, 0),flag = wx.ALL, border = 5) 

        # OUTPUT LAYOUT
        vlayout = wx.BoxSizer(orient=wx.VERTICAL)

        self.out_tb = wx.TextCtrl(panel,style=wx.TE_MULTILINE, size=(500, 400)) 
        self.out_tb.AppendText("---STANDARD OUT---\n")

        vlayout.Add(self.out_tb, wx.EXPAND) 

        sys.stdout = StdoutRedirector(self.out_tb)
        sys.stderr = StdoutRedirector(self.out_tb, prefix="ERROR: ")

        # Piece together all elements
        hlayout.Add(left_sizer)
        hlayout.Add(vlayout)
        panel.SetSizerAndFit(hlayout)
        self.Fit()

    def on_toggle_orientation_optimization(self, event):
        if self.x_spin.IsEnabled():
            self.x_spin.Enable(False)
            self.y_spin.Enable(False)
        else:
            self.x_spin.Enable(True)
            self.y_spin.Enable(True)

    def exec_geoalt(self, event):
        self.out_tb.SetValue("")
        angle = int(self.ang_ct.GetValue())*pi/180
        imax = int(self.imax_ct.GetValue())
        
        # Orientation
        optimize_orientation = bool(self.opt_or.GetValue())
        orientation = None
        x_rot = 0
        y_rot = 0
        if optimize_orientation is False:
            x_rot = self.x_spin.GetValue() * pi/180
            y_rot = self.y_spin.GetValue() * pi/180
            orientation = [x_rot, y_rot]

        search_and_solve('models/architecture.stl', 'fixed_models/architecture.stl', 
        max_iterations=imax,
        overwrite_output=True, 
        phi_min=angle, 
        fixed_orientation=orientation)

app = wx.App() 
GeoAltGUI(None, title = 'GeoAlt') 
app.MainLoop()