import os, sys, re, wx
from wx.lib.scrolledpanel import ScrolledPanel


class Ldir(wx.Panel): # Directory object
    def __init__(self, parent, string = "", pos = (0,0), size = (50,18), pattern = ".*", cache = 0, OnFilePick = lambda x: x):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pos, size)
        #self.SetBackgroundColour((230,255,230))
        self.c = wx.StaticText(self, -1, os.path.basename(string), (18, 2)) # Directory name
        #self.SetFocusIgnoringChildren()
        self.c.Bind(wx.EVT_LEFT_UP, self.OnOpen)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_BUTTON, (16, 16)) # Directory icon
        self.x = wx.StaticBitmap(self, wx.ID_ANY, bmp, pos=(0,0))
        self.x.Bind(wx.EVT_LEFT_UP, self.OnOpen)
        
        self.p = wx.Panel(self, wx.ID_ANY, pos=(18,18)) # wx.Panel for children
        self.p.Show(0)
        Sizer = wx.BoxSizer(wx.VERTICAL)
        self.p.SetSizer(Sizer)
        
        self.SetSize(self.GetBestSize())

        self.loc = string.encode(sys.getfilesystemencoding()) # Directory path
        self.pattern = pattern # Pattern for acceptable files
        self.cache = cache # Caching bool
        self.OnFilePick = OnFilePick # Function which is called after picking (doble click) a file
        self.el = [] # List of directory children

        if self.cache:
            self.explore()

    def OnOpen(self, e): # Called when directory is clicked. Shows its children
        #print "OnOpen dir"
        if self.cache:
            self.p.Show(not self.p.IsShown())
            self.resiz()
        else:
            if self.p.IsShown():
                self.clear()
            else:
                self.explore()
                self.p.Show(1)
                self.resiz()

    
    def resiz(self): # Recursively sets the best (smallest) size of whole dir, updates the view
        self.p.SetSize(self.p.GetBestSize())
        self.SetSize(self.GetBestSize())
        self.Layout()
        try:
            self.GetParent().GetParent().resiz()
        except AttributeError:
            pass
        
    def dodaj(self, i): # Makes Ldir / Lfile its children
        self.el.append(i)
        i.Reparent(self.p) 
        s = self.p.GetSizer()
        s.Add(i, 0, wx.ALL, 0)
        self.Layout()
        self.p.Layout()

    def clear(self): # Destroys all its children
        for e in self.el:
            e.Show(0)
            e.Destroy()
        self.el = []
        Sizer = wx.BoxSizer(wx.VERTICAL)
        self.p.SetSizer(Sizer, 1)
        self.p.Show(0)
        self.resiz()

    def explore(self): # Explores its path, adds new children (Ldir / Lfile)
        p = re.compile(self.pattern)
##        try:
##            #a = os.listdir(self.loc)
##            (dirpath, dirnames, filenames) = os.walk(self.loc, 0)
##            print "e"
##        except Exception: # Acces denied, filesytem error, etc.
##            return 
        for (dirpath, dirnames, filenames) in os.walk(self.loc, 1):
            for e in dirnames:
                #print e
                tp = os.path.join(self.loc, e)
                c = Ldir(self, tp, pattern = self.pattern, cache = self.cache, OnFilePick = self.OnFilePick)
                if len(c.el) > 0: #  | No empty folders
                    self.dodaj(c) #  |
                else: #              |
                    c.Show(0) #      |
                    c.Destroy() #    |
                #if self.cache:
                #    c.explore()
                    
            for e in filenames:
                #print e
                tp = os.path.join(self.loc, e)
                #print tp
                if p.match(e): # If file maches whith the specified pattern
                    c = Lfile(self, tp, OnFilePick = self.OnFilePick)
                    self.dodaj(c)
            return 


class Lfile(wx.Panel): # File object
    def __init__(self, parent, string = "", pos = (0,0), size = (50,18), OnFilePick = lambda x: x):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pos, size)
        #self.SetBackgroundColour((255,255,255))
        self.c = wx.StaticText(self, -1, os.path.basename(string), (18, 2)) # File name
        #self.SetFocusIgnoringChildren()
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnOpen)
        self.c.Bind(wx.EVT_LEFT_DCLICK, self.OnOpen)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_BUTTON, (16, 16))
        self.e = wx.StaticBitmap(self, wx.ID_ANY, bmp, pos=(0,0)) # File icon
        self.e.Bind(wx.EVT_LEFT_DCLICK, self.OnOpen)
        self.loc = string # File path
        self.OnFilePick = OnFilePick # Function which is called after picking (doble click) a file 
        self.SetSize(self.GetBestSize())

    def OnOpen(self, e): # Calls specified function
        #print "OnOpen file", self.loc
        self.OnFilePick(self.loc)
        e.Skip()

class LfileExplorer(ScrolledPanel): # Scrollable panel. File explorer
    def __init__(self, parent, pos = (0,0), size = (50,18), startpaths = (""), pattern = ".*", cache = 1, OnFilePick = lambda x: x):
        ScrolledPanel.__init__(self, parent, wx.ID_ANY, pos, size, wx.RAISED_BORDER)
        self.SetBackgroundColour((255,255,255))
        
        self.OnFilePick = OnFilePick # Function which is called after picking (doble click) a file 
        
        Sizer = wx.BoxSizer(wx.VERTICAL)
        self.p = []
        self.d = []
        x = 0
        for p in startpaths:
            self.p.append(wx.Panel(self, wx.ID_ANY, pos=(0,0))) # Panel, which is being sized like self.d
            Sizer.Add(self.p[x], 0, wx.ALIGN_LEFT|wx.ALL, 0)
            self.d.append(Ldir(self.p[x], p, (0,0), (50,18), pattern, cache, self.OnFilePick)) # Root folders of file explorer
            x += 1
        self.SetSizer(Sizer)
        
        self.locs = startpaths # Start path / Root path
        self.pattern = pattern # Pattern for acceptable files
        self.cache = cache # Caching bool
        self.SetupScrolling()
        #self.SetAutoLayout(1)

    def resiz(self): # Keeps self.p well sized and shows / hides Scrollbars. Is called from its children (only Ldir)
        x = 0
        for n in self.p:    
            self.p[x].SetSize(self.d[x].GetBestSize())
            x += 1
        self.SetupScrolling(scrollToTop = 0)
        self.Layout()
