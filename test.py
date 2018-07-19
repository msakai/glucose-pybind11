import pyglucose

solver = pyglucose.Solver()
solver.set_incremental_mode()
assert solver.is_incremental == True
p = pyglucose.Lit(solver.new_var())
q = pyglucose.Lit(solver.new_var())
solver.add_clause([p,q])
solver.add_clause([p,~q])
solver.add_clause([~p,~q])
solver.solve()
assert solver.okay
m = solver.model
pv = m[p.var]
qv = m[q.var]
assert (pv or qv) and (pv or not qv) and (not pv or not qv)

solver.add_clause([~p,q])
solver.solve()
assert not solver.okay
