# python import
import wx


def create_toolbar_button(parent, size, filepath, filepath_pressed, callback_func):
    bitmap = wx.Bitmap(filepath)
    bitmap_pressed = wx.Bitmap(filepath_pressed)

    button = wx.Button(parent, wx.ID_ANY, style=wx.BU_EXACTFIT)
    
    button.SetMaxSize(size)
    button.SetBitmap(bitmap)
    button.SetBitmapPressed(bitmap_pressed)
    button.Bind(wx.EVT_BUTTON, callback_func)

    return button


def create_toolbar_button_sized(parent, icon_size, button_size, filepath, filepath_pressed, callback_func):
    image = wx.Image(filepath)
    image_pressed = wx.Image(filepath_pressed)

    bitmap = wx.Bitmap(image.Scale(icon_size[0], icon_size[1]))
    bitmap_pressed = wx.Bitmap(image_pressed.Scale(icon_size[0], icon_size[1]))

    button = wx.Button(parent, wx.ID_ANY, style=wx.BU_EXACTFIT)
    
    button.SetMaxSize(button_size)
    button.SetBitmap(bitmap)
    button.SetBitmapPressed(bitmap_pressed)
    button.Bind(wx.EVT_BUTTON, callback_func)

    return button