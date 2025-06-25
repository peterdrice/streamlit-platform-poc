from tempfile import NamedTemporaryFile
from typing import Iterable
import urllib.request

kepler_colors = {
        'blue': '#1CCDF7',  # blue
        'lightblue': '#89E5F4',  # lightblue
        'orange': '#FF6633',  # orange
        'lightorange': '#FFAF99',  # lightorange
        'green': '#2BCC61',  # green
        'lightgreen': '#BCE2C7'  # lightgreen
    }

def load_kepler_colors() -> dict:
    """
      This function loads a dictionary of the Kepler
      color palette (hex values) for use defining matplotlib colors

      Parameters:
      ----------
      None

      Returns:
      -------
      kepler_palette: dictionary
          A dictionary of Kepler friendly names (key) and 
          hex values (value)
    """
    kepler_colors = {
        'blue': '#1CCDF7',  # blue
        'lightblue': '#89E5F4',  # lightblue
        'orange': '#FF6633',  # orange
        'lightorange': '#FFAF99',  # lightorange
        'green': '#2BCC61',  # green
        'lightgreen': '#BCE2C7'  # lightgreen
    }
    return(kepler_colors)


class SafeOpener(urllib.request.OpenerDirector):
    """
        This class ensures that a urllib.request() is encrypted via SSL certificate,
        and that urllib.request.urlopen() fails with a URLError if attempting 
        to open `http:`, `ftp:`, `file:`, `data:`, or any other URL that doesn't have
        `https:` at the beginning.

        SafeOpener prevents any bad actors from injecting malicious code, and hardens the
        urlopen() function to comply with Bandit requirements.

        Link: https://dev.to/bowmanjd/hardening-and-simplifying-python-s-urlopen-4gee
    """
    def __init__(self, handlers: Iterable = None) -> None:
        """Create an instance of SafeOpener"""
        super().__init__()
        handlers = handlers or (
            urllib.request.UnknownHandler,
            urllib.request.HTTPDefaultErrorHandler,
            urllib.request.HTTPRedirectHandler,
            urllib.request.HTTPSHandler,
            urllib.request.HTTPErrorProcessor,
        )

        for handler_class in handlers:
            self.add_handler(handler_class())

def load_kepler_fonts(font_dict: dict = {
    # Playfair Display
    'title': 'https://github.com/google/fonts/blob/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf',
    # Cabin
    'label': 'https://github.com/google/fonts/blob/main/ofl/cabin/Cabin%5Bwdth%2Cwght%5D.ttf'
}) -> list:
    """
      This function loads a dictionary containing the font type (key), 
      and a URL to the font file (value). Then it returns the fonts
      as `fontproperties` objects for use in Matplotlib.

      Parameters:
      ----------
      font_dict: dictionary
          Font type (key), and font URL (value)

      Returns:
      -------
      fonts: series
          A series that returns as many `fontproperties`
          variables as font_dict (input)
    """
    opener = SafeOpener()

    fonts = []
    # Loop through Dict keys and values
    for f_type, f_url in font_dict.items():
        url = f_url + '?raw=true'  # Because we want the actual file, not HTML

        response = opener.open(url)
        f_temp = NamedTemporaryFile(delete=False, suffix='.ttf')
        # vars() ['f_'+ f_type] = f_temp # dynamically named variable based on Dict name
        f_temp.write(response.read())
        f_temp.close()
        fonts.append(f_temp)

    return(fonts)
