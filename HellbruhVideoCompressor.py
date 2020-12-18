from tkinter import *
from tkinter import filedialog
from functools import partial
from pathlib import Path
import psutil
import subprocess

class App:
    global file
    global is_compressing
    global aborted

    file = ''
    is_compressing = False
    aborted = False

    def __init__(self, master) -> None:
        pixel = PhotoImage(width=1, height=1)

        # Info frame
        info_frame = Frame(master, width=400, height=75)
        info_frame.pack()
        info_frame.pack_propagate(0)

        info_title = Label(info_frame, text='Hellbruh Video Compressor 2.0', font='Arial 14 bold')
        info_title.pack()

        author_label = Label(info_frame, text='Created by Hellbruh\nCheck for updates @ github.com/hellbruh', font='Arial 8')
        author_label.pack()

        # Options
        options_frame = Frame(master, width=380, height=250)
        options_frame.pack()
        options_frame.pack_propagate(0)

        res_label = Label(options_frame, text='Resolution (width x height)', width=30)
        res_label.grid(row=0, column=0)

        e_res_w = Entry(options_frame, width=7, justify='center')
        e_res_w.insert(0, '1280')
        e_res_w.grid(row=0, column=1)

        res_w_hint_label = Label(options_frame, text='W', width=4, justify='left')
        res_w_hint_label.grid(row=0, column=2)

        e_res_h = Entry(options_frame, width=7, justify='center')
        e_res_h.insert(0, '720')
        e_res_h.grid(row=0, column=3)

        res_h_hint_label = Label(options_frame, text='H', width=4, justify='left')
        res_h_hint_label.grid(row=0, column=4)

        size_label = Label(options_frame, text='Target File Size (ex. 8MB)', width=28)
        size_label.grid(row=1, column=0)

        e_size = Entry(options_frame, width=7, justify='center')
        e_size.insert(0, '8')
        e_size.grid(row=1, column=1)

        size_hint_label = Label(options_frame, text='MB', width=4, justify='left')
        size_hint_label.grid(row=1, column=2)

        spacer = Label(master, text='')
        spacer.pack()

        # Browse
        browse_frame = Frame(master, width=380, height=300)
        browse_frame.pack()
        browse_frame.pack_propagate(0)

        spacer_2 = Label(master, text='')
        spacer_2.pack()

        # Output
        output_frame = LabelFrame(master, width=380, height=290)
        output_frame.pack()
        output_frame.pack_propagate(0)

        output_field = Label(output_frame, text='Waiting to compress...', wraplength=370, justify='center')
        output_field.pack()

        # Browse Buttons
        browse_button = Button(browse_frame, text='Browse', width=15, command=partial(self.file_select, output_field))
        browse_button.grid(row=0, column=0, padx=5)

        abort_button = Button(browse_frame, text='Abort', width=15, command=self.abort)
        abort_button.grid(row=0, column=2, padx=5)

        compress_button = Button(browse_frame, text='Compress', width=15, command=partial(self.compress, e_size, e_res_w, e_res_h, output_field))
        compress_button.grid(row=0, column=1, padx=5)
    
    def abort(self):
        for proc in psutil.process_iter():
            if proc.name() == 'ffmpeg.exe':
                p = psutil.Process(proc.pid)
                p.kill()

                global is_compressing
                is_compressing = False

                global aborted
                aborted = True

                print('Killing ffmpeg process!')
    
    def close(self):
        self.abort()

        print('Exiting.')
        root.destroy()
    
    def file_select(self, output_field):
        f = filedialog.askopenfilename()
        global file
        file = f
        output_field.configure(text=file)
        root.update()
    
    def update_output(self, proc, e_size, e_w, e_h, output_field):
        line = proc.stdout.readline()
        print(line)

        if aborted:
            output_field.configure(text='Aborted!')
        elif proc.poll() or line == '':
            output_field.configure(text=f'Done! Video location: {file}-Compressed.mp4"')

            global is_compressing
            is_compressing = False
        else:
            desired_file_size = int(e_size.get())
            output_field.configure(text=f'Compressing to {e_w} x {e_h} @ {desired_file_size}MB\n' + str(line), wraplength=370)

            root.update()
            
            global job
            job = root.after(1, self.update_output(proc, e_size, e_w, e_h, output_field))
    
    def compress(self, e_size, e_res_w, e_res_h, output_field):
        if file == '':
            print('No file selected!')
            return
        
        global is_compressing
        
        if is_compressing:
            print('Compression in progress!')
            return
        
        is_compressing = True

        global aborted
        aborted = False

        origin_duration_s = subprocess.Popen(f'ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file}"', stdout=subprocess.PIPE, shell=True)
        origin_duration_s = float(origin_duration_s.stdout.readline())

        print('Video duration: ' + str(origin_duration_s))
        
        origin_audio_bitrate_kbit_s = subprocess.Popen(f'ffprobe.exe -v 0 -select_streams a:0 -show_entries stream=bit_rate -of compact=p=0:nk=1 "{file}"', stdout=subprocess.PIPE, shell=True)

        try:
            target_audio_bitrate_kbit_s = float(origin_audio_bitrate_kbit_s.stdout.readline()) / 1000
            print('Audio bitrate: ' + str(target_audio_bitrate_kbit_s))
        except:
            target_audio_bitrate_kbit_s = 1
            print('Audio bitrate: No audio detected')

        desired_file_size = int(e_size.get())
        print(f'New file size: {desired_file_size}MB')

        quick_mafs = ((desired_file_size * 8192.0) / (1.048576 * origin_duration_s) - target_audio_bitrate_kbit_s)
        print('New video bitrate: ' + str(quick_mafs))

        desired_w = e_res_w.get()
        desired_h = e_res_h.get()
        print(f'New video resolution: {desired_w}:{desired_h}')

        cmd = f'ffmpeg.exe -y -i "{file}" -c:v libx264 -b:v {quick_mafs}k -vf scale={desired_w}:{desired_h} -pass 1 -an -f mp4 temp && ffmpeg.exe -y -i "{file}" -c:v libx264 -b:v {quick_mafs}k -vf scale={desired_w}:{desired_h} -pass 2 -c:a aac -b:a {target_audio_bitrate_kbit_s}k "{file}-Compressed.mp4"'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
        
        self.update_output(proc, e_size, desired_w, desired_h, output_field)

root = Tk()
app = App(root)
root.protocol('WM_DELETE_WINDOW', app.close)
root.wm_geometry('400x500')
root.title('Hellbruh Video Compressor 2.0')
root.resizable(0, 0)
root.mainloop()