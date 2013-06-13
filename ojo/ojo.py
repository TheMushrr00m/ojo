#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (c) 2012, Peter Levi <peterlevi@peterlevi.com>
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import os
import sys

class Ojo(Gtk.Window):
    def __init__(self):
        super(Ojo, self).__init__()
        self.full = False
        self.screen = self.get_screen()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        #self.maximize()

        self.visual = self.screen.get_rgba_visual()
        if self.visual and self.screen.is_composited():
            self.set_visual(self.visual)
        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)

        self.box = Gtk.VBox()
        self.box.set_visible(True)
        self.image = Gtk.Image()
        self.image.set_visible(True)
        self.box.add(self.image)
        self.add(self.box)

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.SCROLL_MASK)

    def main(self):
        path = os.path.realpath(sys.argv[1])
        print "Started with: " + path
        self.need_orientation = {}
        self.pix_cache = {}
        if os.path.isfile(path):
            self.mode = 'image'
            self.show(path)
            GObject.idle_add(self.after_quick_start)
        else:
            self.mode = 'folder'
            self.current = os.path.join(path, 'none')
            self.after_quick_start()
            self.set_mode('folder')
            self.show(self.images[0])

        self.set_visible(True)
        Gtk.main()

    def area_draw(self, widget, cr):
        if self.full:# and self.mode == "image":
            if self.mode == 'folder':
                cr.set_source_rgba(77.0/255, 75.0/255, 69.0/255, 1)
            else:
                cr.set_source_rgba(0, 0, 0, 1.0)
        else:
            cr.set_source_rgba(77.0/255, 75.0/255, 69.0/255, 0.9)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def js(self, command):
        GObject.idle_add(lambda: self.web_view.execute_script(command))

    def update_browser(self, file):
        self.js("select('%s')" % file)

    def show(self, filename=None, orient=False):
        if filename:
            print filename
        filename = filename or self.current
        self.current = filename
        self.selected = self.current
        self.set_title(self.current)
        if getattr(self, "web_view", None):
            self.update_browser(self.current)
        self.pixbuf, oriented = self.get_pixbuf(self.current, orient)
        self.image.set_from_pixbuf(self.pixbuf)
        self.update_size()

        if not orient and not oriented:
            def _check_orientation():
                meta = self.get_meta(filename)
                if self.current == filename and self.needs_orientation(meta):
                    self.show(self.current, True)
            GObject.idle_add(_check_orientation)

        if hasattr(self, "cache_callback_id"):
            GObject.source_remove(self.cache_callback_id)
        self.cache_callback_id = GObject.timeout_add(300, self.cache_around)

    def cache_around(self):
        if not hasattr(self, "images"):
            return
        pos = self.images.index(self.current)
        for f in self.images[pos - 1 : pos + 5]:
            if not f in self.pix_cache:
                def a(f):
                    def _do():
                        print "caching around: " + f
                        self.get_pixbuf(f, False)
                    return _do
                GObject.idle_add(a(f))

    def get_meta(self, filename):
        from pyexiv2 import ImageMetadata
        meta = ImageMetadata(filename)
        meta.read()
        self.need_orientation[filename] = self.needs_orientation(meta)
        return meta

    def set_margins(self, margin):
        self.box.set_margin_right(margin)
        self.box.set_margin_left(margin)
        self.box.set_margin_bottom(margin)
        self.box.set_margin_top(margin)

    def update_size(self):
        if self.mode == 'folder':
            self.set_margins(15)
        elif self.full:
            self.set_margins(0)
        else:
            self.set_margins(30)

        if self.mode == "image":
            self.real_width = self.pixbuf.get_width() + 60
            self.real_height = self.pixbuf.get_height() + 60
        else:
            self.real_width = self.screen.get_width() - 90
            self.real_height = self.screen.get_height() - 90
            if self.real_width > 1.5 * self.real_height:
                self.real_width = int(1.5 * self.real_height)
            else:
                self.real_height = int(self.real_width / 1.5)

        if not self.full:
            self.resize(self.real_width, self.real_height)
            self.move((self.screen.get_width() - self.real_width) // 2,
                (self.screen.get_height() - self.real_height) // 2)

    def go(self, direction, start_position=None):
        filename = None
        try:
            position = start_position - direction if not start_position is None else self.images.index(self.current)
            position = (position + direction + len(self.images)) % len(self.images)
            filename = self.images[position]
            self.show(filename)
            return
        except Exception, ex:
            print str(ex), filename
            GObject.idle_add(lambda: self.go(direction))

    def toggle_fullscreen(self, full=None):
        if full is None:
            full = not self.full
        self.pix_cache.clear()
        self.full = full
        if self.full:
            self.fullscreen()
        else:
            self.unfullscreen()
        self.update_cursor()
        self.show()

    def update_cursor(self):
        if self.get_window():
            self.get_window().set_cursor(Gdk.Cursor.new_for_display(Gdk.Display.get_default(),
                Gdk.CursorType.BLANK_CURSOR if self.full and self.mode == 'image' else Gdk.CursorType.ARROW))

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == "image" and self.selected != self.current:
            self.show(self.selected)
        else:
            self.update_size()
        self.update_cursor()
        self.image.set_visible(self.mode == 'image')
        self.browser.set_visible(self.mode == 'folder')

    def process_key(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        print key
        if key == 'Escape':
            Gtk.main_quit()
        elif key in ("f", "F", "F11"):
            self.toggle_fullscreen()
            self.show()
        elif key == 'Return':
            modes = ["image", "folder"]
            self.set_mode(modes[(modes.index(self.mode) + 1) % len(modes)])
        elif self.mode == 'folder':
            self.js("on_key('%s')" % key)
        elif key == 'F5':
            self.show()
        elif key in ("Right", "Down", "Page_Down", "space"):
            GObject.idle_add(lambda: self.go(1))
        elif key in ("Left", "Up", "Page_Up", "BackSpace"):
            GObject.idle_add(lambda: self.go(-1))
        elif key == "Home":
            GObject.idle_add(lambda: self.go(1, 0))
        elif key == "End":
            GObject.idle_add(lambda: self.go(-1, len(self.images) - 1))

    def clicked(self, widget, event):
        import time
        if self.mode != "image":
            return
        if time.time() - self.from_browser_time < 0.2:
            return
        if event.button == 1:
            self.go(-1 if event.x < 0.5 * self.real_width else 1)

    def scrolled(self, widget, event):
        if self.mode != "image":
            return
        if event.direction not in (
            Gdk.ScrollDirection.UP, Gdk.ScrollDirection.LEFT, Gdk.ScrollDirection.DOWN, Gdk.ScrollDirection.RIGHT):
            return

        if getattr(self, "wheel_timer", None):
            GObject.source_remove(self.wheel_timer)

        direction = -1 if event.direction in (Gdk.ScrollDirection.UP, Gdk.ScrollDirection.LEFT) else 1
        self.wheel_timer = GObject.timeout_add(100, lambda: self.go(direction))

    def after_quick_start(self):
        self.mode = "image"
        self.from_browser_time = 0

        self.browser = Gtk.ScrolledWindow()
        self.browser.set_visible(False)
        rgba = Gdk.RGBA()
        rgba.parse('rgba(0, 0, 0, 0)')
        self.browser.override_background_color(Gtk.StateFlags.NORMAL, rgba)
        self.box.add(self.browser)

        self.connect("delete-event", Gtk.main_quit)
        self.connect("key-press-event", self.process_key)
        #self.connect("focus-out-event", Gtk.main_quit)
        self.connect("button-release-event", self.clicked)
        self.connect("scroll-event", self.scrolled)
        self.folder = os.path.dirname(self.current)
        self.images = filter(os.path.isfile, map(lambda f: os.path.join(self.folder, f), sorted(os.listdir(self.folder))))

        GObject.idle_add(self.render_browser)
        self.cache_callback_id = GObject.timeout_add(200, self.cache_around)

    def render_browser(self):
        from gi.repository import WebKit

        with open(os.path.join(os.path.dirname(os.path.normpath(__file__)), 'browse.html')) as f:
            html = f.read()

        self.web_view = WebKit.WebView()
        self.web_view.set_transparent(True)

        def nav(wv, wf, title):
            import time
            import json

            index = title.index(':')
            action = title[:index]
            argument = title[index + 1:]

            if action in ('ojo', 'ojo-select'):
                self.selected = argument
                if action == 'ojo':
                    def _do():
                        self.show(self.selected)
                        self.from_browser_time = time.time()
                        self.set_mode("image")
                    GObject.idle_add(_do)
            elif action == 'ojo-priority':
                files = json.loads(argument)
                self.priority_thumbs(map(lambda f: f.encode('utf-8'), files))
        self.web_view.connect("title-changed", nav)

        self.thumb_queue = None
        self.web_view.connect('document-load-finished', lambda wf, data: self.prepare_thumbs()) # Load page

        self.web_view.load_string(html, "text/html", "UTF-8", "file://" + os.path.dirname(__file__) + "/")
        self.web_view.set_visible(True)
        rgba = Gdk.RGBA()
        rgba.parse('rgba(0, 0, 0, 0)')
        self.web_view.override_background_color(Gtk.StateFlags.NORMAL, rgba)
        self.browser.add(self.web_view)

    def add_thumb(self, img):
        try:
            self.thumb_queue.remove(img)
        except Exception:
            pass

        try:
            b64 = self.b64(img, 500, 120)
            self.js("add_image('%s', '%s')" % (img, b64))
            if img == self.current:
                self.update_browser(img)
        except Exception, e:
            self.js("remove_image_div('%s')" % img)
            print str(e)

    def prepare_thumbs(self):
        if self.thumb_queue is None:
            pos = self.images.index(self.current)
            self.thumb_queue = [x[1] for x in sorted(enumerate(self.images), key=lambda (i,f): abs(i - pos))]
            assert self.thumb_queue[0] == self.current
            for img in self.images:
                self.js("add_image_div('%s', %s)" % (img, 'true' if img==self.current else 'false'))
                if img == self.current:
                    self.update_browser(img)

        if self.thumb_queue:
            img = self.thumb_queue[0]
            self.add_thumb(img)
            if self.thumb_queue:
                def _do():
                    GObject.idle_add(self.prepare_thumbs)
                GObject.timeout_add(50, _do)

    def priority_thumbs(self, files):
        self.thumb_queue = [f for f in files if f in self.thumb_queue] + \
                           [f for f in self.thumb_queue if not f in files]

    def pixbuf_from_data(self, data, width, height):
        from gi.repository import Gio
        input_str = Gio.MemoryInputStream.new_from_data(data, None)
        pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_str, width, height, True, None)
        return pixbuf

    def b64(self, filename, width, height):
        return self.pil_to_base64(self.get_pil(filename, width, height))

    def get_pixbuf(self, filename, orient):
        if filename in self.pix_cache:
            cached = self.pix_cache[filename]
            if not orient or cached[1]:
                print "cache hit: " + filename
                return cached

        width = self.screen.get_width() if self.full else self.screen.get_width() - 150
        height = self.screen.get_height() if self.full else self.screen.get_height() - 150
        if not orient and (not filename in self.need_orientation or not self.need_orientation[filename]):
            try:
                oriented = filename in self.need_orientation and not self.need_orientation[filename]
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename, width, height, True)
                self.pix_cache[filename] = pixbuf, oriented
                return pixbuf, oriented
            except GObject.GError:
                pass # below we'll use another method
        pixbuf = self.pil_to_pixbuf(self.get_pil(filename, width, height))
        self.pix_cache[filename] = pixbuf, True
        return pixbuf, True

    def get_pil(self, filename, width, height):
        from PIL import Image
        import cStringIO
        meta = self.get_meta(filename)
        try:
            pil_image = Image.open(filename)
        except IOError:
            pil_image = Image.open(cStringIO.StringIO(meta.previews[-1].data))
        pil_image = self.auto_rotate(meta, pil_image)
        pil_image.thumbnail((width, height), Image.ANTIALIAS)
        return pil_image

    def pil_to_base64(self, pil_image):
        import cStringIO
        output = cStringIO.StringIO()
        pil_image.save(output, "PNG")
        contents = output.getvalue().encode("base64")
        output.close()
        return contents.replace('\n', '')

    def pil_to_pixbuf(self, pil_image):
        import cStringIO
        if pil_image.mode != 'RGB':          # Fix IOError: cannot write mode P as PPM
            pil_image = pil_image.convert('RGB')
        buff = cStringIO.StringIO()
        pil_image.save(buff, 'ppm')
        contents = buff.getvalue()
        buff.close()
        loader = GdkPixbuf.PixbufLoader()
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

