import os
from datetime import timedelta
from typing import List, Tuple, Union, Iterator
import re


class Subtitle:
    """
        A class to represent a single subtitle unit in a subtitle file.

        Attributes
        ----------
        start : timedelta
            The start time of the subtitle.
        end : timedelta
            The end time of the subtitle.
        text : str
            The text content of the subtitle.

        Methods
        -------
        _print_duration(duration: timedelta) -> str:
            Returns a formatted string representing the given duration.
        __str__() -> str:
            Returns a string representation of the subtitle, including start and end times and text content.
        __repr__() -> str:
            Returns a string representation of the Subtitle object with its attributes.
    """

    def __init__(self, start_duration, end_duration, text):
        self.start = start_duration
        self.end = end_duration
        self.text = text.strip()

    @staticmethod
    def _print_duration(duration) :
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{duration.microseconds // 1000:03d}"

    def __str__(self):
        return f"{self._print_duration(self.start)} --> {self._print_duration(self.end)}\n{self.text}\n\n"

    def __repr__(self):
        return f"Subtitle Object start:{self.start}, end:{self.end}, text:'{self.text}'"


class SimpleSrt:
    """
        A class to parse and manipulate Simple SubRip (SRT) subtitle files.

        Attributes
        ----------
        subs : List[Subtitle]
            A list of Subtitle objects representing the parsed subtitles in the input SRT string.

        Methods
        -------
        get_duration(parts: Tuple[int, int, int, int]) -> timedelta:
        Returns a timedelta object representing the duration from a tuple of hours, minutes, seconds, and milliseconds.

        parse_timecode_string(line: str) -> Union[bool, Tuple[timedelta, timedelta]]:
            Parses a timecode string from an SRT file and returns a tuple of start and end timedelta objects.
            If the line does not contain a valid timecode, returns False.

        parse_srt(subtitle_text: str) -> List[Subtitle]:
            Parses the input SRT string and returns a list of Subtitle objects.

        Usage
        -----
        srt = SimpleSrt(srt_string)
        subs = srt.subs
        """

    def __init__(self, srt_string):
        self.subs = self.parse_srt(srt_string)

    @staticmethod
    def get_duration(parts) :
        """
        get_duration(parts: Tuple[int, int, int, int]) -> timedelta:
        Returns a timedelta object representing the duration from a tuple of hours, minutes, seconds, and milliseconds.

        :param parts:  Tuple[int, int, int, int])
        :return: timedelta
        """
        hour, minute, second, millisecond = parts

        return timedelta(hours=hour, minutes=minute, seconds=second, milliseconds=millisecond)

    def parse_timecode_string(self, line) -> Union[bool, Tuple[timedelta, timedelta]]:
        """
        Parses a timecode string from an SRT file and returns a tuple of start and end timedelta objects.
        If the line does not contain a valid timecode, returns False.

        :param line: string of srt timecode hh:mm:ss,mss --> hh:mm:ss,mss
        :return: tuple of timedelta objects of start and end time
        """
        time_frame_pattern = re.compile(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)")

        if "-->" in line:
            timing = time_frame_pattern.match(line.strip())
            if timing is None:
                return False

            start = self.get_duration([int(x) for x in timing.groups()[0:4]])
            end = self.get_duration([int(x) for x in timing.groups()[4:8]])
            return start, end
        return False

    def parse_srt(self, subtitle_text) :
        srtlines = [x for x in subtitle_text.split("\n") if len(x.strip()) > 0]
        srtlines += ["", ""]

        i = 0
        while i < len(srtlines):
            timecode = self.parse_timecode_string(srtlines[i])
            if timecode:
                y = 0
                text = ""
                try:
                    while not self.parse_timecode_string(srtlines[y + i + 2]):
                        text += srtlines[y + i + 1] + "\n"
                        y += 1
                except IndexError:
                    pass
                start, end = timecode
                yield Subtitle(start, end, text)
                i += y + 1
            else:
                i += 1

def dedupe_yt_srt(subs_iter):
    previous_subtitle = None
    index = 1
    text = ""
    for subtitle in subs_iter:


        if previous_subtitle is None: # first interation set previous subtitle for comparison
             previous_subtitle = subtitle
             continue

        subtitle.text = subtitle.text.strip() # remove trailing linebreaks



        if len(subtitle.text) == 0:  # skip over empty subtitles
            continue

        if (subtitle.start - subtitle.end < timedelta(milliseconds=150) and # very short
                        subtitle.text in previous_subtitle.text ): # same text as previous
            previous_subtitle.end = subtitle.end # lengthen previous subtitle
            continue
        

     
        


        current_lines = subtitle.text.split("\n")
        last_lines = previous_subtitle.text.split("\n")

        singleword=False

        if current_lines[0] == last_lines[-1]: # if first current is  last previous
            if len(last_lines)==1:
                if  len(last_lines[0].split(" "))<2 and len(last_lines[0])>2: # if  is just one word            
                    singleword=True
                    subtitle.text= current_lines[0]+" "+"\n".join(current_lines[1:]) # remove line break after single word
  
                else:
                    subtitle.text = "\n".join(current_lines[1:]) # discard first line of current            
            else:        
                subtitle.text = "\n".join(current_lines[1:]) # discard first line of current
        else: # not fusing two lines
            if len(subtitle.text.split(" "))<=2: # only one word in subtitle
         
                previous_subtitle.end = subtitle.end # lengthen previous subtitle
                title_text=subtitle.text
                if title_text[0]!=" ":
                    title_text=" "+title_text

                previous_subtitle.text+=title_text # add text to previous
                continue # drop this subtitle


        if subtitle.start <= previous_subtitle.end: # remove overlap and let 1ms gap
            previous_subtitle.end = subtitle.start - timedelta(milliseconds=1)

        if subtitle.start >= subtitle.end: # swap start and end if wrong order
            end =subtitle.end 
            subtitle.end= subtitle.start
            subtitle.start = end
            

        if not singleword:
            yield previous_subtitle
        previous_subtitle = subtitle
        index += 1
    yield previous_subtitle



def subs_to_text(subs_iter):
    index = 1
    text = ""

    for subtitle in subs_iter:

        text += f"{index}\n{subtitle}"# conversion to str handles adding timecode
        index += 1


    return text





def process_srt(file_path, new_file_path):
    text = ""
    with open(file_path, "r", encoding="utf8") as file:
        srtstring = file.read()
        srt = SimpleSrt(srtstring)
        subs = dedupe_yt_srt(srt.subs)
        text=subs_to_text(subs)

    with open(new_file_path, "w", encoding="utf8") as new_file:
        new_file.write(text.strip())
