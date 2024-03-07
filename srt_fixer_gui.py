
from datetime import timedelta
import argparse
from simplesrt import SimpleSrt
from simplesrt import process_srt


try:
    from tqdm import tqdm

    TQDM_INSTALLED = True
except ModuleNotFoundError:
    TQDM_INSTALLED = False



def main():
    parser = argparse.ArgumentParser(description="fix duplicate lines in srt converted youtube auto generated subtitles")
    parser.add_argument("input", nargs="?", help="Input subtitle file.")
    parser.add_argument("-o", "--output", help="Output subtitle file.")
    parser.add_argument("-idir", "--input-directory", help="Input directory containing subtitle files.")
    parser.add_argument("-odir", "--output-directory", help="Output directory for processed subtitle files.")
    args = parser.parse_args()
    input_directory = args.input_directory
    output_directory = args.output_directory

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

        new_file_path = args.output or file_path[:-4] + ".fixed.srt"
        process_srt(file_path, new_file_path)




if __name__ == "__main__":
    main()



import tkinter as tk
from tkinter import ttk, filedialog
import os
import platform
import subprocess


def open_input_file():
    input_file_path.set(filedialog.askopenfilename())
    input_folder_path.set("")


def open_input_folder():
    input_folder_path.set(filedialog.askdirectory())
    input_file_path.set("")


def open_output_dir():
    output_dir_path.set(filedialog.askdirectory())


def open_directory_in_explorer(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def fix_subtitles():
    global root
    if (input_file_path.get() or input_folder_path.get()) and output_dir_path.get():
        if input_file_path.get():
            file_name = os.path.basename(input_file_path.get())
            new_file_path = os.path.join(output_dir_path.get(), os.path.splitext(file_name)[0] + ".fixed.srt")
            process_srt(input_file_path.get(), new_file_path)
        else:
            files = [file for file in os.listdir(input_folder_path.get()) if file.endswith(".srt")]
            progress_bar = ttk.Progressbar(root, length=300, mode="determinate", maximum=len(files))
            progress_bar.grid(row=4, column=0, padx=(20, 20), pady=(5, 20), columnspan=4, sticky="EW")

            for i, file in enumerate(files):
                root.update()
                file_path = os.path.join(input_folder_path.get(), file)
                new_file_path = os.path.join(output_dir_path.get(), os.path.splitext(file)[0] + ".fixed.srt")
                process_srt(file_path, new_file_path)
                progress_bar.step(1)

            progress_bar.grid_forget()

        status_label.config(text="Subtitles fixed successfully!")
        open_directory_in_explorer(output_dir_path.get())
    else:
        status_label.config(text="Error: Please select input file/folder and output directory!")


root = tk.Tk()
root.title("Subtitle Fixer")

input_file_path = tk.StringVar()
input_folder_path = tk.StringVar()
output_dir_path = tk.StringVar()
output_dir_path.set(os.getcwd())
input_file_label = ttk.Label(root, text="Input subtitle file:")
input_file_entry = ttk.Entry(root, textvariable=input_file_path)
input_file_button = ttk.Button(root, text="Browse", command=open_input_file)

input_folder_label = ttk.Label(root, text="Input subtitle folder:")
input_folder_entry = ttk.Entry(root, textvariable=input_folder_path)
input_folder_button = ttk.Button(root, text="Browse", command=open_input_folder)

output_label = ttk.Label(root, text="Output directory:")
output_entry = ttk.Entry(root, textvariable=output_dir_path)
output_button = ttk.Button(root, text="Browse", command=open_output_dir)

fix_button = ttk.Button(root, text="Fix Subtitles", command=fix_subtitles)
status_label = ttk.Label(root, text="")

input_file_label.grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="E")
input_file_entry.grid(row=0, column=1, padx=(5, 20), pady=(20, 5), columnspan=2, sticky="EW")
input_file_button.grid(row=0, column=3, padx=(0, 20), pady=(20, 5))

input_folder_label.grid(row=1, column=0, padx=(20, 5), pady=(5, 5), sticky="E")
input_folder_entry.grid(row=1, column=1, padx=(5, 20), pady=(5, 5), columnspan=2, sticky="EW")
input_folder_button.grid(row=1, column=3, padx=(0, 20), pady=(5, 5))

output_label.grid(row=2, column=0, padx=(20, 5), pady=(5, 5), sticky="E")
output_entry.grid(row=2, column=1, padx=(5, 20), pady=(5, 5), columnspan=2, sticky="EW")
output_button.grid(row=2, column=3, padx=(0, 20), pady=(5, 5))

fix_button.grid(row=3, column=1, padx=(0, 20), pady=(20, 20), columnspan=2)
status_label.grid(row=4, column=0, padx=(20, 20), pady=(5, 20), columnspan=4, sticky="EW")

root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)



root.mainloop()


