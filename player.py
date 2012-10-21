import os, wx, threading, vlc, shutil, time

class SubProces(threading.Thread):
            def __init__(self, function, lag = 0):
                threading.Thread.__init__(self)
                self.function = function
                self.lag = lag / 1000.0
                self.start()
          
            def run(self):
                if self.lag:
                    time.sleep(self.lag)
                self.function()

class Timer(threading.Thread):
            def __init__(self, function, lag = 0):
                threading.Thread.__init__(self)
                self.function = function
                self.lag = lag / 1000.0
                self.running = True
                self.start()
          
            def run(self):
                while self.running:
                    try:
                        self.function()
                    except Exception as e:
                        print "Timer function error:", e
                        #self.running = False
                        #break
                        return
                    time.sleep(self.lag)

            def stop(self):
                self.running = False
                self.join(0)

class Delete(threading.Thread):
            def __init__(self, path, now = False):
                threading.Thread.__init__(self)
                self.path = path
                if now:
                    self.run()
                else:
                    self.start()
          
            def run(self):
                try:
                    os.remove(self.path)
                except Exception as e:
                    try:
                        shutil.rmtree(self.path)
                    except Exception as e2:
                        #print "Delete Error"#, e, e2
                        pass


class TmpFileOperator(object):
            def __init__(self, path = ""):
                self.todel = []
                self.inuse = []
                self.dir = ""
                if not path:
                    try:
                        self.dir = os.path.join(os.getcwd(), "MyTEMP")
                        Delete(self.dir, 1)
                        os.mkdir(self.dir)
                        self.path = self.dir
                    except:
                        self.dir = ""
                        self.path = os.getcwd()
                else:
                    self.path = path
                
                self.fname = "delete_this_" #file_if_the_program_is_not_running_"

            def temp(self, path):
                ext = self.ext(path)
                x = 0
                npath = ""
                while 1:
                    npath = os.path.join(self.path, self.fname + str(x) + ext)
                    if os.path.isfile(npath):
                        x += 1
                        continue
                    else:
                        break
                    
                try:
                    shutil.copy(os.path.abspath(path), npath)
                    self.inuse.append(npath)
                except Exception as e:
                    #print "Copy Error", e
                    npath = path
                    
                SubProces(self.delete, 1000)
                return npath

            def check(self, now = 0):
                for f in self.inuse:
                    try:
                        t = open(f)
                        t.close()
                        self.todel.append(f)
                        self.inuse.pop(self.inuse.index(f))
                        #print f, "to delete"
                    except Exception:
                        #print f, "in use"
                        pass
                self.delete(now = now)

            def delete(self, i = -1, now = 1):
                if i >= 0:
                    self.todel.append(self.inuse.pop(i))

                for f in self.todel:
                    Delete(f, now)

            def add2delete(self, path):
                if path in self.inuse:
                    self.todel.append(self.inuse.pop(self.inuse.index(path)))


            def ext(self, path):
                p = -1
                while(path.find(".", p + 1) != -1):
                    p = path.find(".", p + 1)
                return path[p:]

            def __del__(self):
                #print "deleting"
                self.check()
                if self.dir:
                    Delete(self.dir, 1)


