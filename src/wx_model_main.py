import wx
import threading

import model_server

class Logger(object):
    def __init__(self, window):
        self.window = window

    def log(self, str):
        wx.CallAfter(self.window.message, str)

class ServerThread(model_server.Server, threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        model_server.Server.__init__(self, Logger(window))

    def run(self):
        self.handle_connections()

class HUD(wx.Frame):
    def __init__(self):
        super(self.__class__, self).__init__(None, -1, "Space Fortress Model Server", size = (700, 400))
        self.server = ServerThread(self)
        self.server.setDaemon(True)
        self.server.start()

        panel = wx.Panel(self)

        lbl = wx.StaticText(panel, label="Server output:")
        but = wx.Button(panel, label="Quit")
        but.Bind(wx.EVT_BUTTON, self.close)

        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.HSCROLL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.text, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(but, flag=wx.BOTTOM|wx.LEFT, border=5)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)

        self.Center()
        self.Show(True)

    def close(self, e):
        self.Destroy()


    def message(self, data):
        # self.text.SetInsertionPointEnd()
        self.text.AppendText(data + '\n')


if __name__ == '__main__':
    app = wx.App()
    frame = HUD()
    app.MainLoop()
