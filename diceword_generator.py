#!/usr/bin/python3

# Copyright © 2021 Waleed H. Mebane
# This file is licensed to you under the terms of the
# BSD 3-Clause "New" or "Revised" License that was provided
# by the author in an accompanying file named "LICENSE"
# or may be found online at:
# https://opensource.org/licenses/BSD-3-Clause

# SPDX-License-Identifier: BSD-3-Clause

""" Generate a random Dicewords passphrase using the cross-platform
operating-system-based random number generating facility (os.urandom) """
import os
import sys
import argparse
import logging
import itertools
from math import ceil
from typing import List, Dict, Iterable
from typing_extensions import Final

NUM_DICEWORDS: Final[int] = int(pow(6, 5)) #permutations of 5 die rolls
DICEWORDS_BITS_PER_WORD: Final[int] = 13
BITS_PER_BYTE: Final[int] = 8


def gen_diceword_indexes(random_number: int,
                         num_indexes_to_generate: int) -> Iterable[int]:
    """ generator to generate indexes into the Dicewords list
    starting from a random number encoding all of the indexes.
    I.e., the input is a number between 0 and 7776
    (which is 6 raised to the power of 5) raised to the power of
    the number of words to generate, at least.  The end point number
    can be larger, which is expected to be the case since 7776 is not
    an even number of bytes, which we will get when generating the
    random number.
    Six raised to the power of five is the number of permutations of
    5 six-sided die rolls.  That raised to the power of number
    of words is the number of permutations of words."""
    # Diceword indexes are derived from a large random number by unpacking
    # it as five base-6 number-positions each (i.e., using modulo division
    # by 6 raised to the power of 5). The indexes are generated from
    # the little end (least significant digits) of the input number to the
    # big end.
    if num_indexes_to_generate > 0:
        yield random_number % NUM_DICEWORDS
        yield from gen_diceword_indexes(
                             int(random_number // NUM_DICEWORDS),
                             num_indexes_to_generate - 1)


def gen_dicewords_strings(dicewords_indexes: List[int],
                          dicewords_mapping: Dict[int, str]) -> Iterable[str]:
    """ a generator to lookup strings in dicewords_mapping using
    the keys found in dicewords_indexes and return those strings"""
    if dicewords_indexes:
        yield dicewords_mapping[dicewords_indexes[0]]
        yield from gen_dicewords_strings(dicewords_indexes[1:],
                              dicewords_mapping)



def gen_dicewords(path_to_dicewords_list_file: str,
                  num_words_to_generate: int) -> List[str]:
    """ Returns randomly generated list of dicewords.
    path_to_dicewords_list_file is the file path to the file containing
        the Dicewords list to use.
    num_words_to_generate is the number of Dicewords to generate for
        the passphrase, e.g., 6."""
    num_random_bytes_needed: Final[int] = \
                                 ceil(num_words_to_generate
                                      * DICEWORDS_BITS_PER_WORD
                                      / BITS_PER_BYTE)
    random_bytes: Final[bytes] = os.urandom(num_random_bytes_needed)
    random_bytes_as_int: Final[int] = int.from_bytes(random_bytes,
                                                     sys.byteorder)
    logger.debug(random_bytes_as_int)
    diceword_indexes: Final[List[int]] = [el for el in gen_diceword_indexes(
                                                     random_bytes_as_int,
                                                     num_words_to_generate
                                                 )]
    logger.debug(diceword_indexes)
    with open(path_to_dicewords_list_file, 'r') as file:
        sorted_diceword_indexes: Final[List[int]] = sorted(diceword_indexes)
        unique_dicewords: Final[Dict[int, str]] = \
        { k: v for k, v in itertools.islice(enumerate(iter(file)),
                         sorted_diceword_indexes[0],
                         sorted_diceword_indexes[-1] + 1
                                            ) if k in sorted_diceword_indexes }

    logger.debug(unique_dicewords)
    return [ el for el in gen_dicewords_strings(diceword_indexes,
                                               unique_dicewords
                                               )]
def test_1(num_words_to_generate: int) -> None:
    """Test trivial edge case: all Dicewords indexes equal to zero."""
    diceword_indexes: Final[List[int]] = [el for el in gen_diceword_indexes(
                                                     0,
                                                     num_words_to_generate
                                                 )]
    logger.debug(diceword_indexes)
    assert len(diceword_indexes) == num_words_to_generate
    for i in range(num_words_to_generate):
        assert diceword_indexes[i] == 0



def test_2() -> None:
    """ Test that the expected Diceword indexes are produced by
    the generator."""
    # Diceword indexes are derived from a large random number by unpacking
    # it as five base-6 numbers each.  Here I construct a specific large
    # number in reverse, from the base-6 numbers I am expecting to get out.
    # The big end of the number is on the left.  The generator function,
    # gen_diceword_indexes(), generates the indexes from little end to
    # big end.
    dicewords_int: Final[int] = int("000050000400003000020000100000", 6)
    logger.debug(dicewords_int)
    diceword_indexes: Final[List[int]] = [el for el in gen_diceword_indexes(
        dicewords_int,
        6
    )]
    logger.debug(diceword_indexes)
    assert len(diceword_indexes) == 6
    for k, i in enumerate(diceword_indexes):
        assert k == i

def test_3() -> None:
    """ Test getting Diceword indexes where multiple of the Diceword
    indexes are the same."""
    # Diceword indexes are derived from a large random number by unpacking
    # it as five base-6 numbers each.  Here I construct a specific large
    # number in reverse, from the base-6 numbers I am expecting to get out.
    # The big end of the number is on the left.  The generator function,
    # gen_diceword_indexes(), generates the indexes from little end to
    # big end.
    dicewords_int: Final[int] = int("000050000400004000050000100000", 6)
    logger.debug(dicewords_int)
    diceword_indexes: Final[List[int]] = [el for el in gen_diceword_indexes(
        dicewords_int,
        6
    )]
    logger.debug(diceword_indexes)
    assert len(diceword_indexes) == 6
    assert diceword_indexes[5] == 5
    assert diceword_indexes[4] == 4
    assert diceword_indexes[3] == 4
    assert diceword_indexes[2] == 5
    assert diceword_indexes[1] == 1


def test_4(path_to_dicewords_list_file: str,
         num_words_to_generate: int) -> None:
    """ Test getting all of the Dicewords from the (presumed)
    last line of the file (i.e., the last Diceword entry in a
    Dicewords file, number 7775 when counting from zero)."""
    dicewords_int: Final[int] = int(pow(pow(6,5), num_words_to_generate)) - 1
    logger.debug(dicewords_int)
    diceword_indexes: Final[List[int]] = [el for el in gen_diceword_indexes(
        dicewords_int,
        num_words_to_generate
    )]
    logger.debug(diceword_indexes)
    assert len(diceword_indexes) == num_words_to_generate

    for dw in diceword_indexes:
        assert dw == NUM_DICEWORDS - 1

    with open(path_to_dicewords_list_file, 'r') as file:
        sorted_diceword_indexes: Final[List[int]] = sorted(diceword_indexes)
        unique_dicewords: Final[Dict[int, str]] = \
        { k: v for k, v in itertools.islice(enumerate(iter(file)),
                         sorted_diceword_indexes[0],
                         sorted_diceword_indexes[-1] + 1
                                            ) if k in sorted_diceword_indexes }

    logger.debug(unique_dicewords)
    assert len(unique_dicewords) == 1



def test(path_to_dicewords_list_file: str,
         num_words_to_generate: int) -> None:
    """ Run all tests.  Print 'OK' on success;
    otherwise, an assertion will have failed or
    an exception will have been raised (and they
    are intentionally not handled)."""
    test_1(num_words_to_generate)
    test_2()
    test_3()
    test_4(path_to_dicewords_list_file, num_words_to_generate)
    print("OK")


logger = logging.getLogger(sys.argv[0])

parser: Final = argparse.ArgumentParser()
parser.add_argument("diceword_file_path",
                    help="""path the the Dicewords list""",
                    type=str)
parser.add_argument("-n", "--num_words",
                    help="""number of words to generate, between 1 and 12""",
                    type=int,
                    default=6)
parser.add_argument("-c", "--column",
                    help="column number of column containing the diceword in each line of the file",
                    type=int,
                    default=2)
parser.add_argument("--log",
                    help="""log level, e.g., DEBUG""",
                    type=str,
                    default="INFO")
parser.add_argument("--test",
                    help="""run the tests; prints 'OK' on success.""",
                    action="store_true")
args: Final = parser.parse_args()

DICEWORDS_FILE_PATH: Final[str] = args.diceword_file_path
NUM_WORDS_TO_GENERATE: Final[int] = args.num_words
# Let column numbers start with one, even though list indexes are zero based
COLUMN_NUM_OF_DICEWORD: Final[int] = args.column - 1
numeric_log_level: Final = getattr(logging, args.log.upper(), None)
if not isinstance(numeric_log_level, int):
    raise ValueError('Invalid log level %s' % args.log)
logging.basicConfig(level=numeric_log_level)
logger.debug("test logging at level DEBUG")

if NUM_WORDS_TO_GENERATE < 1 or NUM_WORDS_TO_GENERATE > 12:
    logger.error("Argument to --num_words should be a number between 1 and 12.")
elif COLUMN_NUM_OF_DICEWORD < 0:
    logger.error("Argument to --column should be a number greater than or equal to 1.")
elif args.test:
    test(DICEWORDS_FILE_PATH, NUM_WORDS_TO_GENERATE)
else:
    dicewords_lines_list: Final[List[str]] = gen_dicewords(DICEWORDS_FILE_PATH, NUM_WORDS_TO_GENERATE)
    logger.debug(dicewords_lines_list)
    print(' '.join(k.split()[COLUMN_NUM_OF_DICEWORD] for k in dicewords_lines_list))



