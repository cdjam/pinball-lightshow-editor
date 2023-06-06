import time
import wx

class Sprite:
    def __init__(self, image_path, x, y):
        self.bitmap = wx.Bitmap(image_path)
        self.x = x
        self.y = y
    
        size = self.bitmap.GetSize()
        self.width = size[0]
        self.height = size[1]
        
        self._enabled = False
        self._visible = False # solid or flashing on
        self._flashing = False
        self._flashMicros = 0
        self._startFlashMicros = 0
        
        
    def enable(self):
        self._enabled = True
        self._visible = True
        
        
    def disable(self):
        self._enabled = False
        self._flashing = False
        self._visible = False
        
        
    def flash(self, flashMicros):
        if not self._flashing:
            self._flashMicros = flashMicros
            self._flashing = True
            self._startFlashMicros = time.time_ns() / 1000
            self._visible = True
            
        
    def update(self):
        current_micros = time.time_ns() / 1000
        
        if self._flashing:
            if current_micros >= self._startFlashMicros + self._flashMicros:
                self._visible = not self._visible
                self._startFlashMicros = current_micros
                
                
    def is_visible(self):
        return self._visible
        
        
    def is_enabled(self):
        return self._enabled