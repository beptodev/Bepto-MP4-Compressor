import re, psutil, subprocess, os
from urllib.request import Request, urlopen
from tkinter import *
from tkinter import filedialog
from functools import partial
from pathlib import Path

class App:
	def __init__(self, root):
		# Version fetching
		self.author = 'TERROR'
		self.fetch_url = 'https://bep.to/downloads/tvc_version.txt'
		self.cur_version = 'v.2.1.0'
		self.latest_version = self.fetch_version()

		# Bools
		self.is_compressing = False
		self.aborted = False

		# File and directories
		self.queue = 0
		self.files = []
		self.file_names = []
		self.file_extensions = []
		self.app_dir = os.getcwd()

		# Compression default properties
		self.w = '1280'
		self.h = '720'
		self.fps = '30'
		self.size = '8'

		# Compression desired properties
		self.desired_w = '1280'
		self.desired_h = '720'
		self.desired_fps = '30'
		self.desired_size = 8

		# Info frame
		self.info_frame = Frame(root, width = 400, height = 75)
		self.info_frame.pack()
		self.info_frame.pack_propagate(0)

		self.info_title = Label(self.info_frame, text = f'{self.author} Video Compressor {self.version}', font = 'Arial 12 bold')
		self.info_title.pack()

		self.author_label = Label(self.info_frame, text = f'Created by {self.author}\nCheck for updates @ github.com/terrorhub', font = 'Arial 8')
		self.author_label.pack()

		# Options
		self.options_frame = LabelFrame(root, width = 380)
		self.options_frame.pack()
		self.options_frame.pack_propagate(0)

		# Resolution
		self.res_label = Label(self.options_frame, text = 'Resolution (Width x Height)', width = 30)
		self.res_label.grid(row = 0, column = 0)

		self.e_res_w = Entry(self.options_frame, width = 7, justify = 'center')
		self.e_res_w.insert(0, self.w)
		self.e_res_w.grid(row = 0, column = 1)

		self.res_w_hint_label = Label(self.options_frame, text = 'W', width = 4, justify = 'left')
		self.res_w_hint_label.grid(row = 0, column = 2)

		self.e_res_h = Entry(self.options_frame, width = 7, justify = 'center')
		self.e_res_h.insert(0, self.h)
		self.e_res_h.grid(row = 0, column = 3)

		self.res_h_hint_label = Label(self.options_frame, text = 'H', width = 4, justify = 'left')
		self.res_h_hint_label.grid(row = 0, column = 4)

		# Size
		self.size_label = Label(self.options_frame, text = 'Target File Size (ex. 8MB)', width = 28)
		self.size_label.grid(row = 1, column = 0)

		self.e_size = Entry(self.options_frame, width = 7, justify = 'center')
		self.e_size.insert(0, self.size)
		self.e_size.grid(row = 1, column = 1)

		self.size_hint_label = Label(self.options_frame, text = 'MB', width = 4, justify = 'left')
		self.size_hint_label.grid(row = 1, column = 2)

		# FPS
		self.fps_label = Label(self.options_frame, text = 'Framerate (ex. 30FPS)', width = 28)
		self.fps_label.grid(row = 2, column = 0)

		self.e_fps = Entry(self.options_frame, width = 7, justify = 'center')
		self.e_fps.insert(0, self.fps)
		self.e_fps.grid(row = 2, column = 1)

		self.fps_hint_label = Label(self.options_frame, text = 'FPS', width = 4, justify = 'left')
		self.fps_hint_label.grid(row = 2, column = 2)

		# Mute Audio
		self.mute_label = Label(self.options_frame, text = 'Mute Audio', width = 28)
		self.mute_label.grid(row = 3, column = 0)

		self.mute_var = IntVar()

		self.c_mute = Checkbutton(self.options_frame, variable = self.mute_var)
		self.c_mute.grid(row = 3, column = 1)

		# Video Codec
		self.codec_label = Label(self.options_frame, text = 'Use h.265 (Higher quality)', width = 28)
		self.codec_label.grid(row = 4, column = 0)

		self.h265_var = IntVar()

		self.c_h265 = Checkbutton(self.options_frame, variable = self.h265_var)
		self.c_h265.grid(row = 4, column = 1)

		# Spacer
		self.spacer = Label(root, text = '' )
		self.spacer.pack()

		# Browse
		self.browse_frame = Frame(root, width = 380, height = 150)
		self.browse_frame.pack()
		self.browse_frame.pack_propagate(0)

		# Spacer
		self.spacer_2 = Label(root, text = '' )
		self.spacer_2.pack()

		# Output
		self.output_frame = LabelFrame(root, width = 380, height = 230)
		self.output_frame.pack()
		self.output_frame.pack_propagate(0)

		self.output_field = Label(self.output_frame, text = 'Waiting to compress...', wraplength = 370, justify = 'center')
		self.output_field.pack()

		# Browse Buttons
		self.browse_button = Button(self.browse_frame, text = 'Browse', width = 15, command = self.file_select)
		self.browse_button.grid(row = 0, column = 0, padx = 5)

		self.abort_button = Button(self.browse_frame, text = 'Abort', width = 15, command = self.abort)
		self.abort_button.grid(row = 0, column = 2, padx = 5)

		self.compress_button = Button(self.browse_frame, text = 'Compress', width = 15, command = self.compress)
		self.compress_button.grid(row=0, column=1, padx=5)

	def fetch_version(self):
		msg = ''

		try:
			req = Request(self.fetch_url, headers = {'User-Agent': 'Mozilla/5.0'})
			msg = str(urlopen(req).read())
			msg = re.sub("['b]", '', msg)
			self.latest_version = msg

			if self.cur_version != self.latest_version:
				self.version = f'{self.cur_version} (Outdated)'
			else:
				self.version = f'{self.cur_version} (Latest)'

			print('Successfully fetched version.')
		except:
			print('Error fetching version!')

		return msg
	
	def abort(self):
		for proc in psutil.process_iter():
			if proc.name() == 'ffmpeg.exe':
				p = psutil.Process(proc.pid)
				p.kill()

				self.is_compressing = False
				self.aborted = True

				print('Killing ffmpeg process!')
	
	def close(self):
		self.abort()
		print('Exiting.')
		root.destroy()
	
	def file_select(self):
		f = filedialog.askopenfilenames()
		self.files = f
		self.file_names.clear()
		self.file_extensions.clear()

		for file in self.files:
			split_slash = file.split('/')
			split_extension = os.path.splitext(split_slash[-1])
			self.file_names.append(split_extension[0])
			self.file_extensions.append(split_extension[1])
			print(split_extension[0], split_extension[1])

		self.output_field.configure(text = f'Selected files:\n{self.files}')
		print(f'Selected files: {self.files}')
		root.update()
	
	def update_output(self, proc):
		line = proc.stdout.readline()
		# print(line)

		if self.aborted:
			self.output_field.configure(text = 'Aborted!')
		elif proc.poll() or line == '':
			self.output_field.configure(text = f'Completed!\nVideos outputted to {self.app_dir}')
			self.is_compressing = False
		else:
			self.output_field.configure(text = f'Compressing video {self.queue + 1}/{len(self.files)} to {self.desired_w} x {self.desired_h} {self.desired_fps}fps @ {self.desired_size}MB\n\n' + str(line), wraplength=370)
			root.update()
			root.after(1, self.update_output(proc))
	
	def compress(self):
		if self.files == '':
			print('No files selected!')
			return
		
		if self.is_compressing:
			print('Compression in progress!')
			return
		
		self.is_compressing = True
		self.aborted = False

		self.desired_w = self.e_res_w.get()
		self.desired_h = self.e_res_h.get()
		self.desired_fps = self.e_fps.get()
		self.desired_size = int(self.e_size.get())

		for file in self.files:
			origin_duration_s = subprocess.Popen(f'ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file}"', stdout = subprocess.PIPE, shell = True)
			origin_duration_s = float(origin_duration_s.stdout.readline())

			print('Video duration: ' + str(origin_duration_s))

			origin_audio_bitrate_kbit_s = subprocess.Popen(f'ffprobe.exe -v 0 -select_streams a:0 -show_entries stream=bit_rate -of compact=p=0:nk=1 "{file}"', stdout = subprocess.PIPE, shell = True)

			try:
				target_audio_bitrate_kbit_s = float(origin_audio_bitrate_kbit_s.stdout.readline()) / 1000
				print('Audio bitrate: ' + str(target_audio_bitrate_kbit_s))
			except:
				target_audio_bitrate_kbit_s = 1
				print('Audio bitrate: No audio detected')

			print(f'New file size: {self.desired_size}MB')

			quick_mafs = ((self.desired_size * 8192.0) / (1.048576 * origin_duration_s) - target_audio_bitrate_kbit_s)
			print('New video bitrate: ' + str(quick_mafs))

			print(f'New video resolution: {self.desired_w}:{self.desired_h} @ {self.desired_fps}fps')

			desired_audio = f'-c:a aac -b:a {target_audio_bitrate_kbit_s}k'

			if self.mute_var.get() == 1:
				desired_audio = '-an'
				print('Audio muted')
			
			desired_codec = '-c:v libx264'

			if self.h265_var.get() == 1:
				desired_codec = '-c:v libx265'
				print('Using h.265 video codec')

			cmd = f'ffmpeg.exe -y -i "{file}" {desired_codec} -b:v {quick_mafs}k -r {self.desired_fps} -vf scale={self.desired_w}:{self.desired_h} -pass 1 -an -f mp4 DELETE_AFTER_COMPRESSION && ffmpeg.exe -y -i "{file}" {desired_codec} -b:v {quick_mafs}k -r {self.desired_fps} -vf scale={self.desired_w}:{self.desired_h} -pass 2 {desired_audio} "{self.file_names[self.queue]}-Compressed{self.file_extensions[self.queue]}"'
			proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True, shell = True)
			
			self.update_output(proc)

			self.queue += 1

		self.queue = 0

root = Tk()
app = App(root)
root.protocol('WM_DELETE_WINDOW', app.close)
root.wm_geometry('400x500')
root.title('TERROR Video Compressor')
root.iconbitmap('icon.ico')
root.resizable(0, 0)
root.mainloop()