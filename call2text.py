#! usr/bin/env python

"""
Each Recognizer instance has seven methods for
recognizing speech from an audio source using various APIs. These are:

recognize_bing(): Microsoft Bing Speech
recognize_google(): Google Web Speech API
recognize_google_cloud(): Google Cloud Speech - requires installation of the google-cloud-speech package
recognize_houndify(): Houndify by SoundHound
recognize_ibm(): IBM Speech to Text
recognize_sphinx(): CMU Sphinx - requires installing PocketSphinx
recognize_wit(): Wit.ai
Of the seven, only recognize_sphinx() works offline with the CMU Sphinx engine.


Problems we are trying to solve:
Taking meeting notes
Losing Ideas
Personal Semantic Analysis

"""

def cmd_line_input():
    """
    command line interface for input
    """

    help_msg = """
    usage: call2text.py [-h] [-f] [-d]
    required: audio files
    A program to convert meetings to notes.
    
    optional arguments:
    ::::Args:::::::::Output:::::Desc::::

        -h, --help   str        show this help message and exit

    required arguments:
    ::::Args:::::::::Output:::::Desc::::
        You must supply either a file or directory path
        -f, --file   list       file location that we should target
        -d, --dir    list       directory location that we should target
               """

    parser = argparse.ArgumentParser(description='Comand line parse for input options',
                                     add_help=False)

    parser.add_argument("-h",
                        "--help",
                        action="help",
                        help=help_msg
                        )
    parser.add_argument("-t",
                        "--file_type",
                        dest="file_type",
                        required=True,  # required for now
                        help="""set a file type ex.
                        -t .m4a  etc
                        You can set one type for now!"""
                        )
    parser.add_argument("-f",
                        "--file",
                        nargs='+',
                        dest="file",
                        required=False,  # required for now
                        help="""set a file target ex.
                        -f path/file.txt path/file2.txt etc
                        You can set one or as many as you like"""
                        )
    parser.add_argument("-d",
                        "--dir",
                        nargs='+',
                        dest="dir",
                        required=False,  # required for now
                        help="""set a directory target ex.
                        -f path/ path/ etc
                        You can set one or as many as you like"""
                        )
    # parser.add_argument("-t",
    #                     "--test",
    #                     action='store_true',
    #                     help='include this flag to run testing with -f <path>'
    #                     )

    return parser.parse_args()

def check_args_and_assign(arguements):
    """Check for arguements in file and dir
       Assign the target after that"""

    if arguements.file:
       possible_paths = arguements.file
    else:
        possible_paths = find_files_in_dir(arguements.dir, arguements.file_type)

    # assert(possible_paths is not None,
    #        'Please supply a file or directory target. See the help message for reference...'
    #        )
    print(possible_paths)
    return possible_paths

def find_files_in_dir(directory, file_type):
    """If we are supplied a dir then find all directories
    Then find all the files we need in each"""


    target_list = []
    for dir in directory:
        for dir_info in os.walk(dir, topdown=False):  # tuple of files at the bottom
            ignore = False
            for filename in dir_info[2]:
                print(filename)
                if 'meeting_notes.txt' in filename:
                    ignore = True
            if ignore == False:
                for filename in dir_info[2]:
                    if filename.endswith(file_type):
                        target_list.append((dir_info[0], filename))
            else:
                pass
                 #   target_list.append(os.path.join("/mydir", file))
    return target_list

def convert_audio(file_info, file_type):
    """Convert a single path to file from m4a to wav"""


    # Packages reqd: pydub, ffmpeg

    # pydub - pip install pydub

    # ffmpeg:
    # sudo add-apt-repository ppa:kirillshkrogalev/ffmpeg-next
    # sudo apt-get update
    # sudo apt-get install ffmpeg

    ## Converting to wav
    # Using pydub

    # Convert all file extensions to m4a (if required)

    # import os, sys
    # folder = 'M4a_files/'
    # for filename in os.listdir(folder):
    #     infilename = os.path.join(folder, filename)
    #     if not os.path.isfile(infilename): continue
    #     oldbase = os.path.splitext(filename)
    #     newname = infilename.replace('.tmp', '.m4a')
    #     output = os.rename(infilename, newname)

    # Convert m4a extension files to wav extension files

    filepath = f'{file_info[0]}/{file_info[1]}'

    path, file_extension = os.path.splitext(filepath)
    file_extension_final = file_extension.replace('.', '')
    # print(path, file_extension, file_extension_final)
    # try:
    track = AudioSegment.from_file(filepath, file_extension_final)
    wav_filename = file_info[1].replace(file_extension_final, 'wav')
    wav_path = file_info[0] + '/' + wav_filename
    print('CONVERTING: ' + str(path))
    track.export(wav_path, format='wav')
    store_text(file_info[0],voice2text(wav_path))
    os.remove(wav_path)
    # except Exception as exc:
    #     print("ERROR CONVERTING " + str(path), '\n', exc)


def voice2text(target):
    """Use google recognize to transcribe to text"""

    audio_file = sr.AudioFile(target)

    r = sr.Recognizer()
    with audio_file as source:
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)

        text = r.recognize_google(audio_data)
        print(text)
        return text


def store_text(dir, text):
    """store text in the local dir
       create a file and save
    """

    filename = f'{dir}/meeting_notes.txt'
    # file_dir = target.rpartition('/')[0]
    file = open(filename, 'w+')
    print(f'Meeting notes stored at: {filename}', '\n')
    file.write(text)
    file.close()

if __name__ == '__main__':

    import argparse
    import logging
    import os
    import speech_recognition as sr
    from pydub import AudioSegment
    import time
    # import PocketSphinx
    # import AudioFile
    # from pocketsphinx import AudioFile

    LOG_FILE = ''.join([os.getcwd(), 'voice2text.log'])
    LOGGER = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG,
                        filename=LOG_FILE,
                        filemode='w',  # over write for single use currently default is append
                        format='%(asctime)s : %(name)s - %(levelname)s - %(message)s')
    logging.warning('This will get logged to a file')

    ARGS = cmd_line_input()
    print(ARGS)
    targets = check_args_and_assign(ARGS)
    print(targets)
    for file in targets:  # Feed the filename directly (Threading may want to start here)
        try:
            wav_file = convert_audio(file, ARGS.file_type)
        except Exception as exc:
            print(exc)
            pass
        time.sleep(10)
        # text = voice2text(file)
        # store_text(text)

# /Users/truth/Documents/Zoom
