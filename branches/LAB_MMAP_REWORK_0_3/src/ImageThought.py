# ImageThought.py
# This file is part of labyrinth
#
# Copyright (C) 2006 - Don Scorgie <DonScorgie@Blueyonder.co.uk>
#
# labyrinth is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# labyrinth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with labyrinth; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, 
# Boston, MA  02110-1301  USA
#

import gtk
import xml.dom.minidom as dom
import xml.dom
import gettext
_ = gettext.gettext

import BaseThought
import utils

MODE_EDITING = 0
MODE_IMAGE = 1
MODE_DRAW = 2

class ImageThought (BaseThought.ResizableThought):
	def __init__ (self, coords, pango_context, thought_number, save, loading):
		super (ImageThought, self).__init__(save, "image_thought")

		self.identity = thought_number
		margin = utils.margin_required (utils.STYLE_NORMAL)
		self.want_move = False
		if coords:
			self.ul = (coords[0]-margin[0], coords[1] - margin[1])
			self.pic_location = coords
		else:
			self.ul = None
		self.button_press = False
					
		if not loading:
			self.all_okay = self.open_image ()
		else:
			self.all_okay = True


	def open_image (self, filename = None):
		# Present a dialog for the user to choose an image here
		if not filename:
			fil = gtk.FileFilter ()
			fil.set_name("Images")
			fil.add_pixbuf_formats ()
			dialog = gtk.FileChooserDialog (_("Choose image to insert"), None, gtk.FILE_CHOOSER_ACTION_OPEN, \
			                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			dialog.add_filter (fil)
			res = dialog.run ()
			dialog.hide ()
			if res != gtk.RESPONSE_OK:
				return False
			else:
				fname = dialog.get_filename()
		else:
			fname = filename
		self.filename = fname
		try:
			self.orig_pic = gtk.gdk.pixbuf_new_from_file (fname)
		except:
			return False
		if not filename:
			self.width = self.orig_pic.get_width ()
			self.height = self.orig_pic.get_height ()
			margin = utils.margin_required (utils.STYLE_NORMAL)
		
			self.lr = (self.pic_location[0]+self.width+margin[2], self.pic_location[1]+self.height+margin[3])
			self.pic = self.orig_pic
		self.text = fname[fname.rfind('/')+1:fname.rfind('.')]
		return True

	def draw (self, context):
		utils.draw_thought_outline (context, self.ul, self.lr, self.am_selected, self.am_primary, utils.STYLE_NORMAL)

		if self.pic:
			context.set_source_pixbuf (self.pic, self.pic_location[0], self.pic_location[1])
			context.rectangle (self.pic_location[0], self.pic_location[1], self.width, self.height)
			context.fill ()
		context.set_source_rgb (0,0,0)

	def export (self, context, move_x, move_y):
		utils.export_thought_outline (context, self.ul, self.lr, self.am_selected, self.am_primary, utils.STYLE_NORMAL,
									  (move_x, move_y))

		if self.pic:
			context.set_source_pixbuf (self.pic, self.pic_location[0]+move_x, self.pic_location[1]+move_y)
			context.rectangle (self.pic_location[0]+move_x, self.pic_location[1]+move_y, 
							   self.width, self.height)
			context.fill ()
		context.set_source_rgb (0,0,0)

	def want_motion (self):
		return self.want_move

	def recalc_edges (self):
		margin = utils.margin_required (utils.STYLE_NORMAL)
		self.pic_location = (self.ul[0]+margin[0], self.ul[1]+margin[1])
		self.lr = (self.pic_location[0]+self.width+margin[2], self.pic_location[1]+self.height+margin[3])

	def process_button_down (self, event, mode):
		modifiers = gtk.accelerator_get_default_mod_mask ()
		self.button_down = True
		if mode != MODE_EDITING:
			return False
		if event.button == 1:
			if event.type == gtk.gdk.BUTTON_PRESS:
				self.emit ("select_thought", event.state & modifiers)
				self.emit ("update_view")
			if self.resizing != self.RESIZE_NONE:
				self.want_move = True
				return True
		elif event.button == 3:
			self.emit ("popup_requested", (event.x, event.y), 1)
		self.emit ("update_view")
		

	def process_button_release (self, event, unending_link, mode):
		self.button_down = False
		if unending_link:
			unending_link.set_child (self)
			self.emit ("claim_unending_link")
		if self.orig_pic:
			self.pic = self.orig_pic.scale_simple (int(self.width), int(self.height), gtk.gdk.INTERP_HYPER)
		self.emit ("update_view")
		self.want_move = False
	
	def handle_motion (self, event, mode):
		if self.resizing == self.RESIZE_NONE or not self.want_move or not event.state & gtk.gdk.BUTTON1_MASK:
			if not event.state & gtk.gdk.BUTTON1_MASK:
				return False
			elif mode == MODE_EDITING:
				self.emit ("create_link", \
				 (self.ul[0]-((self.ul[0]-self.lr[0]) / 2.), self.ul[1]-((self.ul[1]-self.lr[1]) / 2.)))
			return True
		diffx = event.x - self.motion_coords[0]
		diffy = event.y - self.motion_coords[1]
		tmp = self.motion_coords
		self.motion_coords = (event.x,event.y)
		if self.resizing == self.RESIZE_LEFT:
			if self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1])
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1])
			self.width -= diffx
		elif self.resizing == self.RESIZE_RIGHT:
			if self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0]+diffx, self.lr[1])
			self.width += diffx
		elif self.resizing == self.RESIZE_TOP:
			if self.height - diffy < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0], self.ul[1]+diffy)
			self.pic_location = (self.pic_location[0], self.pic_location[1]+diffy)
			self.height -= diffy
		elif self.resizing == self.RESIZE_BOTTOM:
			if self.height + diffy < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0], self.lr[1]+diffy)
			self.height += diffy
		elif self.resizing == self.RESIZE_UL:
			if self.height - diffy < 10 or self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1]+diffy)
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1]+diffy)
			self.width -= diffx
			self.height -= diffy
		elif self.resizing == self.RESIZE_UR:
			if self.height - diffy < 10 or self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0], self.ul[1]+diffy)
			self.lr = (self.lr[0]+diffx, self.lr[1])
			self.pic_location = (self.pic_location[0], self.pic_location[1]+diffy)
			self.width += diffx
			self.height -= diffy
		elif self.resizing == self.RESIZE_LL:
			if self.height + diffy < 10 or self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1])
			self.lr = (self.lr[0], self.lr[1]+diffy)
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1])
			self.width -= diffx
			self.height += diffy
		elif self.resizing == self.RESIZE_LR:
			if self.height + diffy < 10:
				self.motion_coords = tmp
				return True
			if self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0]+diffx, self.lr[1]+diffy)
			self.width += diffx
			self.height += diffy
		if self.orig_pic:
			self.pic = self.orig_pic.scale_simple (int(self.width), int(self.height), gtk.gdk.INTERP_NEAREST)
		self.emit ("update_links")
		self.emit ("update_view")
		return True			
			
	def update_save (self):
		text = self.extended_buffer.get_text ()
		if text:
			self.extended_element.replaceWholeText (text)
		else:
			self.extended_element.replaceWholeText ("LABYRINTH_AUTOGEN_TEXT_REMOVE")
		self.element.setAttribute ("ul-coords", str(self.ul))
		self.element.setAttribute ("lr-coords", str(self.lr))
		self.element.setAttribute ("identity", str(self.identity))
		self.element.setAttribute ("file", str(self.filename))
		self.element.setAttribute ("image_width", str(self.width))
		self.element.setAttribute ("image_height", str(self.height))
		if self.am_selected:
				self.element.setAttribute ("current_root", "true")
		else:
			try:
				self.element.removeAttribute ("current_root")
			except xml.dom.NotFoundErr:
				pass
		if self.am_primary:
			self.element.setAttribute ("primary_root", "true")
		else:
			try:
				self.element.removeAttribute ("primary_root")
			except xml.dom.NotFoundErr:
				pass
		return
		
	def load (self, node):
		tmp = node.getAttribute ("ul-coords")
		self.ul = utils.parse_coords (tmp)
		tmp = node.getAttribute ("lr-coords")
		self.lr = utils.parse_coords (tmp)
		self.filename = node.getAttribute ("file")
		self.identity = int (node.getAttribute ("identity"))
		self.width = float(node.getAttribute ("image_width"))
		self.height = float(node.getAttribute ("image_height"))
		if node.hasAttribute ("current_root"):
			self.am_selected = True
		else:
			self.am_selected = False
		if node.hasAttribute ("primary_root"):
			self.am_primary = True
		else:
			self.am_primary = False
			
		for n in node.childNodes:
			if n.nodeName == "Extended":
				for m in n.childNodes:
					if m.nodeType == m.TEXT_NODE:
						text = m.data
						if text != "LABYRINTH_AUTOGEN_TEXT_REMOVE":
							self.extended_buffer.set_text (text)
			else:
				print "Unknown: "+n.nodeName
		margin = utils.margin_required (utils.STYLE_NORMAL)
		self.pic_location = (self.ul[0]+margin[0], self.ul[1]+margin[1])
		self.okay = self.open_image (self.filename)
		self.lr = (self.pic_location[0]+self.width+margin[2], self.pic_location[1]+self.height+margin[3])
		if not self.okay:
			dialog = gtk.MessageDialog (None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
										gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE,
										_("Error loading file"))
			dialog.format_secondary_text (_("%s could not be found.  Associated thought will be empty."%self.filename))
			dialog.run ()
			dialog.hide ()
			self.pic = None
			self.orig_pic = None
		else:
			self.pic = self.orig_pic.scale_simple (int(self.width), int(self.height), gtk.gdk.INTERP_HYPER)	
		return
	

