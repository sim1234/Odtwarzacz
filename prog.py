import wx, os, pygame
from player import MusicPlayer
from explorator import LfileExplorer
from library import QueueUI
from timer import TimeKeeper, TimePicker

MyFilePattern = r"\A(.|^\w)*\.(((m|M)(p|P)3)|((o|O)(g|G)(g|G)))\Z" #".*\.(((m|M)(p|P)3)|((m|M)(p|P)2)|((w|W)(m|M)(a|A))|((a|A)(c|C)3)|((o|O)(g|G)(g|G))|((a|A)(c|C)(c|C)))" #".*\.((mp3|mp2|wma|ac3|ogg|acc)"

class myframe(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=u'Odtwarzacz', size = (800,850))
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

        startPath = "D:\\Gas n' Metal"

        self.d = LfileExplorer(self, (5,5), (300,400), startPath, MyFilePattern, 1, 1, self.OnFilePick)
        #self.l = Library(os.path.abspath("Desktop"), MyFilePattern)
        self.q = QueueUI(self, startPath, MyFilePattern, (310,5), (300,400))
        self.q.random(5)
        #self.p = Player(self, self.OnAskNext, (0,450), (780,100))
        
        #self.l.random(5)
        #pygame.mixer.music.load(self.l.next())
        #pygame.mixer.music.play()
        #pygame.mixer.music.fadeout(5000)
        a = wx.Button(self, -1, "A", (0,410), (60,25))
        a.Bind(wx.EVT_LEFT_UP, self.OR)
        b = wx.Button(self, -1, "B", (70,410), (60,25))
        b.Bind(wx.EVT_LEFT_UP, self.ON)
        c = wx.Button(self, -1, "C", (150,410), (60,25))
        c.Bind(wx.EVT_LEFT_UP, self.OA)

        tp = TimePicker(self, wx.DefaultPosition)
        tp.ShowModal()
        self.lag = tp.GetLag()
        tp.Destroy()
        print "Lag set to", self.lag

        self.tk = TimeKeeper("przerwy.txt", self.lag, self.OnTStart, self.OnTEnd)

        self.mp = MusicPlayer(self, self.OnAskNext, (0,450), (700,100))
        
        self.SetAutoLayout(True)

    def OR(self, e):
        print self.q.random()
        e.Skip()

    def ON(self, e):
        print self.q.next()
        e.Skip()

    def OA(self, e):
        self.mp.play(self.q.next())
        print len(self.q.q), self.q.q
        print len(self.q.lib.queue), self.q.lib.queue
        e.Skip()
        
    def onAbout(self, e):
        d = wx.MessageDialog(self, u"Ten program został stworzony w celach edukacyjnych przez Sim", u"O programie", wx.OK)
        d.ShowModal()
        d.Destroy()
        #e.Skip()

    def onExit(self, e):
        self.tk.stop()
        self.Close(True)
        e.Skip() 

    def OnFilePick(self, path):
        self.q.add(path)

    def OnAskNext(self):
        self.mp.play(self.q.next(), 1)

    def OnTStart(self):
        self.mp.mp.stop()
        self.mp.play(self.q.next(), 1)
        print "Start"

    def OnTEnd(self):
        self.mp.pause()
        #self.mp.mp.stop()
        print "End"

def main():
    app = wx.PySimpleApp()
    frame = myframe()
    frame.Show()
    app.MainLoop()
    

if __name__ == '__main__':
    main()
