import wx
import sys
import threading

from numpy import pi
from os import getcwd, path

from geoalt_algorithms.zero_phi_strategy import ZeroPhiStrategy
from geoalt_algorithms.initiator import search_and_solve

class GeoAltThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self._parent = parent

        # Parameters
        self.imax = 0
        self.angle = angle = pi/4
        self.orientation = None
        self.grounded_only = False
        self.angle_tolerance = 0.017
        self.ground_tolerance = 0.01
        self.zero_phi_strategy = ZeroPhiStrategy.NONE

    def set_imax(self, imax):
        self.imax = imax

    def set_angle(self, angle):
        self.angle = angle
    
    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_grounded_only(self, grounded_only):
        self.grounded_only = grounded_only

    def set_ground_tolerance(self, ground_tol):
        self.ground_tolerance = ground_tol

    def set_angle_tolerance(self, angle_tol):
        self.angle_tolerance = angle_tol

    def set_zero_phi_strategy(self, zps):
        self.zero_phi_strategy = zps

    def run(self):
        search_and_solve(self._parent.input_file_f.GetValue(), self._parent.output_file_f.GetValue(), 
        max_iterations=self.imax,
        overwrite_output=True, 
        phi_min=self.angle, 
        fixed_orientation=self.orientation,
        plot=False,
        grounded_only=self.grounded_only,
        ground_tolerance=self.ground_tolerance,
        angle_tolerance=self.angle_tolerance,
        zero_phi_strategy=self.zero_phi_strategy)

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
        super(GeoAltGUI, self).__init__(parent, title = title, style=wx.SYSTEM_MENU | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX) 
             
        self.InitUI() 
        self.Centre() 
        self.Show()      
         
    def InitUI(self): 
       
        panel = wx.Panel(self) 
        hlayout = wx.BoxSizer()
    
        left_sizer = wx.GridBagSizer(hgap=0, vgap=0)

        # Input and output files
        self.input_file_f = wx.TextCtrl(panel, size=(300,25))
        left_sizer.Add(self.input_file_f, pos=(0,0), span=(1,3), flag=wx.ALL, border=5)

        input_file_d = wx.Button(panel, label="Select STL-file")
        input_file_d.Bind(wx.EVT_BUTTON, self.on_open_file)
        left_sizer.Add(input_file_d, pos=(0, 3), flag=wx.ALL|wx.EXPAND, border=5)

        self.output_file_f = wx.TextCtrl(panel, size=(300,25))
        left_sizer.Add(self.output_file_f, pos=(1,0), span=(1,3), flag=wx.ALL, border=5)

        output_file_d = wx.Button(panel, label="Set output path")
        output_file_d.Bind(wx.EVT_BUTTON, self.on_set_output)
        left_sizer.Add(output_file_d, pos=(1,3), flag=wx.ALL|wx.EXPAND, border=5)

        # Angle spinner
        ang_l = wx.StaticText(panel, label='Min Overhang')
        left_sizer.Add(ang_l, pos=(2, 0), flag =wx.ALL, border=5)

        self.ang_ct = wx.SpinCtrl(panel)
        self.ang_ct.SetRange(10,80)
        self.ang_ct.SetValue(45)
        left_sizer.Add(self.ang_ct, pos=(2,1), span = (1, 1), flag = wx.ALL, border = 5)

        geoalt_lbl = wx.StaticText(panel, label='Geometric alteration:')
        left_sizer.Add(geoalt_lbl, pos=(3,0), flag=wx.ALL, border=5)

        # Max iterations
        imax_l = wx.StaticText(panel, label='Max iterations')
        left_sizer.Add(imax_l, pos=(4,0), flag=wx.ALL,border=5)
        self.imax_ct = wx.SpinCtrl(panel)
        self.imax_ct.SetRange(0,2000)
        self.imax_ct.SetValue(0)
        left_sizer.Add(self.imax_ct, pos=(4,1), span = (1,1), flag = wx.ALL, border=5)

        zps_lbl = wx.StaticText(panel, label='0 phi strategy')
        left_sizer.Add(zps_lbl, pos=(5,0), flag=wx.ALL, border=5)
        self.zps_choice = wx.Choice(panel, choices=['None', 'Inject'])
        self.zps_choice.SetSelection(0)
        left_sizer.Add(self.zps_choice,pos=(5,1), span=(1,1), flag=wx.ALL, border=5)
        
        # Orientation
        or_l = wx.StaticText(panel, label='Orientation:')
        left_sizer.Add(or_l, pos=(6,0), flag=wx.ALL, border=5)

        self.opt_or = wx.CheckBox(panel, label="Analyze optimal orientation")
        left_sizer.Add(self.opt_or, pos=(7,0), span=(1,2), flag=wx.ALL, border=5)
        self.opt_or.SetValue(wx.CHK_CHECKED)
        self.Bind(wx.EVT_CHECKBOX, self.on_toggle_orientation_optimization, self.opt_or)

        self.grounded_only = wx.CheckBox(panel, label="Grounded results only")
        left_sizer.Add(self.grounded_only, pos=(8,0), span=(1,2), flag=wx.ALL, border=5)
        self.grounded_only.SetValue(wx.CHK_CHECKED)
        self.Bind(wx.EVT_CHECKBOX, self.on_toggle_grounded_only, self.grounded_only)

        x_spin_l = wx.StaticText(panel, label='X rotation')
        self.x_spin = wx.SpinCtrl(panel)
        self.x_spin.SetRange(0,180)
        self.x_spin.SetValue(0)
        self.x_spin.Enable(False)
        left_sizer.Add(x_spin_l, pos=(9, 0), flag =wx.ALL, border=5)
        left_sizer.Add(self.x_spin, pos=(9,1), span=(1,2), flag=wx.ALL,border=5)

        y_spin_l = wx.StaticText(panel, label='Y rotation')
        self.y_spin = wx.SpinCtrl(panel)
        self.y_spin.SetRange(0,180)
        self.y_spin.SetValue(0)
        self.y_spin.Enable(False)
        left_sizer.Add(y_spin_l, pos=(10, 0), flag =wx.ALL, border=5)
        left_sizer.Add(self.y_spin, pos=(10,1), span=(1,2), flag=wx.ALL,border=5)

        tolerances_txt = wx.StaticText(panel, label='Tolerances:')
        left_sizer.Add(tolerances_txt, pos=(11,0), flag=wx.ALL,border=5)

        grould_lbl = wx.StaticText(panel, label='Ground')
        left_sizer.Add(grould_lbl, pos=(12, 0), border=5, flag=wx.ALL)
        self.ground_ctrl = wx.SpinCtrlDouble(panel)
        self.ground_ctrl.SetRange(0.001,1)
        self.ground_ctrl.SetValue(0.01)
        self.ground_ctrl.SetIncrement(0.001)
        left_sizer.Add(self.ground_ctrl, pos=(12,1), span = (1, 2), border = 5, flag=wx.ALL)

        angle_tol_lbl = wx.StaticText(panel, label='Angle')
        left_sizer.Add(angle_tol_lbl, pos=(13,0), border=5, flag=wx.ALL)
        self.angle_tol_ctrl = wx.SpinCtrlDouble(panel)
        self.angle_tol_ctrl.SetRange(0.001,1)
        self.angle_tol_ctrl.SetValue(0.017)
        self.angle_tol_ctrl.SetIncrement(0.001)
        left_sizer.Add(self.angle_tol_ctrl, pos=(13,1), span = (1,2), border = 5, flag=wx.ALL)
        

        # Bot buttons
        exec_btn = wx.Button(panel, label = "Run")
        self.Bind(wx.EVT_BUTTON, self.exec_geoalt, exec_btn) 

        left_sizer.Add(exec_btn, pos = (14, 0),flag = wx.ALL, border = 5) 

        # OUTPUT LAYOUT
        vlayout = wx.BoxSizer(orient=wx.VERTICAL)

        self.out_tb = wx.TextCtrl(panel,style=wx.TE_MULTILINE, size=(600, 460)) 
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
            self.grounded_only.Enable(True)
        else:
            self.x_spin.Enable(True)
            self.y_spin.Enable(True)
            self.grounded_only.Enable(False)

    def on_toggle_grounded_only(self, event):
        print("Toggled grounded only.")

    def exec_geoalt(self, event):
        self.out_tb.SetValue("")
        angle = int(self.ang_ct.GetValue())*pi/180
        imax = int(self.imax_ct.GetValue())
        grounded_only = bool(self.grounded_only.GetValue())
        tol_ground = float(self.ground_ctrl.GetValue())
        tol_angle = float(self.angle_tol_ctrl.GetValue())
        zps = None

        if self.zps_choice.GetSelection() == 0:
            zps = ZeroPhiStrategy.NONE
        elif self.zps_choice.GetSelection() == 1:
            zps = ZeroPhiStrategy.INJECT
        else:
            raise ValueError("An error occured when setting the zero phi strategy. Please report.")

        
        # Orientation
        optimize_orientation = bool(self.opt_or.GetValue())
        orientation = None
        x_rot = 0
        y_rot = 0
        if optimize_orientation is False:
            x_rot = self.x_spin.GetValue() * pi/180
            y_rot = self.y_spin.GetValue() * pi/180
            orientation = [x_rot, y_rot]
        
        # setup separate thread
        worker = GeoAltThread(self)
        worker.set_angle(angle)
        worker.set_imax(imax)
        worker.set_orientation(orientation)
        worker.set_grounded_only(grounded_only)
        worker.set_ground_tolerance(tol_ground)
        worker.set_angle_tolerance(tol_angle)
        worker.set_zero_phi_strategy(zps)
        worker.start()

    def on_open_file(self, event):
        """
        Create and show the open file dialog
        """
        fd = wx.FileDialog(self,
        "Open STL file",
        "",
        "",
        "STL files (*.stl)|*.stl|All files (*.*)|*.*",
        wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if fd.ShowModal() == wx.ID_OK:
            print("Selected %s" % fd.GetPath())
            self.input_file_f.SetValue(fd.GetPath())
            self.input_file_f.SetInsertionPointEnd()    # Move cursor in text field to end
            self.output_file_f.SetValue(path.dirname(fd.GetPath()) + "\geoalt_" + path.basename(fd.GetPath()))
            self.output_file_f.SetInsertionPointEnd()   # Move cursor in text field to end
        else:
            print("AN ERROR OCCURED")

    def on_set_output(self, event):
        """
        Create and show save file dialog
        """
        fd = wx.FileDialog(self,
        "Output STL file location",
        ".",
        "",
        "STL files (*.stl)|*.stl",
        wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        if fd.ShowModal() == wx.ID_OK:
            print("Selected output path: %s " % fd.GetPath())
            self.output_file_f.SetValue(fd.GetPath())
        

app = wx.App() 
GeoAltGUI(None, title = 'GeoAlt') 
app.MainLoop()