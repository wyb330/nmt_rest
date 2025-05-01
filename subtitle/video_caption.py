import os

from subtitle.writers import WebVTTWriter, SRTWriter, SMIWriter, SBVWriter
from subtitle.exceptions import MalformedFileError, MissingFilenameError
from subtitle.parsers import WebVTTParser, SRTParser, SBVParser, SMIParser
from subtitle.generic import Caption, Style


def extract_file_extension(file):
    basename = os.path.basename(file)
    return '.' + str(basename.split('.')[-1])


class Subtitle(object):
    """
    Parse captions in SubTitle format and also from other formats like SRT.

    To read Subtitle:

        Subtitle().read('captions.vtt')

    For other formats like SRT, use from_[format in lower case]:

        Subtitle().from_srt('captions.srt')

    A list of all supported formats is available calling supported_formats().
    """

    def __init__(self, styles=None):
        self.file = None
        self._captions = []
        self._styles = styles

    def __len__(self):
        return len(self._captions)

    def __getitem__(self, index):
        return self._captions[index]

    def from_srt(self, file):
        """Reads captions from a file in SubRip format."""
        self.file = file
        self._captions = SRTParser().read(file).captions
        return self

    def from_sbv(self, file):
        """Reads captions from a file in YouTube SBV format."""
        self.file = file
        self._captions = SBVParser().read(file).captions
        return self

    def from_vtt(self, file):
        """Reads a WebVTT captions file."""
        parser = WebVTTParser().read(file)
        self.file = file
        self._captions = parser.captions
        self._styles = parser.styles
        return self

    def from_smi(self, file):
        """Reads a SAMI captions file."""
        parser = SMIParser().read(file)
        self.file = file
        self._captions = parser.captions
        self._styles = parser.styles
        return self

    def read(self, file):
        ext = extract_file_extension(file)
        if ext == '.srt':
            return self.from_srt(file)
        elif ext == '.vtt':
            return self.from_vtt(file)
        elif ext == '.smi':
            return self.from_smi(file)
        elif ext == 'sbv':
            return self.from_sbv(file)
        else:
            raise MalformedFileError()

    def _get_output_file(self, output, extension='smi'):
        if not output:
            if not self.file:
                raise MissingFilenameError
            # saving an original vtt file will overwrite the file
            # and for files read from other formats will save as vtt
            # with the same name and location
            return os.path.splitext(self.file)[0] + '.' + extension
        else:
            target = os.path.join(os.getcwd(), output)
            if os.path.isdir(target):
                # if an output is provided and it is a directory
                # the file will be saved in that location with the same name
                filename = os.path.splitext(os.path.basename(self.file))[0]
                return os.path.join(target, '{}.{}'.format(filename, extension))
            else:
                if target[-3:].lower() != extension:
                    target += '.' + extension
                # otherwise the file will be written in the specified location
                return target

    def add(self, start, end, text, identifier=None):
        caption = Caption()
        caption.start = start
        caption.end = end
        caption.text = text
        caption.identifier = identifier
        self._captions.append(caption)

    def save(self, output=''):
        """Save the document.
        If no output is provided the file will be saved in the same location. Otherwise output
        can determine a target directory or file.
        """
        self.file = self._get_output_file(output)
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f)
        return self.file

    def save_as_srt(self, output=''):
        self.file = self._get_output_file(output, extension='srt')
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f, format='srt')
        return self.file

    def save_as_smi(self, output='', extension='smi'):
        self.file = self._get_output_file(output, extension=extension)
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f, format='smi')
        return self.file

    def save_as_vtt(self, output='', extension='vtt'):
        self.file = self._get_output_file(output, extension=extension)
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f, format='vtt')
        return self.file

    def write(self, f, format='vtt'):
        if format == 'vtt':
            WebVTTWriter().write(self._captions, f)
        elif format == 'srt':
            SRTWriter().write(self._captions, f)
        elif format == 'smi':
            SMIWriter(style=self.styles).write(self._captions, f)
        # elif format == 'sbv':
        #     SBVWriter().write(self._captions, f)

    @staticmethod
    def supported_formats():
        """Provides a list of supported formats that this class can read from."""
        return ['WebVTT (.vtt)', 'SubRip (.srt)', 'YouTube SBV (.sbv)']

    @property
    def captions(self):
        """Returns the list of captions."""
        return self._captions

    @property
    def total_length(self):
        """Returns the total length of the captions."""
        if not self._captions:
            return 0
        return int(self._captions[-1].end_in_seconds) - int(self._captions[0].start_in_seconds)

    @property
    def styles(self):
        return self._styles

