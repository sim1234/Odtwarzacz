import os, re, random, wx
from wx.lib.scrolledpanel import ScrolledPanel

def explore(path, pattern = ".*"):
    p = re.compile(pattern)
    w = []
    a = []
    
    try :
        a = os.listdir(path)
    except Exception:
        return []
    
    for e in a:
        tp = os.path.join(path, e)
        #print tp
        if os.path.isdir(tp):
            w.extend(explore(tp, pattern))
        if os.path.isfile(tp) and p.match(tp):
            w.append(tp)
            
    return w


class Library(object):
    def __init__(self, path, pattern = ".*"):
        self.all = explore(path, pattern)
        self.path = path
        self.pattern = pattern
        self.queue = []

    def random(self, amount = 1):
        r = ""
        if len(self.all):
            for x in xrange(0, amount):
                r = random.choice(self.all)
                self.add2q(r)
        return r

    def __iter__(self):
        return self.queue

    def next(self, f = 1):
        if len(self.queue) == 0:
            if f:
                self.random()
            else:
                raise ValueError("Queue is empty!")
        return self.pop()

    def pop(self, i = 0):
        return self.queue.pop(i)

    def add2q(self, item):
        p = re.compile(self.pattern)
        if os.path.isfile(item) and p.match(item):
            self.queue.append(item)
        else:
            raise ValueError("Invalid file")

    def add2l(self, item):
        p = re.compile(self.pattern)
        if os.path.isfile(item) and p.match(item):
            self.all.append(item)
        else:
            raise ValueError("Invalid file")


class QueueUI(ScrolledPanel):
    def __init__(self, parent, path, pattern, pos = (0,0), size = (50,18)):
        ScrolledPanel.__init__(self, parent, wx.ID_ANY, pos, size)
        #self.SetBackgroundColour((255,255,255))
        self.lib = Library(path, pattern)
        self.q = []

        Sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(Sizer)
        self.SetupScrolling()

    def add(self, item, s = 1):
        if s:
            self.lib.add2q(item)
        i = wx.StaticText(self, -1, os.path.basename(item), (0, 0))
        self.q.append(i)
        s = self.GetSizer()
        s.Add(i, 0, wx.ALL, 0)
        i.Bind(wx.EVT_LEFT_UP, self.OnUp)
        i.Bind(wx.EVT_RIGHT_UP, self.OnDown)
        i.Bind(wx.EVT_MIDDLE_UP, self.OnDel) # wx.EVT_LEFT_DCLICK
        self.refr(0)
        
        #Sizer.Add(self.p, 0, wx.ALIGN_LEFT|wx.ALL, 0)

    def refr(self, r = 1):
        if r:
            self.GetSizer().Clear()
            Sizer = wx.BoxSizer(wx.VERTICAL)
            for n in self.q:
                Sizer.Add(n, 0, wx.ALL, 0)
            self.SetSizer(Sizer, 1)
        self.SetupScrolling(scrollToTop = 0)
        self.Layout()
    
    def next(self):
        try:
            r = self.lib.next(0)
            t = self.q.pop(0)
            t.Show(0)
            t.Destroy()
            self.refr()
            return r
        except ValueError:
            self.random()
            return self.next()

    def random(self, amount = 1):
        r = ""
        for x in xrange(0, amount):
            r = self.lib.random()
            self.add(r, 0)
        return r

    def pop(self, i = 0):
        self.q[i].Show(0)
        self.q[i].Destroy()
        self.q.pop(i)
        self.refr()
        return self.lib.pop(i)
        
        
    def OnUp(self, e):
        i = self.q.index(e.GetEventObject())
        if i > 0:
            self.q[i-1], self.q[i] = self.q[i], self.q[i-1]
            self.lib.queue[i-1], self.lib.queue[i] = self.lib.queue[i], self.lib.queue[i-1]
            self.refr()
        #print "OnUp", i
        #e.Skip()

    def OnDown(self, e):
        i = self.q.index(e.GetEventObject())
        if i < len(self.q)-1:
            self.q[i+1], self.q[i] = self.q[i], self.q[i+1]
            self.lib.queue[i+1], self.lib.queue[i] = self.lib.queue[i], self.lib.queue[i+1]
            self.refr()
        #print "OnDown", i
        #e.Skip()

    def OnDel(self, e):
        i = self.q.index(e.GetEventObject())
        self.pop(i)
        #print "OnDel", i
        #e.Skip()
