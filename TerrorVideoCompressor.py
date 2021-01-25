import re, psutil, subprocess, os, sys, platform
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
		self.cur_version = 'v.2.3.0'
		self.latest_version = self.fetch_version()
		self.os = platform.system()

		# Bools
		self.found_ffmpeg = False
		self.is_compressing = False
		self.aborted = False

		# File and directories
		self.files = []
		self.file_names = []
		self.file_extensions = []
		self.cur_queue = 0
		self.cur_pass = 0
		self.cur_video_length = 0.0
		self.cur_video_progress_s = 0.0
		self.cur_video_progress_percent = 0
		self.app_dir = os.getcwd()

		# Compression default properties
		self.w = '1920'
		self.h = '1080'
		self.fps = '30'
		self.size = '7'
		self.extension = 'mp4'

		# Compression desired properties
		self.desired_w = '1920'
		self.desired_h = '1080'
		self.desired_fps = '30'
		self.desired_size = 7
		self.desired_extension = ''

		# Compression output
		self.proc = None

		# Info frame
		self.info_frame = Frame(root, width = 400, height = 75)
		self.info_frame.pack()
		self.info_frame.pack_propagate(0)

		self.info_title = Label(self.info_frame, text = f'{self.author} Video Compressor {self.version}', font = 'Arial 12 bold')
		self.info_title.pack()

		self.author_label = Label(self.info_frame, text = f'Created by {self.author}\nCheck for updates @ github.com/terrorhub', font = 'Arial 8')
		self.author_label.pack()

		self.ffmpeg_label = Label(self.info_frame, text = self.fetch_ffmpeg(), font = 'Arial 8')
		self.ffmpeg_label.pack()

		# Options
		self.options_frame = Frame(root, width = 380)
		self.options_frame.pack()
		self.options_frame.pack_propagate(0)

		# Resolution
		self.res_label = Label(self.options_frame, text = 'Resolution (Width x Height)', width = 25)
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

		# Extension
		self.extension_label = Label(self.options_frame, text = 'File Extension (Original = Blank)', width = 28)
		self.extension_label.grid(row = 3, column = 0)

		self.e_extension = Entry(self.options_frame, width = 7, justify = 'center')
		self.e_extension.insert(0, self.extension)
		self.e_extension.grid(row = 3, column = 1)

		self.extension_hint_label = Label(self.options_frame, text = '', width = 4, justify = 'left')
		self.extension_hint_label.grid(row = 3, column = 2)

		# Mute Audio
		self.mute_label = Label(self.options_frame, text = 'Mute Audio', width = 28)
		self.mute_label.grid(row = 4, column = 0)

		self.mute_var = IntVar()

		self.c_mute = Checkbutton(self.options_frame, variable = self.mute_var)
		self.c_mute.grid(row = 4, column = 1)

		# Video Codec
		self.codec_label = Label(self.options_frame, text = 'Use h.265 (Higher quality)', width = 28)
		self.codec_label.grid(row = 5, column = 0)

		self.h265_var = IntVar()

		self.c_h265 = Checkbutton(self.options_frame, variable = self.h265_var)
		self.c_h265.grid(row = 5, column = 1)

		# Portrait Mode
		self.portrait_label = Label(self.options_frame, text = 'Portrait Mode (Flip W and H)', width = 28)
		self.portrait_label.grid(row = 6, column = 0)

		self.portrait_var = IntVar()

		self.c_portrait = Checkbutton(self.options_frame, variable = self.portrait_var)
		self.c_portrait.grid(row = 6, column = 1)

		# Spacer
		self.spacer = Label(root, text = '' )
		self.spacer.pack()

		# Button Frame
		self.button_frame = Frame(root, width = 380, height = 150)
		self.button_frame.pack()
		self.button_frame.pack_propagate(0)

		# Spacer
		self.spacer_2 = Label(root, text = '' )
		self.spacer_2.pack()

		# Output
		self.output_frame = LabelFrame(root, width = 380, height = 190)
		self.output_frame.pack()
		self.output_frame.pack_propagate(0)

		output = 'Browse and select your videos to begin!' if self.found_ffmpeg else 'Missing ffmpeg and ffprobe, this app will not work without them!\n\nWindows Users:\nYou need ffmpeg.exe and ffprobe.exe in the same directory as this app, download it from ffmpeg.org.\n\nLinux Users:\nInstall ffmpeg with your package manager.'

		self.output_field = Label(self.output_frame, text = output, wraplength = 370, justify = 'center')
		self.output_field.pack()

		# Buttons
		self.browse_button = Button(self.button_frame, text = 'Browse', width = 12, command = self.file_select)
		self.browse_button.grid(row = 0, column = 0, padx = 5)

		self.abort_button = Button(self.button_frame, text = 'Abort', width = 12, command = self.abort)
		self.abort_button.grid(row = 0, column = 2, padx = 5)

		self.compress_button = Button(self.button_frame, text = 'Compress', width = 12, command = self.compress)
		self.compress_button.grid(row = 0, column = 1, padx = 5)

		# Create output folder
		if not os.path.exists(os.getcwd() + '/Output'):
			os.mkdir(os.getcwd() + '/Output')
			print('TVC: Created output directory.')


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

			print('TVC: Fetched version.')
		except:
			print('TVC: Error fetching version!')

		return msg

	def fetch_ffmpeg(self):
		msg = ''

		if self.os == 'Windows':
			if os.path.exists('ffmpeg.exe') and os.path.exists('ffprobe.exe'):
				self.found_ffmpeg = True
				msg = 'Ready!'
			else:
				self.found_ffmpeg = False
				msg = 'MISSING FFMPEG!'
		elif self.os == 'Linux':
			proc = subprocess.Popen('which ffmpeg', stdout = subprocess.PIPE, shell = True)
			result = proc.stdout.readline()

			if result:
				self.found_ffmpeg = True
				msg = 'Ready!'
			else:
				self.found_ffmpeg = False
				msg = 'MISSING FFMPEG!'

		return msg
	
	def abort(self):
		for proc in psutil.process_iter():
			if proc.name() == 'ffmpeg.exe' or proc.name() == 'ffmpeg':
				p = psutil.Process(proc.pid)
				p.kill()

				try:
					os.remove('TEMP')
					os.remove('ffmpeg2pass-0.log')
					os.remove('ffmpeg2pass-0.log.mbtree')
					print('TVC: Cleaned up logs and temp files.')
				except:
					print('TVC: No files to clean up.')

				self.is_compressing = False
				self.aborted = True

				print('TVC: Killing ffmpeg process!')
	
	def close(self):
		self.abort()
		print('TVC: Exiting.')
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

		self.output_field.configure(text = f'Selected files:\n\n{self.files}')

		print(f'TVC: Selected files:\n{self.files}')
		print(f'TVC: Extensions:\n{self.file_extensions}')

		root.update()
	
	def compress(self):
		if not self.files:
			print('TVC: No files selected!')
			return
		
		if self.is_compressing:
			print('TVC: Compression in progress!')
			return
		
		self.is_compressing = True
		self.aborted = False

		self.desired_w = self.e_res_w.get() if self.portrait_var.get() == 0 else self.e_res_h.get()
		self.desired_h = self.e_res_h.get() if self.portrait_var.get() == 0 else self.e_res_w.get()
		self.desired_fps = self.e_fps.get()
		self.desired_size = int(self.e_size.get())
		self.desired_extension = self.e_extension.get()

		ffmpeg = 'ffmpeg' if self.os == 'Linux' else 'ffmpeg.exe'
		ffprobe = 'ffprobe' if self.os == 'Linux' else 'ffprobe.exe'

		origin_duration_s = subprocess.Popen(f'{ffprobe} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{self.files[self.cur_queue]}"', stdout = subprocess.PIPE, shell = True)
		origin_duration_s = float(origin_duration_s.stdout.readline())
		self.cur_video_length = origin_duration_s

		print('TVC: Video duration: ' + str(origin_duration_s))

		target_audio_bitrate_kbit_s = 64000

		print(f'TVC: Set file size: {self.desired_size}MB')

		quick_mafs = max(1, ((self.desired_size * 8192.0) / (1.048576 * origin_duration_s) - (target_audio_bitrate_kbit_s / 1000)))
		print('TVC: Set video bitrate: ' + str(quick_mafs))

		print(f'TVC: Set resolution: {self.desired_w}x{self.desired_h}')
		print(f'TVC: Set framerate: {self.desired_fps}')

		desired_audio = f'-c:a aac -b:a {target_audio_bitrate_kbit_s / 1000}k'

		if self.mute_var.get() == 1:
			desired_audio = '-an'
			print('TVC: Set audio muted')
		
		desired_codec = '-c:v libx264'

		if self.h265_var.get() == 1:
			desired_codec = '-c:v libx265'
			print('TVC: Set h.265 video codec')

		if self.desired_extension != '':
			new_extensions = []

			for e in self.file_extensions:
				new_extensions.append('.' + self.desired_extension)
				
			self.file_extensions = new_extensions

			print(f'TVC: Set file extension: {self.desired_extension}')

		cmd = f'{ffmpeg} -y -i "{self.files[self.cur_queue]}" {desired_codec} -b:v {quick_mafs}k -r {self.desired_fps} -vf scale={self.desired_w}:{self.desired_h} -pass 1 -an -f mp4 TEMP && {ffmpeg} -y -i "{self.files[self.cur_queue]}" {desired_codec} -b:v {quick_mafs}k -r {self.desired_fps} -vf scale={self.desired_w}:{self.desired_h} -pass 2 {desired_audio} "{os.getcwd()}/Output/{self.file_names[self.cur_queue]}-Compressed{self.file_extensions[self.cur_queue]}"'
		self.proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True, shell = True)
		
		self.update_output()

	def update_output(self):
		line = self.proc.stdout.readline()
		print(line)

		if self.aborted:
			self.output_field.configure(text = 'Aborted!\n\nThis may be due to too many duplicate frames or a manual abort. If you did not manually abort compression, try matching the framerate to the original video.')
			self.is_compressing = False
			self.cur_queue = 0
		elif 'failed' in line:
			self.output_field.configure(text = f'Video {self.cur_queue + 1}/{len(self.files)} failed!\n\nTry again with different settings.')
			self.is_compressing = False
			self.cur_queue = 0
		elif self.proc.poll() or line == '':
			if self.cur_queue + 1 == len(self.files):
				self.output_field.configure(text = f'Completed!\n\nVideo(s) can be found in the Output folder.')
				self.is_compressing = False
				self.cur_queue = 0

				try:
					os.remove('TEMP')
					os.remove('ffmpeg2pass-0.log')
					os.remove('ffmpeg2pass-0.log.mbtree')
					print('TVC: Cleaned up logs and temp files.')
				except:
					print('TVC: No files to clean up.')
			else:
				self.cur_queue += 1
				self.is_compressing = False
				self.compress()
		else:
			ffmpeg_time = []
			h = 1
			m = 1
			s = 1
			split_space = line.split(' ')

			for split in split_space:
				if 'dup=' in split:
					split_equal = split.split('=')
					if int(split_equal[1]) >= 300:
						self.abort()

			for split in split_space:
				if 'time=' in split:
					split_equal = split.split('=')
					split_colon = split_equal[1].split(':')
					h = float(split_colon[0])
					m = float(split_colon[1])
					s = float(split_colon[2])

			self.cur_video_progress_sec = (h * 3600) + (m * 60) + s
			self.cur_video_progress_percent = int((self.cur_video_progress_sec / self.cur_video_length) * 100)

			self.output_field.configure(text = f'Compressing video {self.cur_queue + 1}/{len(self.files)} to {self.desired_w}x{self.desired_h} {self.desired_fps}fps @ {self.desired_size}MB\nProgress: {self.cur_video_progress_percent}% (2 passes)\n\nFFMPEG Output\n{str(line)}', wraplength=370)
			root.update()
			root.after(1, self.update_output())

root = Tk()
app = App(root)
root.protocol('WM_DELETE_WINDOW', app.close)
root.wm_geometry('400x500')
root.title('TERROR Video Compressor')

try:
	root.iconbitmap('icon.ico')
except:
	print("TVC: Couldn't load icon.")

root.resizable(0, 0)
root.mainloop()