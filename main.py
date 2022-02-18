from tkinter.filedialog import askdirectory
from tkinter.messagebox import showwarning
from colorama import Fore, init
import os
from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
import re
import urllib.request
from pytube import YouTube
from pytube.exceptions import *
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
import threading
import io
from PIL import Image, ImageTk
from http.client import InvalidURL


class App(Tk):
    def __init__(self):
        super().__init__()

        #app vars
        self.output_directory = f'{os.path.expanduser("~")}\\Music'
        self.search_button_accessed = False

        self.title("YT Music Download")
        self.resizable(False, False)
        self.geometry("400x400")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.grid_propagate(0)
        
        #label at top
        self.title_font = tkFont.Font(family="Lucida Grande", size=20)
        self.title_label = Label(self, text="Youtube Album Downloader", font=self.title_font)
        self.title_label.grid(row=0, column=0, sticky=NSEW)

        #output directory and button to change it
        self.output_frame = ttk.Frame(self)
        self.output_frame.grid(row=1, column=0, sticky=NSEW)

        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=2)
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_columnconfigure(1, weight=10)
        self.output_frame.grid_rowconfigure(2, weight=1)
        self.output_frame.grid_columnconfigure(2, weight=1)
        self.output_frame.grid_columnconfigure(3, weight=4)
        self.output_frame.grid_columnconfigure(4, weight=2)

        self.output_frame.grid_propagate(0)

        self.output_entry = Entry(self.output_frame, width=1)
        self.output_entry.grid(row=1, column=1, sticky=NSEW)  
        self.output_entry.configure(state=DISABLED)

        self.update_output_entry()

        self.output_change_button = ttk.Button(self.output_frame, width=1, text="Change Output", command=self.change_output_button_clicked)
        self.output_change_button.grid(row=1, column=3, sticky=NSEW)

        #input playlist name entry
        self.input_frame = ttk.Frame(self)
        self.input_frame.grid(row=2, column=0, sticky=NSEW)

        self.input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=2)
        self.input_frame.grid_rowconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=10)
        self.input_frame.grid_rowconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)
        self.input_frame.grid_columnconfigure(3, weight=4)
        self.input_frame.grid_columnconfigure(4, weight=2)

        self.input_frame.grid_propagate(0)

        self.input_box = Entry(self.input_frame, width=1)
        self.input_box.grid(row=1, column=1, sticky=NSEW)

        self.search_button = ttk.Button(self.input_frame, width=1, text="Search", command=self.search_button_clicked)
        self.search_button.grid(row=1, column=3, sticky=NSEW)

        #thumbnail display
        self.thumbnail_frame = ttk.Frame(self, relief=FLAT)
        self.thumbnail_frame.grid(row=3, column=0, sticky=NSEW)


        self.thumbnail_frame.grid_propagate(0)

        self.thumbnail_canvas = Canvas(self.thumbnail_frame, bg="black", width=320, height=180, borderwidth=0, highlightthickness=0)
        self.thumbnail_canvas.pack(expand=True)

        self.thumbnail_canvas.pack_propagate(0)

        self.current_thumbnail = None

        #progress label
        self.progress_label_frame = ttk.Frame(self, relief=FLAT)
        self.progress_label_frame.grid(row=4, column=0, sticky=NSEW)

        self.progress_label_frame.grid_rowconfigure(0, weight=1)
        self.progress_label_frame.grid_rowconfigure(1, weight=2)
        self.progress_label_frame.grid_columnconfigure(0, weight=1)
        self.progress_label_frame.grid_columnconfigure(1, weight=1)
        self.progress_label_frame.grid_columnconfigure(2, weight=1)

        self.progress_label = Label(self.progress_label_frame, text="No download in progress")
        self.progress_label.grid(row=0, column=1, sticky=NSEW)
        


    def update_output_entry(self):
        self.output_entry.configure(state=NORMAL)
        self.output_entry.delete(0, END)
        self.output_entry.insert(0, self.output_directory)   
        self.output_entry.xview(END)
        self.output_entry.configure(state=DISABLED)

    def change_output_button_clicked(self):
        new_directory = askdirectory()
        if new_directory != "":
            self.output_directory = new_directory
        self.update_output_entry()

    def search_button_clicked(self):
        #check to see if its matches hte format for a playlist link, if it doesnt use the input as the search query to find one
        playlist_pattern = r"https://www.youtube.com/playlist\?list\=.+"
        video_pattern = r"https://www.youtube.com/watch\?v\=.+"
        
        input = self.input_box.get()
        
        is_playlist_link = bool(re.match(playlist_pattern, input))
        is_video_link = bool(re.match(video_pattern, input))

        if input == "":
            showwarning("Warning!", "Input cannot be empty!")
        else:
            if is_playlist_link:
                t = threading.Thread(target=self.download_playlist_videos, args=(input,))
                t.start()
            elif is_video_link:
                self.index = 1
                self.playlist_length = 1
                t = threading.Thread(target=self.download_video, args=(input,self.output_directory,True))
                t.start()
            else:
                #download playlist
                t = threading.Thread(target=self.download_playlist_links, args=(input,))
                t.start()
            self.disable_buttons()


    def download_playlist_links(self, playlist_name):
        #get playlist from user input 
        search_name = playlist_name.replace(" ", "+")
        try:
            html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_name}&sp=EgIQAw%253D%253D")
        except InvalidURL:
            self.enable_buttons()
            showwarning("Warning!", "Invalid URL")
            return False
        except:
            self.enable_buttons()
            showwarning("Warning!", "An unknown error occurred")
            return False

        playlist_ids = re.findall(r"playlist\?list=(\S{0,50})", html.read().decode())
        try:
            #reduce link down 
            playlist_link = ("https://www.youtube.com/playlist?list=" + playlist_ids[0]).split("\"", 1)[0]
        except IndexError:
            #stop function
            return False

        #get each video link
        self.download_playlist_videos(playlist_link)

    def download_playlist_videos(self, link):
        api_key = "AIzaSyAPer0rClRPJ4sdn14LU52haQWja6vCdZU"

        #extract playlist id from url
        query = parse_qs(urlparse(link).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = api_key)
        
        #get info about invidual videos
        request = youtube.playlistItems().list(
            part = "snippet",
            playlistId = playlist_id,
            maxResults = 50
        )
        response = request.execute()

        #get playlis information
        request2 = youtube.playlists().list(
            part = "snippet",
            id = playlist_id,
            maxResults = 50
        )
        
        response2 = request2.execute()
        name=response2['items'][0]['snippet']['title']
        
        #remove potential illgeal characters causing an exception to be thrown
        illegal_characters = ['#', '<', '$', '+', '%', '>', '!', '`', '&', '*', '\'', '|', '{', '?','"', '=', '}', '/', ':', '\\', '@']
        for char in illegal_characters:
            name = name.replace(char, "")

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            
            request = youtube.playlistItems().list_next(request, response)

        video_links = [ 
            f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s'
            for t in playlist_items
        ]

        try:
            os.makedirs(self.output_directory + "/" + name)
        except FileExistsError:
            self.progress_label = Label(self.progress_label_frame, text="No download in progress")
            self.enable_buttons()
            showwarning("Warning!", f"Warning! {name} already exists.")
            return False

        #download videos
        self.playlist_length = len(video_links)
        self.index = 1
        for count, link in enumerate(video_links):
            self.index = count+1
            if count + 1 == len(video_links):
                self.download_video(link, f'{self.output_directory}/{name}/', True)
            else:
                self.download_video(link, f'{self.output_directory}/{name}/', False)


        #reactive button and text box
        self.enable_buttons()
        

    def download_video(self, link, location, isLastVideo):
        yt = YouTube(link)
        thumb = yt.thumbnail_url
        self.progress_label.configure(text=f'Downloading {yt.title} ({self.index}/{self.playlist_length})')

        #replace thumbnail image
        self.thumbnail_canvas.delete(self.current_thumbnail)
        raw_data = urllib.request.urlopen(thumb).read()
        im = Image.open(io.BytesIO(raw_data))

        #reszie to fit canvas
        im = im.resize((320, 180))
        self.current_thumbnail = ImageTk.PhotoImage(im)

        label = Label(image=self.current_thumbnail)
        label.image = self.current_thumbnail # keep a reference!

        self.thumbnail_canvas.create_image(0, 0, image=self.current_thumbnail, anchor=NW)

        video = yt.streams.filter(only_audio=True)
        highest_abr = 0
        vid_to_download = None
        for vid in video:
            abr = int(vid.abr.replace("kbps",""))
            if abr > highest_abr:
                highest_abr = abr
                vid_to_download = vid
        try:
            out_file = vid_to_download.download(output_path=location)
        except VideoUnavailable:
            print(f"{Fore.RED}Video Unavailable!{Fore.WHITE}")
        except:
            print(f'{Fore.RED}An unknown error occurred!{Fore.WHITE}')
        else:
            base, ext = os.path.splitext(out_file)
            new_file = base + ".wav"

            song_name = os.path.basename(new_file)
            
            try:
                os.rename(out_file, new_file)
            except FileExistsError:
                os.remove(out_file)
                self.progress_label.configure(text="No download in progress")
                self.enable_buttons()

                showwarning("Warning!", f"Warning! {song_name} already exists.")
                return False

                
            print(f'{Fore.GREEN}{song_name} sucessfully downloaded!{Fore.WHITE}')

        if isLastVideo:
            #reactive button and text box
            self.enable_buttons()

    def disable_buttons(self):
        self.input_box.configure(state=DISABLED)
        self.search_button.configure(state=DISABLED)
        self.output_change_button.configure(state=DISABLED)

    def enable_buttons(self):
        self.input_box.configure(state=NORMAL)
        self.input_box.delete(0, END)
        self.search_button.configure(state=NORMAL)
        self.output_change_button.configure(state=NORMAL)


if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    #init colorama
    init()

    app = App()
    app.mainloop()