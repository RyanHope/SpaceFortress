#!/usr/bin/env python

# A GUI wrapper around game_events.py. This is for anyone not
# comfortable with the command-line who wants to analyze space
# fortress event log files.

import wx
from threading import Thread
import game_events

class analysis(game_events.analysis, Thread):
    def __init__(self, window, datadir, output_file):
        game_events.analysis.__init__(self, datadir, output_file)
        Thread.__init__(self)
        self.window = window

    def update(self, msg):
        # print(msg)
        wx.CallAfter(self.window.message, msg)

    def run(self):
        try:
            self.scan_and_dump()
        except Exception as e:
            self.update('Error! %s'%e)

class Convert(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Game Event Tool", size = (700, 400))

        panel = wx.Panel(self)

        lbl = wx.StaticText(panel, label="Output:")
        but = wx.Button(panel, label="Generate Spreadsheet")
        but.Bind(wx.EVT_BUTTON, self.doscan)

        self.text = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.HSCROLL)

        # self.drop = FileDrop(self)
        # self.text.SetDropTarget(self.drop)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.text, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(but, flag=wx.BOTTOM|wx.LEFT, border=5)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)

        self.Center()
        self.Show(True)

    def doscan(self, ev):
        # Hard code the values needed for use as a stand-alone OSX app.
        self.analysis = analysis(self, '../../../data/', 'game-events.xlsx')
        self.analysis.setDaemon(True)
        self.analysis.start()

    def close(self, e):
        self.Destroy()

    def message(self, data):
        self.text.AppendText(data + '\n')

if __name__ == '__main__':
    app = wx.App()
    frame = Convert()
    app.MainLoop()