class ImageThoughtOld (BaseThought.ResizableThought):
	def __init__ (self, filename=None, coords=None, ident=None, element=None, load=None, extended=None):
		super (ImageThought, self).__init__()
		
		self.element = element
		self.filename = filename
		self.extended_element = extended
		
		if not load:
			margin = utils.margin_required (utils.STYLE_NORMAL)
			self.ul = (coords[0]-margin[0], coords[1]-margin[1])
			self.identity = ident
			self.okay = self.load_image (filename)
			if self.okay:
				self.width = self.orig_pic.get_width ()
				self.height = self.orig_pic.get_height ()
				
				self.pic_location = coords
				self.lr = (self.pic_location[0]+self.width+margin[2], self.pic_location[1]+self.height+margin[3])
				self.pic = self.orig_pic
				self.text = filename[filename.rfind('/')+1:filename.rfind('.')]				
				self.emit ("title_changed", self.text, 65)
		else:
			self.load_data (load)
		
	def load_image (self, filename):
		if filename == None:
			print "Error: Filename not given!!!!"
			return False
			
		try:
			self.orig_pic = gtk.gdk.pixbuf_new_from_file (filename)
		except:
			return False
		return True

	def draw (self, context):
		utils.draw_thought_outline (context, self.ul, self.lr, self.am_root, self.am_primary, utils.STYLE_NORMAL)

		if self.pic:
			context.set_source_pixbuf (self.pic, self.pic_location[0], self.pic_location[1])
			context.rectangle (self.pic_location[0], self.pic_location[1], self.width, self.height)
			context.fill ()
		context.set_source_rgb (0,0,0)
		
		return
	
	def export (self, context, move_x, move_y):
		utils.export_thought_outline (context, self.ul, self.lr, self.am_root, self.am_primary, utils.STYLE_NORMAL,
									  (move_x, move_y))

		if self.pic:
			print "Putting Pic"
			context.set_source_pixbuf (self.pic, self.pic_location[0]+move_x, self.pic_location[1]+move_y)
			context.rectangle (self.pic_location[0]+move_x, self.pic_location[1]+move_y, 
							   self.width, self.height)
			context.fill ()
		context.set_source_rgb (0,0,0)
		
		return
		
	def handle_movement (self, coords, move=True, edit_mode = False):
		diffx = coords[0] - self.motion_coords[0]
		diffy = coords[1] - self.motion_coords[1]
		
		tmp = self.motion_coords
		self.motion_coords = coords
		if self.resizing == self.MOTION_NONE:
			# Actually, we have to move the entire thing
			self.ul = (self.ul[0]+diffx, self.ul[1]+diffy)
			self.lr = (self.lr[0]+diffx, self.lr[1]+diffy)
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1]+diffy)
			return True
		elif self.resizing == self.MOTION_LEFT:
			if self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1])
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1])
			self.width -= diffx
		elif self.resizing == self.MOTION_RIGHT:
			if self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0]+diffx, self.lr[1])
			self.width += diffx
		elif self.resizing == self.MOTION_TOP:
			if self.height - diffy < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0], self.ul[1]+diffy)
			self.pic_location = (self.pic_location[0], self.pic_location[1]+diffy)
			self.height -= diffy
		elif self.resizing == self.MOTION_BOTTOM:
			if self.height + diffy < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0], self.lr[1]+diffy)
			self.height += diffy
		elif self.resizing == self.MOTION_UL:
			if self.height - diffy < 10 or self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1]+diffy)
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1]+diffy)
			self.width -= diffx
			self.height -= diffy
		elif self.resizing == self.MOTION_UR:
			if self.height - diffy < 10 or self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0], self.ul[1]+diffy)
			self.lr = (self.lr[0]+diffx, self.lr[1])
			self.pic_location = (self.pic_location[1], self.pic_location[1]+diffy)
			self.width += diffx
			self.height -= diffy
		elif self.resizing == self.MOTION_LL:
			if self.height + diffy < 10 or self.width - diffx < 10:
				self.motion_coords = tmp
				return True
			self.ul = (self.ul[0]+diffx, self.ul[1])
			self.lr = (self.lr[0], self.lr[1]+diffy)
			self.pic_location = (self.pic_location[0]+diffx, self.pic_location[1])
			self.width -= diffx
			self.height += diffy
		elif self.resizing == self.MOTION_LR:
			if self.height + diffy < 10:
				self.motion_coords = tmp
				return True
			if self.width + diffx < 10:
				self.motion_coords = tmp
				return True
			self.lr = (self.lr[0]+diffx, self.lr[1]+diffy)
			self.width += diffx
			self.height += diffy
		if self.orig_pic:
			self.pic = self.orig_pic.scale_simple (int(self.width), int(self.height), gtk.gdk.INTERP_NEAREST)
		
		return True
			
	def finish_motion (self):
		# Up till now, we've been using the fastest interp.  Here, its made best
		# Yes, it makes quite a big difference actually
		if self.orig_pic:
			self.pic = self.orig_pic.scale_simple (int (self.width), int (self.height), gtk.gdk.INTERP_HYPER)
		self.emit ("change_cursor", gtk.gdk.LEFT_PTR, None)
		self.resizing = self.MOTION_NONE
		return	
	
	def handle_key (self, string, keysym, modifiers):
		# Since we can't handle text in an image node, we ignore it.
		return False
		
	def find_connection (self, other, export=False):
		if not export and self.editing or other.editing:
			return (None, None)
		elif export:
			self.update_bbox ()
			other.update_bbox ()
		xfrom = self.ul[0]-((self.ul[0]-self.lr[0]) / 2.)
		yfrom = self.ul[1]-((self.ul[1]-self.lr[1]) / 2.)
		xto = other.ul[0]-((other.ul[0]-other.lr[0]) / 2.)
		yto = other.ul[1]-((other.ul[1]-other.lr[1]) / 2.)

		return ((xfrom, yfrom), (xto, yto))
		
	def begin_editing (self, im_context = None):
		return
	
	def finish_editing (self):
		return
	
	def become_active_root (self):
		self.am_root = True
		return
		
	def finish_active_root (self):
		self.am_root = False
		return
		
	def become_primary_thought (self):
		self.am_primary = True
		return

	# These haven't been done yet...
	def update_save (self):
		text = self.extended_buffer.get_text ()
		if text:
			self.extended_element.replaceWholeText (text)
		else:
			self.extended_element.replaceWholeText ("LABYRINTH_AUTOGEN_TEXT_REMOVE")
		self.element.setAttribute ("ul-coords", str(self.ul))
		self.element.setAttribute ("lr-coords", str(self.lr))
		self.element.setAttribute ("identity", str(self.identity))
		self.element.setAttribute ("file", str(self.filename))
		self.element.setAttribute ("image_width", str(self.width))
		self.element.setAttribute ("image_height", str(self.height))
		if self.am_root:
				self.element.setAttribute ("current_root", "true")
		else:
			try:
				self.element.removeAttribute ("current_root")
			except xml.dom.NotFoundErr:
				pass
		if self.am_primary:
			self.element.setAttribute ("primary_root", "true")
		else:
			try:
				self.element.removeAttribute ("primary_root")
			except xml.dom.NotFoundErr:
				pass
		return
		
	def load_data (self, node):
		tmp = node.getAttribute ("ul-coords")
		self.ul = utils.parse_coords (tmp)
		tmp = node.getAttribute ("lr-coords")
		self.lr = utils.parse_coords (tmp)
		self.filename = node.getAttribute ("file")
		self.identity = int (node.getAttribute ("identity"))
		self.width = float(node.getAttribute ("image_width"))
		self.height = float(node.getAttribute ("image_height"))
		if node.hasAttribute ("current_root"):
			self.am_root = True
		else:
			self.am_root = False
		if node.hasAttribute ("primary_root"):
			self.am_primary = True
		else:
			self.am_primary = False
			
		for n in node.childNodes:
			if n.nodeName == "Extended":
				for m in n.childNodes:
					if m.nodeType == m.TEXT_NODE:
						text = m.data
						if text != "LABYRINTH_AUTOGEN_TEXT_REMOVE":
							self.extended_buffer.set_text (text)
			else:
				print "Unknown: "+n.nodeName
		self.okay = self.load_image (self.filename)
		margin = utils.margin_required (utils.STYLE_NORMAL)
		self.pic_location = (self.ul[0]+margin[0], self.ul[1]+margin[1])
		self.lr = (self.pic_location[0]+self.width+margin[2], self.pic_location[1]+self.height+margin[3])
		if not self.okay:
			dialog = gtk.MessageDialog (None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
										gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE,
										_("Error loading file"))
			dialog.format_secondary_text (_("%s could not be found.  Associated thought will be empty."%self.filename))
			dialog.run ()
			dialog.hide ()
			self.pic = None
			self.orig_pic = None
		else:
			self.pic = self.orig_pic.scale_simple (int(self.width), int(self.height), gtk.gdk.INTERP_HYPER)	
		return
		
	def get_max_area (self):
		return (self.ul[0],self.ul[1],self.lr[0],self.lr[1])	
	
