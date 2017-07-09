import copy

class RegexCrossword(object):
    """
    Solve hexagonal regexp crossword
    http://also.kottke.org/misc/images/regexp-crossword.jpg
    """

    @classmethod
    def solve(cls, n, x_regexes, y_regexes, z_regexes):
        """
        the axes notation:
            * * * >  x
           * *
          *   *
         <     >
        y      z

        x regexes are matched from left to right
        y regexes are matched from up to down
        z regexes are matched from down to up         
        """
        instance = cls(n, x_regexes, y_regexes, z_regexes)
        return instance._solve()
    
    def __init__(self, n, x_regexes, y_regexes, z_regexes):
        self.n = n
        self.x_regexes = x_regexes
        self.y_regexes = y_regexes
        self.z_regexes = z_regexes
        self.arr = self.create_hexagon(n, '.')
        self.candidates = self.create_hexagon(
            self.n,
            [chr(ord('A') + i) for i in range(26)]
        )

    @classmethod
    def create_hexagon(cls, n, val):
        return [
            [val for x in range(min(n + y, 3 * n - 2 - y))]
            for y in range(2 * n - 1)
        ]

    def _check(self, x, y):
        """
        Check if regular expressions crossing (x, y) point still have potential matches
        """
        n = self.n
        # x direction
        xline = self.arr[y]
        if not self.x_regexes[y].match(xline):
            return False

        # y direction
        ypos = x + max(0, y + 1 - n)
        yline = []
        x1, y1 = ypos, 0
        while x1 >= 0 and y1 < 2 * n - 1:
            if x1 < len(self.arr[y1]):
                yline.append(self.arr[y1][x1])
            if y1 >= n - 1:
                x1 -= 1
            y1 += 1

        if not self.y_regexes[ypos].match(yline):
            return False

        # z direction
        zpos = x + max(0, n - 1 - y)
        zline = []
        x1, y1 = zpos, 2 * n - 2
        while x1 >= 0 and y1 >= 0:
            if x1 < len(self.arr[y1]):
                zline.append(self.arr[y1][x1])
            if y1 <= n - 1:
                x1 -= 1
            y1 -= 1

        if not self.z_regexes[zpos].match(zline):
            return False

        return True

    def _make_deductions(self):
        """
        Look for positions where only 1 possible character can fit and fill them in.
        This logic stops, once all remaining positions are ambiguous
        """
        
        n = self.n
        progress = True
        all_solved = True
        while progress:
            progress = False
            for y in range(2 * n - 1):
                for x in range(len(self.arr[y])):
                    if self.arr[y][x] == '.':
                        all_solved = False
                        new_candidates = []
                        for c in self.candidates[y][x]:
                            self.arr[y][x] = c
                            fits = self._check(x, y)
                            self.arr[y][x] = '.'
                            if fits:
                                new_candidates.append(c)

                        self.candidates[y][x] = new_candidates
                        if len(new_candidates) == 1:
                            progress = True
                            self.arr[y][x] = new_candidates[0]

        return all_solved

    def _backtracking_solve(self):
        n = self.n
        if self._make_deductions():
            return True

        x1, y1, cnt = -1, -1, 99
        for y in range(2 * n - 1):
            for x in range(len(self.arr[y])):
                l = len(self.candidates[y][x])
                if l == 0:      # contradiction
                    return False
                elif l > 1 and l < cnt:
                    x1, y1, cnt = x, y, l
        backup = (self.arr, self.candidates)
        options = self.candidates[y1][x1]
        for c in options:
            (self.arr, self.candidates) = copy.deepcopy(backup)
            self.arr[y1][x1] = c
            self.candidates[y1][x1] = [c]
            if self._backtracking_solve():
                return True
        return False            # no solutions found
        
    def _solve(self):
        if self._backtracking_solve():
            return self.arr
        else:
            raise Exception("No solutions exist!")
        
