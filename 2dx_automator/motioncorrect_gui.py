#!/usr/bin/python

from Tkinter import *
import tkFileDialog
import tkMessageBox

from pylab import plt, plot, subplot, figure, hist

import thread

from PIL import Image, ImageDraw, ImageTk

from EMAN2  import *
from sparx  import *

from MotionCorrectionWatcher import *

import os
import datetime


n = 508
n_small = 400

import tkSimpleDialog
		

def bind(widget, event):
	def decorator(func):
		widget.bind(event, func)
		return func
	return decorator
	
	
class Auto2dxGUI(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent, background="white")
		self.parent = parent
		self.index_selected = 0
		self.initUI()	
		self.resetResultOverview()
		self.listbox.selection_clear(0, END)
		self.listbox.selection_set(END)
		self.listbox.activate(END)
		self.index_selected = self.count-1
		self.indexChanged()
		
		
	def getFolders(self):
		self.input_dir = tkFileDialog.askdirectory(parent=self.parent, title="Please select an input directory for Motion Correction")
		if len(self.input_dir)==0:
			raise SystemExit("No input directory selected")
		
		self.output_dir = tkFileDialog.askdirectory(parent=self.parent, title="Please select an output directory for Motion Correction")
		if len(self.output_dir)==0:
			raise SystemExit("No output directory selected")
			
			
	def initLayout(self):
		
		self.pack(fill=BOTH, expand=1)
		self.topframe = Frame(self, relief=RAISED, borderwidth=1)
		self.topframe.pack(fill=BOTH)
		
		self.topleftframe = Frame(self.topframe)
		self.topleftframe.pack(side=LEFT)
		
		self.toprightframe = Frame(self.topframe)
		self.toprightframe.pack(side=RIGHT)
		
		self.centralframe = Frame(self)
		self.centralframe.pack(expand=1, fill=BOTH)
		
		self.centralleftframe = Frame(self.centralframe)
		self.centralleftframe.pack(side=LEFT)
		
		self.lowleftframe = Frame(self.centralleftframe)
		self.lowleftframe.pack(side=BOTTOM)
		
		self.centralrightframe = Frame(self.centralframe, relief=RAISED, borderwidth=2)
		self.centralrightframe.pack(pady=5)
		
		self.centralrightframe3 = Frame(self.centralrightframe)
		self.centralrightframe3.pack(side=LEFT)
		
		self.centralrightframe1 = Frame(self.centralrightframe)
		self.centralrightframe1.pack()
		
		self.centralrightframe2 = Frame(self.centralrightframe)
		self.centralrightframe2.pack()
		
		
	
	def getInfoString(self, folder):
		result = "Image Statistics:\n\n\n"
		result += "Input image: " + self.image_names[self.index_selected] + "\n\n\n"
		file_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.input_dir + "/" + self.image_names[self.index_selected])) 
		result += "Time: " + str(file_time) + "\n\n"
		
		return result
		
	
	def resetResultOverview(self):
		self.listbox.delete(0, END)
		self.image_names = []
		if os.path.exists(self.output_dir + "/automatic_import_log.txt"):
			f = open( self.output_dir + "/automatic_import_log.txt", 'r')
			for line in f:
				self.listbox.insert(END, line.split()[0])
				self.image_names.append(line.split()[0])
		
		self.image_count_label.configure(text=str(len(self.image_names)) + " Images")
		
		self.listbox.selection_clear(0, END)
		self.listbox.selection_set(self.index_selected)
		self.listbox.activate(self.index_selected)
		self.indexChanged()

		
	def runAutomation(self):
		if not self.is_running:
			if tkMessageBox.askyesno("Automation Launch", "Relaunching may take a while as all new images are processed!\n\nDo you want to continue?"):
				self.status.configure(text="Automation starting up...", fg="orange")
				self.parent.update()
				time.sleep(2)
				if self.watcher.restart():
					self.resetResultOverview()
				self.status.configure(text="Automation running", fg="green")
				self.is_running = True
				
		
	def indexChanged(self):
		
		if len(self.image_names) == 0:
			return
		
		all_fine = True
		
		corename = self.watcher.getFileCoreName(self.image_names[self.index_selected])
		raw_fft_name = self.input_dir + "/dosef_quick/" + corename + "_ready_RawFFT.gif"
		corr_fft_name = self.input_dir + "/dosef_quick/" + corename + "_ready_CorrFFT.gif"
		corr_img_name = self.input_dir + "/dosef_quick/" + corename + "_ready_CorrSum.gif"
		rot_name = self.input_dir + "/dosef_quick/" + corename + "_rotpower.tif"
		plot_name = self.input_dir + "/dosef_quick/" + corename + ".tif"
		
		if os.path.exists(raw_fft_name):
			try:
				self.fft_in_image = ImageTk.PhotoImage(Image.open(raw_fft_name).resize((n,n),Image.ANTIALIAS))
				self.fft_in_label.configure(image=self.fft_in_image)
			except:
				print "image not found"
		else:
			self.fft_in_label.configure(image=self.default_tkimage)
			all_fine = False
		
		if os.path.exists(corr_fft_name):
			try:
				self.fft_out_image = ImageTk.PhotoImage(Image.open(corr_fft_name).resize((n,n),Image.ANTIALIAS))
				self.fft_out_label.configure(image=self.fft_out_image)
			except:
				print "image not found"
		else:
			self.fft_out_label.configure(image=self.default_tkimage)
			all_fine = False
	
		if os.path.exists(corr_img_name):
			try:
				self.corr_image = ImageTk.PhotoImage(Image.open(corr_img_name).resize((n,n),Image.ANTIALIAS))
				self.image_label.configure(image=self.corr_image)
			except:
				print "image not found"
		else:
			self.image_label.configure(image=self.default_tkimage)
			all_fine = False
			
		nx = int(800 * 0.635)
		ny = int(600 * 0.635)	
			
		if os.path.exists(rot_name):
			try:
				self.power_image = ImageTk.PhotoImage(Image.open(rot_name).resize((nx,ny),Image.ANTIALIAS))
				self.rotpower_label.configure(image=self.power_image)
			except:
				print "image not found"
		else:
			self.rotpower_label.configure(image=self.default_tkimage)
			all_fine = False
			
		nx = int(800 * 0.55)
		ny = int(600 * 0.55)	
		
		if os.path.exists(plot_name):
			try:
				self.plot_image = ImageTk.PhotoImage(Image.open(plot_name).resize((nx,ny),Image.ANTIALIAS))
				self.drift_label.configure(image=self.plot_image)
			except:
				print "image not found"
		else:
			self.drift_label.configure(image=self.default_tkimage_small)
			all_fine = False


		if all_fine:
			info = self.getInfoString(self.image_names[self.index_selected])
		else:
			info = "Image Statistics:\n\n\n"
			info += "Input image: " + self.image_names[self.index_selected] + "\n\n\n"
			info += "processing..."
		self.info_label.configure(text=info)

	
	def check_for_new_images(self):
		if os.path.exists(self.output_dir + "/automatic_import_log.txt"):
			f = open( self.output_dir + "/automatic_import_log.txt", 'r')
			num = len(f.readlines())
			if num>self.count:
				self.count = num
				self.resetResultOverview()
		
		
	def autom_do_check(self):
		if self.is_running:
			if self.watcher.test4new():
				self.resetResultOverview()
		self.after(2000, self.autom_do_check)
		
		
	def switchAutomationOff(self):
		if tkMessageBox.askyesno("Stop Automation", "Do you realy want to stop the automation?"):
			self.is_running = False
			self.status.configure(text="Automation not running", fg="red")
	
	
	def reprocessOneImage(self, corename):
		raw_fft_name = self.input_dir + "/dosef_quick/" + corename + "_ready_RawFFT.gif"
		corr_fft_name = self.input_dir + "/dosef_quick/" + corename + "_ready_CorrFFT.gif"
		corr_img_name = self.input_dir + "/dosef_quick/" + corename + "_ready_CorrSum.gif"
		rot_name = self.input_dir + "/dosef_quick/" + corename + "_rotpower.tif"
		plot_name = self.input_dir + "/dosef_quick/" + corename + ".tif"
		
		if os.path.exists(raw_fft_name):
			os.remove(raw_fft_name)
		
		if os.path.exists(corr_fft_name):
			os.remove(corr_fft_name)
		
		if os.path.exists(corr_img_name):
			os.remove(corr_img_name)
		
		if os.path.exists(rot_name):
			os.remove(rot_name)
		
		if os.path.exists(plot_name):
			os.remove(plot_name)
		
		filename = corename + ".mrc"
		thread.start_new_thread(self.watcher.image_added, (filename, False,))
	
	
	def reprocessALLImage(self):
		if tkMessageBox.askyesno("Reprocess all images", "Continue?"):
			for f in self.image_names:
				corename = self.watcher.getFileCoreName(f)
				self.reprocessOneImage(corename)
			
			
	def reprocessImage(self):
		corename = self.watcher.getFileCoreName(self.image_names[self.index_selected])
		self.reprocessOneImage(corename)
		
		
	def openImageEman(self):
		i = self.index_selected
		image_name = self.watcher.getFileCoreName(self.image_names[i])
		image_to_show = self.output_dir + "/" + image_name + "_aligned.mrc"
		print image_to_show
		
		if os.path.exists(image_to_show):
			eman_command = "e2display.py " + image_to_show
			os.system(eman_command)
		
	def minFrameChanged(self):
		number = tkSimpleDialog.askinteger("Edit Motion Correct Properties", "First Frame")
		if number>=0:
			self.minframe = number
			self.minframe_label.configure(text="Starting Frame Number: " + str(self.minframe))
			self.watcher.setFirstFrame(self.minframe)
		
	def maxFrameChanged(self):
		number = tkSimpleDialog.askinteger("Edit Motion Correct Properties", "Last Frame")
		if number>=0:
			self.maxframe = number
			self.maxframe_label.configure(text="Ending Frame Number: " + str(self.maxframe))
			self.watcher.setLastFrame(self.maxframe)
			
	def changeExportLocation(self):
		self.export_location = tkFileDialog.askdirectory(parent=self.parent, title="Select export directory")
		if len(self.export_location) == 0:
			self.export_location = "not set"
		self.export_location_label.configure(text="Export Location:\n" + self.export_location)
		
	def exportImage(self):
		i = self.index_selected
		image_name = self.watcher.getFileCoreName(self.image_names[i])
		image_to_show = self.output_dir + "/" + image_name + "_aligned.mrc"
		image_name = image_to_show.split("/")[-1]
		shutil.copy(image_to_show, self.export_location + "/" + image_name)
		
	def troubleshootGUI(self):
		if tkMessageBox.askyesno("Troubleshooting", "Do you realy want to remove all locks?"):
			print "Troubleshooting..."
			try:
				self.watcher.lock_compute.release()
			except:
				print "releasing the locks did not help"
	
	def initUI(self):
		self.parent.title("Motion Correction GUI (beta)")
	
		self.getFolders()
		
		#self.input_dir = '/mnt/afd867f9-f76e-40f3-9b3a-12c42385bba8/scherers/mlok_k2/mc_in'
		#self.output_dir = '/mnt/afd867f9-f76e-40f3-9b3a-12c42385bba8/scherers/mlok_k2/mc_out'
		
		in_folder = self.input_dir
		out_folder = self.output_dir
		logfile = out_folder + "/automatic_import_log.txt"
		wait = 1
		refresh = 10
	#	self.watcher = Add2dxImageWatcher(refresh, wait, in_folder, out_folder, logfile)

		self.initLayout()
		
		self.is_running = False
		
		Label(self.topleftframe, text="Input: " + self.input_dir).pack()
		Label(self.topleftframe, text="Output: " + self.output_dir).pack()
		
		run_button = Button(self.toprightframe ,text='Launch Automation', command=self.runAutomation, width=30)
		run_button.pack(padx=5, pady=2)
		
		stop_button = Button(self.toprightframe ,text='Stop Automation', command=self.switchAutomationOff, width=30)
		stop_button.pack(padx=5, pady=2)
		
		self.minframe = 0
		self.maxframe = 0
		
		self.minframe_label = Label(self.centralleftframe, text="Starting Frame Number: " + str(self.minframe))
		self.minframe_label.pack(padx=5, pady=5)
		
		change_min_frame_button = Button(self.centralleftframe ,text='Change min frame', width=20, command=self.minFrameChanged)
		change_min_frame_button.pack()
		
		Label(self.centralleftframe, text=" ", height=1).pack()
		
		self.maxframe_label = Label(self.centralleftframe, text="Ending Frame Number: " + str(self.maxframe))
		self.maxframe_label.pack(padx=5, pady=5)
		
		change_max_frame_button = Button(self.centralleftframe ,text='Change max frame', width=20, command=self.maxFrameChanged)
		change_max_frame_button.pack()
		
		Label(self.centralleftframe, text=" ", height=1).pack()
		
		## Export
		self.export_location = "not set"
		self.exportframe = Frame(self.centralleftframe, relief=RAISED, borderwidth=2)
		self.exportframe.pack(pady=5)
		self.export_location_label = Label(self.exportframe, text="Export Location:\n" + self.export_location, width=45)
		self.export_location_label.pack(pady=5)
		self.change_export_location_button = Button(self.exportframe ,text='Change Export Location', width=20, command=self.changeExportLocation)
		self.change_export_location_button.pack()
		self.export_button = Button(self.exportframe ,text='Export Image', width=20, command=self.exportImage)
		self.export_button.pack(pady=5)
		
		self.troubles_button = Button(self.centralleftframe ,text='Troubleshoot ', width=20, command=self.troubleshootGUI)
		self.troubles_button.pack(padx=20, pady=8)
		
		Label(self.centralleftframe, text=" ", height=1).pack()
		
		self.image_count_label = Label(self.centralleftframe, text="Images")
		self.image_count_label.pack()
		
		self.scrollbar = Scrollbar(self.centralleftframe)
		self.scrollbar.pack(side=RIGHT, fill=Y)

		self.listbox = Listbox(self.centralleftframe, width=45)
		self.listbox.pack(padx=14)

		# attach listbox to scrollbar
		self.listbox.config(yscrollcommand=self.scrollbar.set, height=30)
		self.scrollbar.config(command=self.listbox.yview)
		
		@bind(self.listbox, '<<ListboxSelect>>')
		def onselect(evt):
			w = evt.widget
			index = int(w.curselection()[0])
			value = w.get(index)
			print 'You selected item %d: "%s"' % (index, value)
			self.index_selected = index
			self.indexChanged()
			
		Label(self.centralleftframe, text=" ", height=2).pack()
		
		self.reprocess_button = Button(self.lowleftframe ,text='Reprocess Image', width=40, command=self.reprocessImage)
		self.reprocess_button.pack(padx=20, pady=5)
		
		self.reprocess_ALL_button = Button(self.lowleftframe ,text='Reprocess ALL Image', width=40, command=self.reprocessALLImage)
		self.reprocess_ALL_button.pack(padx=20, pady=5)
		
		Label(self.centralleftframe, text=" ", height=2).pack()
		
		self.open_button = Button(self.lowleftframe ,text='Open Image', width=40, command=self.openImageEman)
		self.open_button.pack(padx=20, pady=5)
	
		in_folder = self.input_dir
		out_folder = self.output_dir
		logfile = out_folder + "/automatic_import_log.txt"
		wait = 1
		refresh = 1
		self.watcher = MotionCorrectionWatcher(refresh, wait, in_folder, out_folder, logfile, first_frame=0, last_frame=0)
	
		self.default_image = Image.new("RGB", (n,n), "white")
		self.default_tkimage = ImageTk.PhotoImage(self.default_image)
		
		self.fft_out_label = Label(self.centralrightframe1, image=self.default_tkimage)
		self.fft_out_label.pack(side=RIGHT, pady=5, padx=5)
		
		self.fft_in_label = Label(self.centralrightframe1, image=self.default_tkimage)
		self.fft_in_label.pack(side=LEFT, pady=5, padx=5)
		
		self.rotpower_label = Label(self.centralrightframe2, image=self.default_tkimage)
		self.rotpower_label.pack(side=RIGHT, padx=5, pady=5)
		
		self.image_label = Label(self.centralrightframe2, image=self.default_tkimage)
		self.image_label.pack(side=LEFT, padx=5, pady=5)
		
		
		self.info_label = Label(self.centralrightframe3, text="Image Staticstics:\n", height=28, width=50)
		self.info_label.pack()
		
		self.default_image_small = Image.new("RGB", (n_small,n_small), "white")
		self.default_tkimage_small = ImageTk.PhotoImage(self.default_image_small)
		self.drift_label = Label(self.centralrightframe3, image=self.default_tkimage_small)
		self.drift_label.pack(side=BOTTOM, padx=5, pady=5)
		
		self.status = Label(self.parent, text="Automation not running", bd=1, relief=SUNKEN, anchor=W, fg="red")
		self.status.pack(side=BOTTOM, fill=X)
		
		self.count = 0
		self.check_for_new_images()
		self.autom_do_check()
		
		
		
def main():
	root = Tk()
	root.geometry("1920x1200+000+000")
	#root.geometry("800x600+300+300")
	app = Auto2dxGUI(root)
	root.mainloop()
	
if __name__ == '__main__':
	main() 
