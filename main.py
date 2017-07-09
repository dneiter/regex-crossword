#!/usr/bin/env python

import sys

from regex import Regex
from regex_crossword import RegexCrossword

def display_hexagon(arr):
    n = len(arr[0])
    for y in range(2 * n - 1):
        line = " ".join(arr[y])
        padding = max(n - 1 - y, y - n + 1)
        print (' ' * padding) + line
                 
def main():        
    x_regexes = [
        '.*H.*H.*',
        '(DI|NS|TH|OM)*',
        'F.*[AO].*[AO].*',
        '(O|RHH|MM)*',
        '.*',
        'C*MC(CCC|MM)*',
        '[^C]*[^R]*III.*',
        '(...?)\\1*',
        '([^X]|XCC)*',
        '(RR|HHH)*.?',
        'N.*X.X.X.*E',
        'R*D*M*',
        '.(C|HH)*',
    ]

    y_regexes = [
        '(ND|ET|IN)[^X]*',
        '[CHMNOR]*I[CHMNOR]*',
        'P+(..)\\1.*',
        '(E|CR|MN)*',
        '([^MC]|MM|CC)*',
        '[AM]*CM(RC)*R?',
        '.*',
        '.*PRR.*DDC.*',
        '(HHX|[^HX])*',
        '([^EMC]|EM)*',
        '.*OXR.*',
        '.*LR.*RL.*',
        '.*SE.*UE.*',
    ]

    # start with x = 0, y = max
    z_regexes = [
        '.*G.*V.*H.*',
        '[CR]*',
        '.*XEXM*',
        '.*DD.*CCM.*',
        '.*XHCR.*X.*',
        '.*(.)(.)(.)(.)\\4\\3\\2\\1.*',
        '.*(IN|SE|HI)',
        '[^C]*MMM[^C]*',
        '.*(.)C\\1X\\1.*',
        '[CEIMU]*OH[AEMOR]*',
        '(RX|[^R])*',
        '[^M]*M[^M]*',
        '(S|MM|HHH)*',
    ]

    n = 7
    x_regexes = [Regex.compile(i) for i in x_regexes]
    y_regexes = [Regex.compile(i) for i in y_regexes]
    z_regexes = [Regex.compile(i) for i in z_regexes]

    arr = RegexCrossword.solve(n, x_regexes, y_regexes, z_regexes)
    display_hexagon(arr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
