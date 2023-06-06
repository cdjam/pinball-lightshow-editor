# python imports
import wx

# local imports
import __init__
import frame_main


class GuiApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        
        
    def OnInit(self):
        self._frame = frame_main.FrameMain()
        
        self.SetTopWindow(self._frame)
        
        self._frame.Show()
        
        return True
        
        
def main():
    app = GuiApp()
    
    app.MainLoop()
    

if __name__ == "__main__":
    print("Pinball Lightshow Editor v{}".format(__init__.__version__))
    main()