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
root.wm_geometry('325x400')
root.title('Discord 8MB MP4 Compressor')
root.resizable(0, 0)

mp4_file = ''
pixel = tkinter.PhotoImage(width=1, height=1)

app_title = tkinter.Label(text='Discord 8MB MP4 Compressor', font='Arial 14 normal')
app_title.pack()

author_title = tkinter.Label(text='Created by salt_pouch\nhttps://github.com/saltpouch/', font='Arial 8')
author_title.pack()

disclaimer = tkinter.Label(text='DISCLAIMER\nVideos over 1 minute will look terrible.', font='Arial 8')
disclaimer.pack()

def file_select():
    global mp4_file
    mp4_file = filedialog.askopenfilename()
    file.configure(text=mp4_file, anchor='e')
    compress_btn.configure(state=tkinter.NORMAL, command=partial(compress, mp4_file))

browse_btn = tkinter.Button(root, text='Browse', command=file_select, image=pixel, width=200, height=25, compound='c')
browse_btn.pack()

browse_frame = tkinter.LabelFrame(text='Select .mp4', width=225, height=50)
browse_frame.pack()
browse_frame.pack_propagate(0)

file = tkinter.Label(browse_frame, text='No file selected')
file.pack()

def update_output(proc):
    line = proc.stdout.readline()
    if proc.poll() or line == '':
        output_field.configure(text=f'Done! File: {mp4_file}-8MbShare.mp4"')
        browse_btn.configure(state=tkinter.NORMAL)
        abort_btn.configure(state=tkinter.DISABLED)
    else:
        output_field.configure(text='Compressing...\n' + str(line), wraplength=225)
        root.update()
        global job
        job = root.after(10, update_output(proc))

def compress(mp4_file):
    compress_btn.configure(state=tkinter.DISABLED)
    browse_btn.configure(state=tkinter.DISABLED)
    abort_btn.configure(state=tkinter.NORMAL)
    output_field.configure(text='Compressing...')
    root.update()
    
    if platform.system() == 'Linux':
        origin_duration_s = subprocess.Popen(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)
        origin_duration_s = float(origin_duration_s.stdout.readline())
        print(origin_duration_s)
        origin_audio_bitrate_kbit_s = subprocess.Popen(f'ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)
        target_audio_bitrate_kbit_s = float(origin_audio_bitrate_kbit_s.stdout.readline()) / 1000
        print(target_audio_bitrate_kbit_s)
        quick_mafs = ((8.0 * 8192.0) / (1.048576 * origin_duration_s) - target_audio_bitrate_kbit_s)
        cmd = f'ffmpeg -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale=720:-2 -pass 1 -an -f mp4 /dev/null && ffmpeg -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale=720:-2 -pass 2 -c:a aac -b:a {target_audio_bitrate_kbit_s}k "{mp4_file}-8MbShare.mp4"'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
    elif platform.system() == 'Windows':
        origin_duration_s = subprocess.Popen(f'ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)
        origin_duration_s = float(origin_duration_s.stdout.readline())
        print(origin_duration_s)
        origin_audio_bitrate_kbit_s = subprocess.Popen(f'ffprobe.exe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "{mp4_file}"', stdout=subprocess.PIPE, shell=True)
        target_audio_bitrate_kbit_s= float(origin_audio_bitrate_kbit_s.stdout.readline()) / 1000
        print(target_audio_bitrate_kbit_s)
        quick_mafs = ((8.0 * 8192.0) / (1.048576 * origin_duration_s) - target_audio_bitrate_kbit_s)
        print(quick_mafs)
        cmd = f'ffmpeg.exe -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale=720:-2 -pass 1 -an -f mp4 temp && ffmpeg.exe -y -i "{mp4_file}" -c:v libx264 -b:v {quick_mafs}k -vf scale=720:-2 -pass 2 -c:a aac -b:a {target_audio_bitrate_kbit_s}k "{mp4_file}-8MbShare.mp4"'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        
    update_output(proc)

compress_btn = tkinter.Button(root, text='Compress', command=partial(compress, mp4_file), state=tkinter.DISABLED, image=pixel, width=200, height=25, compound='c')
compress_btn.pack()

output_frame = tkinter.LabelFrame(text='Output', width=225, height=125)
output_frame.pack()
output_frame.pack_propagate(0)

output_field = tkinter.Label(output_frame, text='Waiting to begin...', justify='center')
output_field.pack()

def abort_compress():
    pid = None
    for proc in psutil.process_iter():
        if proc.name() == 'ffmpeg':
            pid = proc.pid

    if pid != None:
        p = psutil.Process(pid)
        p.kill()
        abort_btn.configure(state=tkinter.DISABLED)
        browse_btn.config(state=tkinter.NORMAL)
        root.after_cancel(job)
        output_field.configure(text='Aborted!')

abort_btn = tkinter.Button(text='Abort', command=abort_compress, state=tkinter.DISABLED, image=pixel, width=200, height=25, compound='c')
abort_btn.pack()

root.mainloop()
