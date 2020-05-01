
import pfuncs as pf 

expr = '8 * (9-7) + (-1.5) + 2**4'
r = pf.Reader(expr)
r.summarize_tokens()
r.show_parse_tree()
r.read()