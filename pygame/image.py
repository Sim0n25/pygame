#!/usr/bin/env python

'''Pygame module for image transfer.

The image module contains functions for loading and saving pictures, as
well as transferring Surfaces to formats usable by other packages.

Note that there is no Image class; an image is loaded as a
Surface object. The Surface class allows manipulation (drawing lines,
setting pixels, capturing regions, etc.).

The image module is a required dependency of Pygame, but it only optionally
supports any extended file formats.  By default it can only load uncompressed
BMP images. When built with full image support, the pygame.image.load()
function can support the following formats.

* JPG
* PNG
* GIF (non animated)
* BMP
* PCX
* TGA (uncompressed)
* TIF
* LBM (and PBM)
* PBM (and PGM, PPM)
* XPM

Saving images only supports a limited set of formats. You can save
to the following formats.

* BMP
* TGA
* PNG
* JPEG

PNG, JPEG saving new in pygame 1.8.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os.path
from SDL import *

import pygame.surface

try:
    from SDL.image import *
    _have_SDL_image = True
except ImportError:
    _have_SDL_image = False

def load_extended(file, namehint=''):
    '''Load new image from a file, using SDL.image.

    :see: `load`

    :Parameters:
        `file` : str or file-like object
            Image file or filename to load.
        `namehint` : str
            Optional file extension.

    :rtype: `Surface`
    '''
    if not _have_SDL_image:
        raise NotImplementedError, 'load_extended requires SDL.image'

    if not hasattr(file, 'read'):
        surf = IMG_Load(file)
    else:
        if not namehint and hasattr(file, 'name'):
            namehint = file.name
        namehint = os.path.splitext(namehint)[1]
        rw = SDL_RWFromObject(file)
        # XXX Should this really be freesrc when we didn't open it?
        surf = IMG_LoadTyped_RW(rw, 1, namehint)
    return pygame.surface.Surface(surf=surf)

def load_basic(file, namehint=''):
    '''Load BMP image from a file.

    :see: `load`

    :Parameters:
        `file` : str or file-like object
            Image file or filename to load.
        `namehint` : str
            Ignored, for compatibility.

    :rtype: `Surface`
    '''
    if not hasattr(file, 'read'):
        surf = SDL_LoadBMP(file)
    else:
        rw = SDL_RWFromObject(file)
        # XXX Should this really be freesrc when we didn't open it?
        surf = SDL_LoadBMP_RW(rw, 1)
    return pygame.surface.Surface(surf=surf)

def load(file, namehint=''):
    '''Load a new image from a file.

    Pygame will automatically determine the image type (e.g., GIF or bitmap)
    and create a new Surface object from the data. In some cases it will need
    to know the file extension (e.g., GIF images should end in ".gif").  If
    you pass a raw file-like object, you may also want to pass the original
    filename as the namehint argument.

    The returned Surface will contain the same color format, colorkey and
    alpha transparency as the file it came from. You will often want to call
    Surface.convert() with no arguments, to create a copy that will draw more
    quickly on the screen.

    For alpha transparency, like in .png images use the convert_alpha() method
    after loading so that the image has per pixel transparency.

    Pygame may not always be built to support all image formats. At minimum it
    will support uncompressed BMP. If pygame.image.get_extended() returns
    'True', you should be able to load most images (including png, jpg and gif).

    You should use os.path.join() for compatibility, e.g.::  
    
        asurf = pygame.image.load(os.path.join('data', 'bla.png'))

    This function calls `load_extended` if SDL.image is available, otherwise
    `load_basic`.

    :Parameters:
        `file` : str or file-like object
            Image file or filename to load.
        `namehint` : str
            Optional file extension.

    :rtype: `Surface`    
    '''
    if _have_SDL_image:
        return load_extended(file, namehint)
    else:
        return load_basic(file, namehint)

def save(surface, file):
    '''Save an image to disk.

    This will save your Surface as either a BMP, TGA, PNG, or JPEG image. If
    the filename extension is unrecognized it will default to TGA. Both TGA,
    and BMP file formats create uncompressed files.  

    :note: Only BMP is currently implemented.

    :Parameters:
        `surface` : `Surface`
            Surface containing image data to save.
        `file` : str or file-like object
            File or filename to save to.

    '''
    if surface._surf.flags & SDL_OPENGL:
        raise NotImplementedError, 'TODO: OpenGL surfaces'
    else:
        surface._prep()

    if hasattr(file, 'write'):
        # TODO TGA not BMP save
        rw = SDL_RWFromObject(file)
        # XXX Should this really be freesrc when we didn't open it?
        SDL_SaveBMP_RW(surface._surf, rw, 1)  
    else:
        fileext = os.path.splitext(file)[1].lower()
        if fileext == '.bmp':
            SDL_SaveBMP(surface._surf, file)
        elif fileext in ('.jpg', '.jpeg'):
            raise pygame.base.error, 'No support for jpg compiled in.'
        elif fileext == '.png':
            raise pygame.base.error, 'No support for png compiled in.'
        else:
            raise NotImplementedError, 'TODO: TGA support'
    
    if surface._surf.flags & SDL_OPENGL:
        pass # TODO
    else:
        surface._unprep()


def get_extended():
    '''Test if extended image formats can be loaded.

    If pygame is built with extended image formats this function will return
    True.  It is still not possible to determine which formats will be
    available, but generally you will be able to load them all.

    :rtype: bool
    '''
    return _have_SDL_image

def tostring(surface, format, flipped=False):
    '''Transfer image to string buffer.

    Creates a string that can be transferred with the 'fromstring' method in
    other Python imaging packages. Some Python image packages prefer their
    images in bottom-to-top format (PyOpenGL for example). If you pass True
    for the flipped argument, the string buffer will be vertically flipped.

    The format argument is a string of one of the following values. Note that
    only 8bit Surfaces can use the "P" format. The other formats will work for
    any Surface. Also note that other Python image packages support more
    formats than Pygame.

    * P, 8bit palettized Surfaces
    * RGB, 24bit image 
    * RGBX, 32bit image with alpha channel derived from color key
    * RGBA, 32bit image with an alpha channel
    * ARGB, 32bit image with alpha channel first
    
    :Parameters:
        `surface` : `Surface`
            Surface containing data to convert.
        `format` : str
            One of 'P', 'RGB', 'RGBX', 'RGBA' or 'ARGB'
        `flipped` : bool
            If True, data is ordered from bottom row to top.

    :rtype: str
    '''
    surf = surface._surf
    if surf.flags & SDL_OPENGL:
        raise NotImplementedError, 'TODO: OpenGL support.'

    rows = []
    pitch = surf.pitch
    w = surf.w

    if flipped:
        h_range = range(surf.h - 1, 0, -1)
    else:
        h_range = range(surf.h)

    if format == 'P':
        if surf.format.BytesPerPixel != 1:
            raise ValueError, \
                  'Can only create "P" format data with 8bit Surfaces'

        surface.lock()
        pixels = surf.pixels.to_string()
        surface.unlock()

        if pitch == w:
            rows = [pixels] # easy exit
        else:
            for y in h_range:
                rows.append(pixels[y*pitch:y*pitch + w])
    else:
        surface.lock()
        if surf.format.BytesPerPixel == 1:
            palette = surf.format.palette.colors
            if surf.flags & SDL_SRCCOLORKEY and not Amask and format == 'RGBX':
                colorkey = surf.format.colorkey
                pixels = [(palette[c].r, palette[c].g, palette[c].b, 
                           (c != colorkey) * 0xff) \
                          for c in surf.pixels]
            else:
                pixels = [(palette[c].r, palette[c].g, palette[c].b, 255) \
                          for c in surf.pixels]
        else:
            Rmask = surf.format.Rmask
            Gmask = surf.format.Gmask
            Bmask = surf.format.Bmask
            Amask = surf.format.Amask
            Rshift = surf.format.Rshift
            Gshift = surf.format.Gshift
            Bshift = surf.format.Bshift
            Ashift = surf.format.Ashift
            Rloss = surf.format.Rloss
            Gloss = surf.format.Gloss
            Bloss = surf.format.Bloss
            Aloss = surf.format.Aloss
            if surf.flags & SDL_SRCCOLORKEY and not Amask and format == 'RGBX':
                colorkey = surf.format.colorkey
                pixels = [( ((c & Rmask) >> Rshift) << Rloss,
                            ((c & Gmask) >> Gshift) << Gloss,
                            ((c & Bmask) >> Bshift) << Bloss,
                            (c != colorkey) * 0xff ) \
                          for c in surf.pixels]
            else:
                pixels = [( ((c & Rmask) >> Rshift) << Rloss,
                            ((c & Gmask) >> Gshift) << Gloss,
                            ((c & Bmask) >> Bshift) << Bloss,
                            ((c & Amask) >> Ashift) << Aloss ) \
                          for c in surf.pixels]
        surface.unlock()
        if format == 'RGB':
            for y in h_range:
                rows.append(''.join([ chr(c[0]) + chr(c[1]) + chr(c[2]) \
                                      for c in pixels[y*pitch:y*pitch + w] ]))
        elif format in ('RGBA', 'RGBX'):
            for y in h_range:
                rows.append(''.join([ chr(c[0]) + chr(c[1]) + chr(c[2]) + \
                                      chr(c[3]) \
                                      for c in pixels[y*pitch:y*pitch + w] ]))
        elif format == 'ARGB':
            for y in h_range:
                rows.append(''.join([ chr(c[3]) + chr(c[1]) + chr(c[2]) + \
                                      chr(c[0]) \
                                      for c in pixels[y*pitch:y*pitch + w] ]))

    if surf.flags & SDL_OPENGL:
        pass # TODO

    return ''.join(rows)

def fromstring(string, size, format, flipped=False):
    '''Create new Surface from a string buffer.

    This function takes arguments similar to pygame.image.tostring(). The size
    argument is a pair of numbers representing the width and height. Once the
    new Surface is created you can destroy the string buffer.

    The size and format image must compute the exact same size as the passed
    string buffer. Otherwise an exception will be raised. 

    See the pygame.image.frombuffer() method for a potentially faster way to
    transfer images into Pygame.

    :Parameters:
        `string` : str
            String containing image data.
        `size` : (int, int)
            Width, height of the image.
        `format` : str
            One of 'P', 'RGB', 'RGBX', 'RGBA' or 'ARGBA'
        `flipped` : bool
            If True, data is ordered from bottom row to top.

    :rtype: `Surface`
    '''
def frombuffer(string, size, format):
    '''Create a new Surface that shares data inside a string buffer.

    Create a new Surface that shares pixel data directly from the string buffer.
    This method takes the same arguments as pygame.image.fromstring(), but is
    unable to vertically flip the source data.

    This will run much faster than pygame.image.fromstring, since no pixel data
    must be allocated and copied.

    :Parameters:
        `string` : str
            String containing image data.
        `size` : (int, int)
            Width, height of the image.
        `format` : str
            One of 'P', 'RGB', 'RGBX', 'RGBA' or 'ARGBA'
    
    :rtype: `Surface`
    '''


try:
    import pygame.imageext
    _is_extended = True
except ImportError:
    _is_extended = False
