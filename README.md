# regex-crossword

This program solves regular expression crossword by combination of inference and backtracking.

It is inspired by regular expression crossword puzzle from MIT Mystery Hunt 2013.

The crossword is filled iteratively by examining set of candidate characters for every cell. Candidate character is ruled out if it would make one of regular expression constraints impossible to satisfy. Once there is single acceptable candidate left, it's committed as value for the cell, and the process restarts.

Sometimes it's not possible to infer the value for a any of remaining cells in this manner. In this case, the implementation resorts to backtracking, trying different potential values for a cell with fewest alternatives.

Checking if regular expression is possible to satisfy with given subset of characters filled in relies on an uncommon feature - support for wildcards in input text. As wildcards in input are not supported by any common regex implementation, I rolled a simple implementation of my own in `regex.py`. It is based on non-deterministic finite automata with back-reference matching bolted on top.

Original puzzle: http://web.mit.edu/puzzle/www/2013/coinheist.com/rubik/a_regular_crossword/index.html

![regex crossword](http://also.kottke.org/misc/images/regexp-crossword.jpg)

