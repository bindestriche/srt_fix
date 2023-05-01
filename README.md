This repository contains a  plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme). 
it fixes duplicate lines in youtube subitles



## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/yt-dlp/yt-dlp-sample-plugins/archive/master.zip
```

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.


## usage 

` yt-dlp https://www.youtube.com/xxxx --write-auto-sub  --sub-lang en  --convert-subs=srt  --use-postprocessor srt_fix`

### srt fixer cli
If you use `--skip download` the postprocessor is not triggered and no conversion happens. for that case you can use
[srt_fixer_cli.py](srt_fixer_cli.py) to process the files independently.
If you prefer a graphical user interface, check out 
[subtitle_fixer_tk.exe](https://github.com/bindestriche/youtubesubsearcher) in my other repo. 