#        import array
#        if pil_image.mode != 'RGB':
#            pil_image = pil_image.convert('RGB')
#        arr = array.array('B', pil_image.tostring())
#        height, width = pil_image.size
#        return GdkPixbuf.Pixbuf.new_from_data(
#            arr, GdkPixbuf.Colorspace.RGB, True, 8, width, height, width * 4, None, None)

    def needs_orientation(self, meta):
        if 'Exif.Image.Orientation' in meta.keys():
            return meta['Exif.Image.Orientation'].value != 1
        else:
            return False

    def auto_rotate(self, meta, im):
        from PIL import Image
        # We rotate regarding to the EXIF orientation information
        if 'Exif.Image.Orientation' in meta.keys():
            orientation = meta['Exif.Image.Orientation'].value
            if orientation == 1:
                # Nothing
                result = im
            elif orientation == 2:
                # Vertical Mirror
                result = im.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                # Rotation 180°
                result = im.transpose(Image.ROTATE_180)
            elif orientation == 4:
                # Horizontal Mirror
                result = im.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                # Horizontal Mirror + Rotation 270°
                result = im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
            elif orientation == 6:
                # Rotation 270°
                result = im.transpose(Image.ROTATE_270)
            elif orientation == 7:
                # Vertical Mirror + Rotation 270°
                result = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
            elif orientation == 8:
                # Rotation 90°
                result = im.transpose(Image.ROTATE_90)
            else:
                result = im
        else:
            # No EXIF information, the user has to do it
            result = im

        return result

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Ojo().main()
