# Author: Lizhou Sha <slz@mit.edu>

from __future__ import division, print_function
import numpy as np

DATATYPE_MAP = {"(X++(Y..Y))": "xyy",
                "(XY..XY)": "xy",
                "(XYZ..XYZ)": "xyz",
                "(XYA)": "xya",
                "(XYWA)": "xywa"}

DATA_START_HEADERS = {"xydata", "xypoint", "peak table", "radata"}

class JdxParserError(Exception):
    pass

def sanity_check(jdx_dict):
    # TODO: Check obtained data with header max & min of x & y.
    return True

def try_str_to_num(string):
    """string -> float if is_number else string"""
    try:
        return float(string)
    except ValueError:
        return string
    except:
        raise TypeError("Unknown error while trying to convert string into number.")

def _try_getitem(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return None

def _try_delitem(dictionary, key):
    try:
        del dictionary[key]
    except KeyError:
        return False
    else:
        return True

def deltax(firstx, lastx, npoints, **kwargs):
    """-> (lastx - firstx) / (npoints - 1)"""
    return (lastx - firstx) / (npoints - 1)

def line_splitter(data_line):
    """A line splitter for JDX data lines. str -> [columns]

    Splits along whitespaces as well as minus signs.
    """
    # Temporarily replace floating numbers of the form 1.234E-23
    no_float = data_line.lower().replace("e-", "e~").replace("e+", "e@")
    # All remaining + or - signs may be delimiters
    split_line = no_float.replace("-", " -").replace("+", " +").split()
    # Recover floating numbers
    return [i.replace("e~", "e-").replace("e@", "e+") for i in split_line]

def xyy_line_parser(data_line, deltax):
    """JDX data line in the (X++(Y..Y)) format -> x, y in np.array"""
    xyy = line_splitter(data_line)
    x_start, y = float(xyy[0]), np.array(xyy[1:], dtype="float")
    x = np.array([x_start + deltax * i for i, _ in enumerate(y)])
    return x, y

def data_parser(data_lines, data_type, **kwargs):
    """
    Takes the data lines of a JDX file and processes them according to the data type.
    """
    if data_type == "xyy":
        xs, ys = [], []
        for line in data_lines:
            x, y = xyy_line_parser(line, deltax(**kwargs))
            xs.append(x)
            ys.append(y)
        return {"x": np.concatenate(xs), "y": np.concatenate(ys)}
    else:
        raise JdxParserError("JCAMP-DX data type {0} not supported".format(data_type))

def data_transformer(x, y, xfactor, yfactor, **kwargs):
    """Multiplies x or y data by their corresponding factor."""
    return {"x": x * xfactor, "y": y * yfactor}

def comment_stripper(jdx_line):
    """-> header.strip(), comment.strip()

    header=="" indicates a full comment line.
    """
    split_line = jdx_line.split("$$", 1)
    if len(split_line) > 1:
        header, comment = split_line
        return header.strip(), comment.strip()
    else:
        return split_line[0].strip(), ""

def header_parser(header_line):
    """"##LABEL=value" -> "label", value (float or str)"""
    key, value = header_line.lstrip("#").split("=", 1)
    return key.lower(), try_str_to_num(value)

def jdx_reader(jdx_file, transform_data=True):
    """Iterable of JCAMP-DX file lines -> jdx_dict"""

    # Initialization
    jdx_dict = {"comments":""}
    data_start = ""
    data_lines = []

    for line in jdx_file:
        header, comment = comment_stripper(line)
        if comment:
            jdx_dict["comments"] += comment + "\n"
        if not header:
            continue
        else:
            if not data_start:
                if header.startswith("##"):
                    key, value = header_parser(header)
                    jdx_dict[key] = value
                    if key in DATA_START_HEADERS:
                        data_start = key
                else:
                    if isinstance(jdx_dict[key], str):
                        jdx_dict[key] += "\n" + header
                    else:
                        jdx_dict[key] = str(jdx_dict[key]) + "\n" + header
            else:
                # Store all the data lines for later processing
                if header.lower() != "##end=":
                    data_lines.append(header)
                else:
                    break
    else:
        raise JdxParserError("No data start point identified, "
                             "or JDX file has no ##END=")

    data_type = DATATYPE_MAP[jdx_dict[data_start]]
    if data_lines:
        jdx_dict.update(data_parser(data_lines, data_type, **jdx_dict))
    else:
        raise JdxParserError("JDX file contains no data")
    if transform_data:
        # Multiply x, y by xfactor, yfactor if asked
        jdx_dict.update(data_transformer(**jdx_dict))

    return jdx_dict

def jdx_file_reader(filename, transform_data=True):
    """Opens a JCAMP-DX file and returns its contents in a dictionary."""
    with open(filename) as f:
        return jdx_reader(f, transform_data)

class JdxFile(object):

    default_labels = ["title", "cas registry no", "x", "y", "xunits", "yunits"]

    def __init__(filename):
        jdx_data= jdx_file_reader(filename, True)
        self.title = jdx_data["title"]
        self.cas = _try_getitem(jdx_data, "cas registry no")
        self.x, self.y = jdx_data["x"], jdx_data["y"]
        self.xunits, self.yunits = jdx_data["xunits"], jdx_data["yunits"]
        for key in default_labels:
            _try_delitem(jdx_data, key)
        self._data = jdx_data

    def wavenumber():
        """-> self.x in wavenumber (1/cm)"""
        pass

    def wavelength():
        """-> self.x in wavelength (micrometer)"""
        pass

    def absorbance():
        """-> self.y in absorbance (-log10(I/I_0))"""
        pass

    def transmittance():
        """-> self.y in transmittance (I/I_0)"""
        pass

