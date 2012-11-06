##    Copyright (c) 2012 Szymon Zmilczak
##
##
##    This file is part of Odtwarzacz.
##
##    Odtwarzacz is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    Odtwarzacz is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Odtwarzacz; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA



import wx, os
from player import MusicPlayer
from explorator import LfileExplorer
from library import QueueUI
from timer import TimeKeeper, TimePicker

def config(filename):
    f = open(filename)
    c = {}
    for l in f:
        t = l.split("=")
        if len(t[1]) > 0 and t[1][-1] == "\n":
            t[1] = t[1][:-1]
        c[t[0]] = t[1]
    return c

#MyFilePattern = r"\A.*\.(((m|M)(p|P)3)|((o|O)(g|G)(g|G)))\Z" #".*\.(((m|M)(p|P)3)|((m|M)(p|P)2)|((w|W)(m|M)(a|A))|((a|A)(c|C)3)|((o|O)(g|G)(g|G))|((a|A)(c|C)(c|C)))" #".*\.((mp3|mp2|wma|ac3|ogg|acc)"

class myframe(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=u'Odtwarzacz', size = (800,600))
        self.SetBackgroundColour((220,220,255))
        self.SetMinSize((400, 300)) 
        c = config("config.txt")
        
        self.CreateStatusBar()
        filemenu = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, u"O programie",u" Informacje o tym programie")
        menuExit = filemenu.Append(wx.ID_EXIT, u"Wyjście",u" Wychondzi z programu")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, u"&Plik")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_CLOSE, self.onExit)

        #startPath = "D:\\Gas n' Metal"
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        self.te = wx.StaticText(self, -1, u"Biblioteka:", (0, 0))
        f = self.te.GetFont()
        f.SetPixelSize((10,25))
        self.te.SetFont(f)
        sizer3.Add(self.te, 0, wx.BOTTOM, 0)
        self.d = LfileExplorer(self, (0,0), (500,600), c["paths"].split(","), c["file_pattern"], 1, self.OnFilePick)
        sizer3.Add(self.d, 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add(sizer3, 1, wx.RIGHT|wx.EXPAND, 0)

        sizer4 = wx.BoxSizer(wx.VERTICAL)
        self.tq = wx.StaticText(self, -1, u"Kolejka:", (0, 0))
        self.tq.SetFont(f)
        sizer4.Add(self.tq, 0, wx.BOTTOM, 0)
        self.q = QueueUI(self, c["paths"].split(","), c["file_pattern"], (505,0), (500,600))
        sizer4.Add(self.q, 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add(sizer4, 1, wx.ALL|wx.EXPAND, 0)
        
        sizer2.Add(sizer, 6, wx.ALL|wx.EXPAND, 0)
        
        tp = TimePicker(self, wx.DefaultPosition)
        tp.ShowModal()
        self.lag = tp.GetLag()
        tp.Destroy()
        print "Lag set to", self.lag

        self.tk = TimeKeeper("przerwy.txt", self.lag, self.OnTStart, self.OnTEnd, self.UpdateClock)

        self.mp = MusicPlayer(self, self.OnAskNext, (0,450), (700,100))
        self.mp.SetMinSize((200, 100))
        sizer2.Add(self.mp, 0, wx.TOP|wx.EXPAND, 0)

        self.SetSizer(sizer2)
        self.SetAutoLayout(True)

    def UpdateClock(self, time):
        t = (time, 0)
        self.GetStatusBar().SetFields(t[:1])
        
    def onAbout(self, e):
        d = wx.MessageDialog(self, u"Ten program został stworzony w celach edukacyjnych przez Sim1234", u"O programie", wx.OK)
        d.ShowModal()
        d.Destroy()
        #e.Skip()

    def onExit(self, e):
        self.tk.stop()
        self.mp.clean()
        e.Skip()

    def OnFilePick(self, path):
        self.q.add(path)

    def OnAskNext(self):
        return self.q.next()

    def OnTStart(self):
        self.mp.next()
        self.mp.epp(1)
        print "Start"

    def OnTEnd(self):
        self.mp.epp(-1)
        print "End"

def main():
    app = wx.PySimpleApp()
    frame = myframe()
    frame.Show()
    app.MainLoop()
    

if __name__ == '__main__':
    main()
