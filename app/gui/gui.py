import wx

from app.gui.gui_func import brain_starter


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400, -1))

        self.buttonStarter = wx.Button(self, label="Starter.")
        self.Bind(wx.EVT_BUTTON, self.handle_buttonStarter_click, self.buttonStarter)

        self.button = wx.Button(self, label="Ignite Brain.")
        # self.Bind(wx.EVT_BUTTON, self.handle_button_click, self.button)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.button)
        self.sizer.Add(self.buttonStarter)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Show()

    def handle_buttonStarter_click(self, event):
        self.brain = brain_starter()
        # self.Close()


app = wx.App(False)
w = MainWindow(None, "Hello World")
app.MainLoop()
