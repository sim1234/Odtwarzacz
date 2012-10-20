import time, threading, re, wx
from player import Timer
from wx.lib.masked import TimeCtrl
        

class TimePicker(wx.Dialog):
    def __init__(self, parent, pos = (0,0), size = (200,110)):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Korekta czasu", pos, size)

        #self.SetBackgroundColour((230,255,230))        
        
        Sizer1 = wx.BoxSizer(wx.VERTICAL)

        self.c = wx.StaticText(self, -1, u"Podaj aktualną godzinę:")
        Sizer1.Add(self.c, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)

        self.tc = TimeCtrl(self, -1, fmt24hr = True)
        Sizer1.Add(self.tc, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        self.tc.SetValue(wx.DateTime.Now())

        self.ok = wx.Button(self, -1, "OK")
        self.ok.Bind(wx.EVT_BUTTON, self.OnConfirm)
        Sizer1.Add(self.ok, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)

        self.t = Timer(self.OnUpdate, 1000)
        
        self.SetSizer(Sizer1)
        self.Layout()

    def OnConfirm(self, e):
        self.t.stop()
        e.Skip()
        self.EndModal(1)

    def OnUpdate(self):
        value = self.tc.GetValue(as_wxTimeSpan = 1)#as_wxDateTime, as_mxDateTime, as_wxTimeSpan, as_mxDateTimeDelta
        value += wx.TimeSpan(0, 0, 1, 0)
        sel = self.tc.GetSelection()
        self.tc.ChangeValue(value)
        self.tc.SetSelection(sel[0], sel[1])

    def GetLag(self):
        now = wx.DateTime.Now()
        t = now - now.GetDateOnly()
        return self.tc.GetValue(as_wxTimeSpan = 1) - t


class TimeKeeper(threading.Thread):
    def __init__(self, path, lag, OnStart, OnEnd):
        threading.Thread.__init__(self)
        self.path = path
        self.lag = lag
        self.OnStart = OnStart
        self.OnEnd = OnEnd
        self.loadlib()
        self.start()

    def loadlib(self):
        self.table = []
        p = re.compile(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})")
        f = open(self.path, "r")
        for l in f:
            m = p.search(l)
            self.table.append(((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4)))))
            # ^ Adds to self.table touple of 2 touples: ((hs, ms), (he, me)) where h?, m? = huors, minutes; ?s = start, ?e = end
        print self.table        

    def run(self):
        pass
