import copy
import unittest
import pyglucose


class TestSolver(unittest.TestCase):
    def test_sat(self) -> None:
        solver = pyglucose.Solver()
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

    def test_unsat(self) -> None:
        solver = pyglucose.Solver()
        x1 = pyglucose.Lit(solver.new_var())
        x2 = pyglucose.Lit(solver.new_var())
        x3 = pyglucose.Lit(solver.new_var())
        x4 = pyglucose.Lit(solver.new_var())
        solver.add_clause([x1])
        solver.add_clause([~x1])
        solver.add_clause([~x1, x2])
        solver.add_clause([~x2])
        solver.add_clause([~x1, x3])
        solver.add_clause([~x3])
        solver.solve()
        assert not solver.okay

    def test_incremental(self) -> None:
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

        solver.add_clause([~p,q])
        solver.solve()
        assert not solver.okay

    def test_copy(self) -> None:
        solver = pyglucose.Solver()
        solver.set_incremental_mode()

        p = pyglucose.Lit(solver.new_var())
        q = pyglucose.Lit(solver.new_var())
        solver.add_clause([p,q])
        solver.add_clause([p,~q])
        solver.add_clause([~p,~q])
        solver.solve()

        solver2 = copy.deepcopy(solver)

        solver.add_clause([~p,q])
        solver.solve()
        assert not solver.okay

        solver2.solve()
        assert solver2.okay


if __name__ == '__main__':
    unittest.main()
