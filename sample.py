import re
import sys
import pyglucose

def read(fname):
    with open(fname, "r") as f:
        def read_header():
            line = f.readline()
            while line:
                if re.match(r'^c', line):
                    pass
                else:
                    m = re.match(r'^p\s+cnf\s+(\d+)\s+(\d+)\s*', line)
                    if m:
                        nv = int(m.group(1))
                        nc = int(m.group(2))
                        return (nv,nc)
                line = f.readline()
            raise RuntimeError("failed to find CNF header")

        def read_body(nc):
            cs = []
            for _ in range(nc):
                line = f.readline()
                c = [int(w) for w in line.split()]
                if c[-1] == 0:
                    c.pop()
                else:
                    raise RuntimeError("invalid line")
                cs.append(c)
            return cs

        nv, nc = read_header()
        return (nv, read_body(nc))

nv, cs = read(sys.argv[1])
solver = pyglucose.SimpSolver()
ls = {i+1: pyglucose.Lit(solver.new_var()) for i in range(nv)}
for clause in cs:
    solver.add_clause([ls[l] if l > 0 else ~ls[-l] for l in clause])
solver.verbosity = 1
solver.solve()
if solver.okay:
    print("SAT")
    print(solver.model)
else:
    print("UNSAT")
