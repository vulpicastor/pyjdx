#!/usr/bin/env python3

# Author: Lizhou Sha <slz@mit.edu>

from __future__ import division, print_function
import numpy as np

DATATYPE_MAP = {"(X++(Y..Y))": "xyy",
                "(XY..XY)": "xy",
                "(XYZ..XYZ)": "xyz",
                "(XYA)": "xya",
                "(XYWA)": "xywa"}

DATA_START = {"xydata", "xypoint", "peak table", "radata"}

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

def comment_stripper(header_line):
    """-> header.strip(), comment.strip()

    header=="" indicates a full comment line.
    """
    split_line = header_line.split("$$", 1)
    if len(split_line) > 1:
        header, comment = split_line
        return header.strip(), comment.strip()
    else:
        return split_line[0].strip(), ""

def jdx_reader(filename):
    """Opens a JCAMP-DX file and returns its contents in a dictionary."""

    # Initialization
    jdx_dict = {"comments":""}
    x = []
    y = []
    data_start = ""
    data_lines = []

    with open(filename) as jdx_file:
        for line in jdx_file:
            header, comment = comment_stripper(line)
            if comment:
                jdx_dict["comments"] += comment + "\n"
            if not header:
                continue
            elif header.startswith("##"):
                # Enter header key & value into jdx_dict
                key, value = header.lstrip("##").split("=", 1)
                key = key.lower()
                jdx_dict[key] = try_str_to_num(value)
                if key in DATA_START:
                    data_start = key
            elif not data_start:
                jdx_dict[key] += "\n" + header
            elif data_start:
                # Store all the data lines for later processing
                data_lines.append(header)
            else:
                # Just in case, so that I know the code is failing
                raise JdxParserError("Uncaught case while parsing JDX file.")

    data_type = DATATYPE_MAP[jdx_dict[data_start]]
    jdx_dict.update(data_parser(data_lines, data_type, **jdx_dict))
    jdx_dict.update(data_transformer(**jdx_dict))
    sanity_check(jdx_dict)

    return jdx_dict
