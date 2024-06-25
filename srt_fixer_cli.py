import re
from argparse import ArgumentParser


import argparse
import os
from simplesrt import process_srt


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
        file_path = str(args.input)
        if not file_path or not os.path.isfile(file_path):
            print(f"Input file '{file_path}' does not exist or is not accessible.")
            return

        if not output_file and output_directory:
            new_file_path = os.path.join(output_directory,file_path[:-4] + ".fixed.srt")
        elif os.path.isdir(output_file):
            new_file_path = os.path.join(output_directory, file_path[:-4] + ".fixed.srt")
            pass
        else:
            new_file_path = output_file or file_path[:-4] + ".fixed.srt"

        process_srt(file_path, new_file_path)



if __name__ == "__main__":
    main()
