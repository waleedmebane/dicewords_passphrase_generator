# dicewords_passphrase_generator

You don't need to use this script (or any like it) to generate Diceword passphrases; you can do it manually with real six-sided dice.
You can use this script if you need to generate passphrases automatically or need to generate several passphrases quickly or if you temporarily find yourself without dice.

You will need a Dicewords list, which you can find at:  <br />
https://theworld/~reinhold/diceware.html OR  <br />
https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases

The script expects the list of words to start on the first line of the file.  So, remove the PGP header and empty line(s) from the top of your Dicewords list before using it with this script, such that the first line contains the first word of the list.

This script uses os.urandom() to generate the random number representing the die rolls.  Ensure that is sufficient for your security needs; otherwise, you can modify the code to use a random number generator that you prefer.

In his FAQ at his Diceware website, Arnold Reinhold recommends using a Dicewords list that is a whole power of 2 if using a computer to generate the passphrase.  This script expects a word list of 7776 (6^5) words.  Extra words would not be used.  You must modify the code if you want it to take advantage of longer word lists.

Requirements:
Python 3 version >= 3.6
(Tested with Python version 3.7.4.)

License:
BSD 3-Clause license found in the LICENSE file