class Player(object):
            def __init__(self, OnMusicEnd):
                self.OnMusicEnd = OnMusicEnd
                self.paused = 1
                self.loaded = True
                self.path = ""
                self.TFO = TmpFileOperator()
                
                self.Instance = vlc.Instance()
                self.new_player()

            def new_player(self):
                self.player = self.Instance.media_player_new()
                self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.OnEnd)
                self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.OnPlay)

            @vlc.callbackmethod
            def OnEnd(self, e):
                print "Ended"
                SubProces(self.OnMusicEnd, 1000)

            @vlc.callbackmethod
            def OnPlay(self, e):
                if not self.loaded:
                    self.player.set_pause(1)
                    SubProces(self.OnLoaded, 200)
                else:
                    self.OnLoaded()

            def OnLoaded(self):
                if self.paused:
                    self.player.set_pause(1)
                else:
                    self.player.set_pause(0)
                self.loaded = True
                            

            def play(self, path = "", play = 1):
                print "Play", play, path
                while (not self.loaded):
                    print "Me lagsta"
                    time.sleep(0.1)
                
                if path:
                    try:
                        #self.stop()
                        self.loaded = False
                        self.TFO.add2delete(self.path)
                        self.path = path
                        tmpPath = self.TFO.temp(path)
                        #self.new_player()
                        self.Media = self.Instance.media_new(tmpPath)
                        if not self.Media:
                            raise Exception
                        self.player.set_media(self.Media)
                        #print "Loaded"
                    except Exception as e:
                        print "Error!!!", e
                        self.OnEnd(None)
                if play:
                    print "Played"
                    self.paused = 0
                    self.player.play()
                    self.player.set_pause(0)
                else:
                    self.pause()

                
            def pause(self):
                print "Paused"
                self.paused = 1
                self.player.set_pause(1)
                
            def stop(self):
                print "Stopped"
                self.pause()
                self.player.stop()

            def ms2format(self, ms, delimiter = ":"):
                ms = int(round(ms / 1000.0))
                s = ms % 60
                m = (ms - s) / 60
                r = ""
                if m < 10:
                    r += "0"
                r += str(m)
                r += delimiter
                if s < 10:
                    r += "0"
                r += str(s)
                return r

            def get_time(self):
                t1 = 0
                t2 = 0
                if self.loaded and self.player.will_play():
                    t1 = max(0, self.player.get_time())
                    t2 = max(0, self.player.get_length())
                return self.ms2format(t1) + " / " + self.ms2format(t2)

            def __del__(self):
                self.stop()
                #self.TFO.__del__()


class MusicPlayer(wx.Panel):
    def __init__(self, parent, OnNext, pos = (0,0), size = (50,18)):
        wx.Panel.__init__(self, parent, wx.ID_ANY, pos, size)
        #self.SetBackgroundColour((255,255,255))
        self.path = ""
        self.OnNext = OnNext

        Sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pb = wx.Button(self, -1, "Play")
        Sizer.Add(self.pb, 1, wx.ALL|wx.EXPAND, 0)
        self.pb.Bind(wx.EVT_LEFT_UP, self.OnPP)

        stsiz = wx.BoxSizer(wx.VERTICAL)
        
        self.t = wx.StaticText(self, -1, "Looped 4'33''") # os.path.basename(item)
        f = self.t.GetFont()
        f.SetPixelSize((10,25))
        self.t.SetFont(f)
        stsiz.Add(self.t, 3, wx.EXPAND, 0)

        self.ti = wx.StaticText(self, -1, "00:00 / 04:33")
        stsiz.Add(self.ti, 1, wx.ALL, 0)

        Sizer.Add(stsiz, 6, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.nb = wx.Button(self, -1, "Next")
        self.nb.Bind(wx.EVT_LEFT_UP, self.OnN)
        Sizer.Add(self.nb, 1, wx.ALL|wx.EXPAND, 0)

        self.mp = Player(self.next)

        self.timer = Timer(self.UpdateTime, 500)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(Sizer, 1, wx.ALL, 0)
        self.SetSizer(Sizer)
        self.Layout()
        #self.SetAutoLayout(1)

    def UpdateTime(self):
        self.ti.SetLabel(self.mp.get_time())

    def OnPP(self, e):
        #print "OnPP"
        if self.mp.paused:
            self.play()
        else:
            self.pause()
        e.Skip(1)

    def OnN(self, e):
        self.next()
        e.Skip(1)

    def next(self):
        #print "Next"
        t = int(not self.mp.paused)
        self.OnNext()
        self.play(play = t)

    def play(self, path = "", play = 1):
        if path:
            self.path = path
            self.mp.play(path, play)
            self.t.SetLabel(os.path.basename(path))
            self.t.Layout()
        else:    
            self.mp.play(play = play)
            
        if play:
            self.pb.SetLabel("Pause")
        else:
            self.pb.SetLabel("Play")
        

    def pause(self):
        self.mp.pause()
        self.pb.SetLabel("Play")

    def __del__(self):
        #self.mp.__del__()
        self.timer.stop()
        wx.Panel.__del__(self)


