This repository contains a  plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme). 
it fixes duplicate lines in youtube subitles



## Installation

Requires yt-dlp `2023.01.02` or above.

save srt_fix.py under
`C:\Users\{username}\AppData\Roaming\yt-dlp\plugins\srt_fix\yt_dlp_plugins`


You can install this package with pip:
```
python3 -m pip install -U https://github.com/yt-dlp/yt-dlp-sample-plugins/archive/master.zip
```

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.


## usage 

` yt-dlp https://www.youtube.com/xxxx --write-auto-sub  --sub-lang en  --convert-subs=srt  --use-postprocessor srt_fix`

# srt fixer cli
If you use `--skip download` the postprocessor is not triggered and no conversion happens. for that case you can use
[srt_fixer_cli.py](srt_fixer_cli.py) to process the files independently.
If you prefer a graphical user interface, check out 
[subtitle_fixer_tk.exe](https://github.com/bindestriche/youtubesubsearcher) in my other repo. 

# srt fixer gui

SRT Fixer is a simple Python-based tool that processes and fixes issues with SRT subtitle files. The tool removes duplicate lines and corrects timing issues in SRT files, which are common problems in YouTube's automatically generated subtitles. The application is built using Python's Tkinter library for an easy-to-use graphical user interface.


* Fix duplicate lines in subtitle files
* Correct overlapping timings
* Process single files or an entire folder of SRT files


## Installation

### Windows
 downlaod the .exe from release

### other

install  Python 3.7 or higher
run
'python srt_fixer_gui.py'

## Usage

Use the "Browse" buttons to select an input file or an input folder containing SRT files.
Select an output folder to save the fixed SRT files.
Click the "Fix Subtitles" button to process and fix the selected subtitle files.
A progress bar will show the progress of the subtitle processing.
Upon completion, a success message will be displayed, and the output folder will open in File Explorer.


