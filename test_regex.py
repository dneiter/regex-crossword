#!/usr/bin/env python

import sys 

from regex import Regex

def main():
    ###### testing code snippets (leftover from development) ######
    
    re = Regex.compile('(.)\\1')
    re.display()
    assert re.match('AA')
    assert not re.match('AB')
    print "===================================="
    
    re = Regex.compile('AA')
    re.display()
    assert not re.match('A')
    assert re.match('AA')
    assert not re.match('AAAA')
    print "===================================="

    re = Regex.compile('(O|RHH|MM)*')
    re.display()
    assert re.match('')
    assert re.match('OOOO')
    assert re.match('MMORHHO')
    assert not re.match('MMORHHH')
    assert re.match('ORHH')

    return 0

if __name__ == "__main__":
    sys.exit(main())
