import re
from argparse import ArgumentParser
from datetime import timedelta
from typing import List, Tuple, Union, Iterator
import argparse
import os
from simplesrt import SimpleSrt


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
