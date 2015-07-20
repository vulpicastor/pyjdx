#!/usr/bin/env python3

# Author: Lizhou Sha <slz@mit.edu>

from __future__ import division, print_function
import numpy as np

XYDATA_MAP = {"(X++(Y..Y))": "xyy",
              "(XY..XY)": "xyxy"}

def sanity_check(jdx_dict):
    # TODO: Check obtained data with header max & min of x & y.
    return True

def try_str_to_num(string):
    """string -> number (int or float)"""
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string
    except:
        raise TypeError("Unknown error while trying to convert string into number.")
        

def line_splitter(data_line):
    """An alias of data_line.split()

    Warning: This function is not entirely correct due to complications with negative signs."
    """
    # TODO: Splits line correctly if minus signs are used in place of whitespace
    return data_line.split()

def xyy_line_parser(data_line, deltax):
    """JDX data line in the (X++(Y..Y)) format -> x, y in np.array"""
    xyy = np.array(line_splitter(data_line), dtype="float")
    x_start, y = xyy[0], xyy[1:]
    x = np.array([x_start + deltax * i for i, _ in enumerate(y)])
    return x, y

def data_parser(data_lines, data_type, **kwargs):
    """
    Takes the data lines of a JDX file and processes them according to the data type.
    """
    if data_type == "xyy":
        xs, ys = [], []
        for line in data_lines:
            x, y = xyy_line_parser(line, kwargs["deltax"])
            xs.append(x)
            ys.append(y)
        return {"x": np.concatenate(xs), "y": np.concatenate(ys)}
    else:
        raise Exception("JCAMP-DX data type {0} not supported".format(data_type))

def data_transformer(x, y, xfactor, yfactor, **kwargs):
    """Multiplies x or y data by their corresponding factor."""
    return {"x": x * xfactor, "y": y * yfactor}

def jdx_reader(filename):
    """Opens a JCAMP-DX file and returns its contents in a dictionary."""

    # Initialization
    jdx_dict = {}
    x = []
    y = []
    data_lines = []

    with open(filename) as jdx_file:
        data_start = False
        for line in jdx_file:
            if line.startswith("##"):
                # Enter header key & value into jdx_dict
                key, value = line.lstrip("##").split("=", 1)
                jdx_dict[key.lower()] = try_str_to_num(value.rstrip("\n"))
                if key.lower() == "xydata":
                    data_start = True
            elif not data_start:
                continue
            elif data_start:
                # Store all the data lines for later processing
                data_lines.append(line)
            else:
                # Just in case, so that I know the code is failing
                raise Exception("Uncaught case while parsing JDX file.")

    data_type = XYDATA_MAP[jdx_dict["xydata"]]
    jdx_dict.update(data_parser(data_lines, data_type, **jdx_dict))
    jdx_dict.update(data_transformer(**jdx_dict))
    sanity_check(jdx_dict)

    return jdx_dict

