import re
from argparse import ArgumentParser
from datetime import timedelta
from typing import List, Tuple, Union, Iterator
import argparse
import os


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

    def __init__(self, start_duration: timedelta, end_duration: timedelta, text: str):
        self.start = start_duration
        self.end = end_duration
        self.text = text.strip()

    @staticmethod
    def _print_duration(duration: timedelta) -> str:
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{duration.microseconds // 1000:03d}"

    def __str__(self) -> str:
        return f"{self._print_duration(self.start)} --> {self._print_duration(self.end)}\n{self.text}\n\n"

    def __repr__(self) -> str:
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

    def __init__(self, srt_string: str):
        self.subs = self.parse_srt(srt_string)

    @staticmethod
    def get_duration(parts: list[int, int, int, int]) -> timedelta:
        """
        get_duration(parts: Tuple[int, int, int, int]) -> timedelta:
        Returns a timedelta object representing the duration from a tuple of hours, minutes, seconds, and milliseconds.

        :param parts:  Tuple[int, int, int, int])
        :return: timedelta
        """
        hour, minute, second, millisecond = parts

        return timedelta(hours=hour, minutes=minute, seconds=second, milliseconds=millisecond)

    def parse_timecode_string(self, line: str) -> Union[bool, Tuple[timedelta, timedelta]]:
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

    def parse_srt(self, subtitle_text: str) -> Iterator[Subtitle]:
        srtlines = [x for x in subtitle_text.split("\n") if len(x.strip()) > 0]

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


# nice progressbar via tqdm
try:
    from tqdm import tqdm

    TQDM_INSTALLED = True
except ModuleNotFoundError:
    TQDM_INSTALLED = False

def main():
    parser: ArgumentParser = argparse.ArgumentParser(description="fix duplicate lines in srt converted youtube auto generated subtitles")
    parser.add_argument("input", nargs="?", help="Input subtitle file.")
    parser.add_argument("-o", "--output", help="Output subtitle file.")
    parser.add_argument("-idir", "--input-directory", help="Input directory containing subtitle files.")
    parser.add_argument("-odir", "--output-directory", help='Output directory for processed subtitle files.')
    args = parser.parse_args()
    input_directory = args.input_directory
    output_directory = args.output_directory
    output_file = args.output
    if output_file and not input_directory:
        output_directory=None



    if input_directory:
        if not os.path.isdir(input_directory):
            print(f"Input directory '{input_directory}' does not exist or is not accessible.")
            return

        if not output_directory:
            output_directory = input_directory

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if not TQDM_INSTALLED:
            filelist = os.listdir(input_directory)
            filecount = len(filelist)
            counter = 1
            for file in filelist:
                deciles = int(counter / filecount * 20)
                print(f"processing SRT files:|{'█' * deciles}{' ' * (20 - deciles)}| {counter}/{filecount}", end='\r')
                if counter == filecount:
                    print("\n", end="\r")
                counter += 1
                if file.endswith(".srt"):
                    file_path = os.path.join(input_directory, file)
                    new_file_path = os.path.join(output_directory, file[:-4] + ".fixed.srt")
                    process_srt(file_path, new_file_path)
        else:
            for file in tqdm(os.listdir(input_directory), desc="Processing SRT files", unit="file",
                             bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
                if file.endswith(".srt"):
                    file_path = os.path.join(input_directory, file)
                    new_file_path = os.path.join(output_directory, file[:-4] + ".fixed.srt")
                    process_srt(file_path, new_file_path)
    else:
        file_path = args.input
        if not file_path or not os.path.isfile(file_path):
            print(f"Input file '{file_path}' does not exist or is not accessible.")
            return

        if not output_file and output_directory:
            new_file_path = os.oath.join(output_directory,file_path[:-4] + ".fixed.srt")
        elif os.path.isdir(output_file):
            new_file_path = os.oath.join(output_directory, file_path[:-4] + ".fixed.srt")
            pass

            new_file_path = output_file or file_path[:-4] + ".fixed.srt"

        process_srt(file_path, new_file_path)


def process_srt(file_path: str, new_file_path: str):
    with open(file_path, "r", encoding="utf8") as file, open(new_file_path, "w", encoding="utf8") as new_file:
        srtstring = file.read()
        srt = SimpleSrt(srtstring)
        subs_iter = srt.subs
        last_subtitle = None
        index = 1
        while True:
            try:
                subtitle = next(subs_iter)
            except StopIteration:
                break

            if last_subtitle is not None:
                if subtitle is not None:
                    subtitle.text = subtitle.text.strip("\n ")
                    if len(subtitle.text) == 0:  # skip over empty subtitles
                        continue
                    if (subtitle.start - subtitle.end < timedelta(milliseconds=150) and
                            last_subtitle.text in subtitle.text):
                        last_subtitle.start = subtitle.end
                        continue
                    current_lines = subtitle.text.split("\n")
                    last_lines = last_subtitle.text.split("\n")
                    if current_lines[0] == last_lines[-1]:
                        subtitle.text = "\n".join(current_lines[1:])
                    if subtitle.start < last_subtitle.end:
                        last_subtitle.end = subtitle.start - timedelta(milliseconds=1)
                new_file.write(f"{index}\n{last_subtitle}")
                index += 1

            if subtitle is None:
                break
            last_subtitle = subtitle


if __name__ == "__main__":
    main()
