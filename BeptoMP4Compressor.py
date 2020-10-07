import tkinter
from tkinter import filedialog
from functools import partial
from pathlib import Path
import platform
import subprocess
import psutil
import sys
import os

root = tkinter.Tk()
root.wm_geometry('325x515')
root.title('Bepto MP4 Compressor')
root.resizable(0, 0)

def close_window():
    pid = None
    for proc in psutil.process_iter():
        if proc.name() == 'ffmpeg':
            pid = proc.pid

    if pid != None:
        p = psutil.Process(pid)
        p.kill()
        print("Killed ffmpeg before closing!")

    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_window)

mp4_file = ""
pixel = tkinter.PhotoImage(width=1, height=1)

app_title = tkinter.Label(text='Bepto MP4 Compressor', font='Arial 14 normal')
app_title.pack()

author_label = tkinter.Label(text='Created by bepto:\nhttps://github.com/beptodev', font='Arial 8')
author_label.pack()

purpose = tkinter.Label(text='What?:\nThis app compresses mp4 files to any resolution and file size.', font='Arial 8')
purpose.pack()

def file_select():
    global mp4_file
    mp4_file = filedialog.askopenfilename()
    file.configure(text=mp4_file, anchor='e')
    compress_btn.configure(state=tkinter.NORMAL, text='Begin Compression', command=partial(compress, mp4_file))
    root.update()

options_frame = tkinter.LabelFrame(text='Options', width=294, height=100)
options_frame.pack()
options_frame.pack_propagate(0)

res_label = tkinter.Label(options_frame, text='Resolution Width (ex. 1920px = 1080p)', width=28)
res_label.grid(row=0, column=0)

e_res = tkinter.Entry(options_frame, width=8, justify='center')
e_res.insert(10, '1920')
e_res.grid(row=0, column=1)

res_hint_label = tkinter.Label(options_frame, text='px', width=4, justify='left')
res_hint_label.grid(row=0, column=2)

size_label = tkinter.Label(options_frame, text='Target File Size (ex. 8MB)', width=28)
size_label.grid(row=1, column=0)

e_size = tkinter.Entry(options_frame, width=8, justify='center')
e_size.insert(10, '8')
e_size.grid(row=1, column=1)

size_hint_label = tkinter.Label(options_frame, text='MB', width=4, justify='left')
size_hint_label.grid(row=1, column=2)

browse_frame = tkinter.LabelFrame(text='Select a .mp4 file', width=294, height=100)
browse_frame.pack()
browse_frame.pack_propagate(0)

browse_btn = tkinter.Button(browse_frame, text='Browse .mp4', command=file_select, image=pixel, width=225, height=15, compound='c')
browse_btn.pack()

file = tkinter.Label(browse_frame, text='', wraplength=225)
file.pack()

def update_output(proc):
    line = proc.stdout.readline()
    print(line)
    if proc.poll() or line == '':
        output_field.configure(text=f'Done! Video location: {mp4_file}-Compressed.mp4"')
        browse_btn.configure(state=tkinter.NORMAL)
        compress_btn.configure(state=tkinter.DISABLED)
    else:
        global e_res
        desired_resolution = e_res.get()
        global e_size
        desired_file_size = int(e_size.get())
        output_field.configure(text=f'Compressing to {desired_resolution}p @ {desired_file_size}MB\n' + str(line), wraplength=225)
        root.update()
        global job
        job = root.after(1, update_output(proc))

def compress(mp4_file):
    compress_btn.configure(state=tkinter.DISABLED)
    browse_btn.configure(state=tkinter.DISABLED)
    output_field.configure(text='Compressing...')
    root.update()
    
    if platform.system() == 'Windows':
        origin_duration_s = subprocess.Popen(f'ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)
        origin_duration_s = float(origin_duration_s.stdout.readline())
        print('Video duration: ' + str(origin_duration_s))
        origin_audio_bitrate_kbit_s = subprocess.Popen(f'ffprobe.exe -v 0 -select_streams a:0 -show_entries stream=bit_rate -of compact=p=0:nk=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)

        try:
            target_audio_bitrate_kbit_s = float(origin_audio_bitrate_kbit_s.stdout.readline()) / 1000
            print('Audio bitrate: ' + str(target_audio_bitrate_kbit_s))
        except:
            target_audio_bitrate_kbit_s = 1
            print('Audio bitrate: No audio detected')

        global e_size
        desired_file_size = int(e_size.get())
        print(f'New file size: {desired_file_size}MB')

        quick_mafs = ((desired_file_size * 8192.0) / (1.048576 * origin_duration_s) - target_audio_bitrate_kbit_s)
        print('New video bitrate: ' + str(quick_mafs))

        global e_res
        desired_resolution = e_res.get()
        print(f'New video resolution: {desired_resolution}p')

        cmd = f'ffmpeg.exe -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale=720:-2 -pass 1 -an -f mp4 temp && ffmpeg.exe -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale={desired_resolution}:-2 -pass 2 -c:a aac -b:a {target_audio_bitrate_kbit_s}k "{mp4_file}-Compressed.mp4"'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)

    update_output(proc)

begin_frame = tkinter.LabelFrame(text='Begin', width=294, height=50)
begin_frame.pack()
begin_frame.pack_propagate(0)

compress_btn = tkinter.Button(begin_frame, text='Begin Compression', command=partial(compress, mp4_file), state=tkinter.DISABLED, image=pixel, width=225, height=15, compound='c')
compress_btn.pack()

output_frame = tkinter.LabelFrame(text='Output', width=294, height=200)
output_frame.pack()
output_frame.pack_propagate(0)

output_field = tkinter.Label(output_frame, text='', wraplength=225, justify='center')
output_field.pack()

root.mainloop()
