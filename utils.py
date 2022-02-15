import unicodedata
from fractions import Fraction


def fraction_to_float(fraction: str) -> float:
    # convert fraction strings to float
    fraction = fraction.replace("⁄", "/")
    try:
        fraction_out = unicodedata.numeric(fraction)
    except TypeError:
        try:
            fraction_out = float(sum(Fraction(s) for s in fraction.split()))
        except ValueError:
            fraction_split = fraction.split()
            fraction_out = float(fraction_split[0]) + unicodedata.numeric(
                fraction_split[1]
            )
    return fraction_out


def string_to_float(input: str) -> float:
    # convert decimal strings to float
    try:
        output = float(input)
    except ValueError:
        output = None

    return output