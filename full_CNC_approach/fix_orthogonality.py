import re,sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional

NUM_RE = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)'
WORD_RE = re.compile(r'([A-Za-z])\s*(' + NUM_RE + r')')

COMMENT_PAREN_RE = re.compile(r'\(.*?\)')      # remove (...) blocks
COMMENT_SEMI_RE  = re.compile(r'[;#].*$')      # remove ; ... or # ... to EOL

@dataclass
class ModalState:
    units_mm: bool = True       # G21 mm, G20 inch
    abs_dist: bool = True       # G90 abs, G91 inc
    abs_ijk: Optional[bool] = None  # G90.1/G91.1 (None = controller default)
    plane: str = 'G17'          # G17 XY, G18 XZ, G19 YZ
    feed: Optional[float] = None
    spindle: Optional[float] = None
    tool: Optional[int] = None
    pos: Dict[str, float] = field(default_factory=lambda: {'X':0.0, 'Y':0.0, 'Z':0.0})

@dataclass
class GLine:
    raw: str
    stripped: str
    comment: str
    words: Dict[str, object]  # e.g. {'G':[1], 'X':10.0, 'Y':5.0}

def strip_comments(line: str):
    c1 = ''.join(COMMENT_PAREN_RE.findall(line))
    line_wo_paren = COMMENT_PAREN_RE.sub('', line)
    c2m = COMMENT_SEMI_RE.search(line_wo_paren)
    if c2m:
        return line_wo_paren[:c2m.start()], (c1 + line_wo_paren[c2m.start():]).strip()
    return line_wo_paren, c1.strip()

def parse_words(s: str) -> Dict[str, object]:
    words: Dict[str, object] = {}
    for m in WORD_RE.finditer(s):
        k = m.group(1).upper()
        v = float(m.group(2))
        if k in ('G','M'):
            words.setdefault(k, []).append(int(v))
        else:
            words[k] = v
    return words

class GCodeParser:
    def __init__(self):
        self.state = ModalState()

    def parse_line(self, raw: str) -> GLine:
        stripped0, comment = strip_comments(raw)
        stripped = stripped0.strip()
        words = parse_words(stripped)
        self._apply_modal(words)
        return GLine(raw=raw.rstrip('\n'), stripped=stripped, comment=comment, words=words)

    def _apply_modal(self, w: Dict[str, object]):
        # Units
        for g in w.get('G', []):
            if g == 20: self.state.units_mm = False
            elif g == 21: self.state.units_mm = True
            elif g == 90: self.state.abs_dist = True
            elif g == 91: self.state.abs_dist = False
            elif g == 901: self.state.abs_ijk = True   # G90.1 becomes 901 after int()
            elif g == 911: self.state.abs_ijk = False  # G91.1 -> 911
            elif g in (17,18,19): self.state.plane = f'G{g}'

        if 'F' in w: self.state.feed = float(w['F'])
        if 'S' in w: self.state.spindle = float(w['S'])
        if 'T' in w: self.state.tool = int(w['T'])

        # Track XYZ (modal distance)
        if any(k in w for k in ('X','Y','Z')):
            x = self.state.pos['X']; y = self.state.pos['Y']; z = self.state.pos['Z']
            dx = w.get('X', None); dy = w.get('Y', None); dz = w.get('Z', None)
            if self.state.abs_dist:
                if dx is not None: x = dx
                if dy is not None: y = dy
                if dz is not None: z = dz
            else:
                if dx is not None: x += dx
                if dy is not None: y += dy
                if dz is not None: z += dz
            self.state.pos.update({'X':x,'Y':y,'Z':z})

    def to_string(self, gline: GLine, precision: int = 5) -> str:
        """
        Convert a parsed GLine object back into a formatted G-code string.

        Args:
            gline: GLine instance produced by parse_line().
            precision: Number of decimal places for numeric values.

        Returns:
            String representation of the G-code line, including comment if present.
        """
        parts = []

        # Sort so that motion codes (G/M) come before coordinates, typical for readability
        # Order roughly: N, G, M, X,Y,Z,A,B,C,I,J,K,F,S,T,...
        order_hint = ['N','G','M','X','Y','Z','A','B','C','I','J','K','F','S','T']
        words = gline.words

        def fmt_num(v):
            # Avoid .00000 when it's an integer
            if abs(v - int(v)) < 10**-precision:
                return str(int(v))
            return f"{v:.{precision}f}".rstrip('0').rstrip('.')

        # Collect words by order
        for key in order_hint:
            if key in words:
                val = words[key]
                if isinstance(val, list):  # G/M may have multiple codes
                    for v in val:
                        parts.append(f"{key}{int(v)}")
                else:
                    parts.append(f"{key}{fmt_num(val)}")

        # Include any extra words not in the hint list
        for key, val in words.items():
            if key not in order_hint:
                if isinstance(val, list):
                    for v in val:
                        parts.append(f"{key}{int(v)}")
                else:
                    parts.append(f"{key}{fmt_num(val)}")

        line = " ".join(parts)

        # Reattach comment if exists
        if gline.comment:
            comment = gline.comment.strip()
            if not comment.startswith(('(', ';', '#')):
                # Default to parentheses if not originally marked
                line += f" ({comment})"
            else:
                line += f" {comment}"

        return line

def iter_gcode(lines: List[str]):
    p = GCodeParser()
    for raw in lines:
        yield p.parse_line(raw)





if "__main__" == __name__ : 

    p = GCodeParser()
    if len(sys.argv) != 4:
        print("Usage: python fix_orthogonalty.py <ypos> input.gcode output.gcode")
        sys.exit(1)
   
    flip_y_pos =float(sys.argv[1]); 
    def f_map(x,y) : 
        k = - 0.5 / 52
        y_align = flip_y_pos ; 
        dy = y - y_align ;
        dx = k * dy ;  
        new_x =  x + dx ; 
        return new_x , y ; 

    with open(sys.argv[2], 'r') as fin, open(sys.argv[3], 'w') as fout:
        for line in fin:
            w = p.parse_line(line) ; 
            if('X' in w.words) : w.words['X'],_ = f_map(p.state.pos['X'],p.state.pos['Y']) ; 
            fout.write(p.to_string(w)+'\n');
    
