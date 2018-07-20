#include <string>
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>
#include <core/Solver.h>
#include <simp/SimpSolver.h>

namespace py = pybind11;

using Glucose::lbool;
using Glucose::vec;
using Glucose::Var;
using Glucose::Lit;
using Glucose::Solver;
using Glucose::SimpSolver;

namespace pybind11 { namespace detail {
    template <> struct type_caster<lbool> {
    public:
        /**
         * This macro establishes the name 'lbool' in
         * function signatures and declares a local variable
         * 'value' of type lbool
         */
        PYBIND11_TYPE_CASTER(lbool, _("lbool"));

        /**
         * Conversion part 1 (Python->C++): convert a PyObject into a lbool
         * instance or return false upon failure. The second argument
         * indicates whether implicit conversions should be applied.
         */
        lbool load(handle src, bool) {
            /* Extract PyObject from handle */
            PyObject *source = src.ptr();
            if (source == Py_None)
                return l_Undef;
            else if (PyObject_IsTrue(source))
                return l_True;
            else
                return l_False;
        }

        /**
         * Conversion part 2 (C++ -> Python): convert an lbool instance into
         * a Python object. The second and third arguments are used to
         * indicate the return value policy and parent object (for
         * ``return_value_policy::reference_internal``) and are generally
         * ignored by implicit casters.
         */
        static handle cast(lbool src, return_value_policy /* policy */, handle /* parent */) {
            if (src == l_True) {
                Py_RETURN_TRUE;
            } else if (src == l_False) {
                Py_RETURN_FALSE;
            } else {
                assert(src == l_Undef);
                Py_RETURN_NONE;
            }
        }
    };
}} // namespace pybind11::detail


PYBIND11_MODULE(pyglucose, m) {
    m.doc() = "pybind11 example plugin";
    // m.def("add", &add, "A function which adds tow numbers");

    auto Lit_class = py::class_<Lit>(m, "Lit")
      .def(py::init(&Glucose::mkLit), py::arg("var"), py::arg("sign") = false)
      .def("__str__", [](Lit &lit) {
          return std::string("Lit(") + std::to_string(Glucose::var(lit)) + "," +
	    (Glucose::sign(lit) ? "True" : "False") + ")";
       })
      .def_property_readonly("sign", &Glucose::sign)
      .def_property_readonly("var", &Glucose::var)
      .def(py::self == py::self)
      .def(py::self != py::self)
      .def(~py::self)
      .def(py::self ^ bool())
      .def_property_readonly_static("Undef", [](py::object /* self */) { return Glucose::lit_Undef; })
      .def_property_readonly_static("Error", [](py::object /* self */) { return Glucose::lit_Error; });

    auto Solver_class = py::class_<Solver>(m, "Solver")
      .def(py::init<>())
      .def("clone", &Solver::clone)
      .def("__copy__", &Solver::clone)
      .def("__deepcopy__", [](Solver &solver, py::object memo) { return solver.clone(); })

      // Problem specification:
      .def("new_var", &Solver::newVar, py::arg("polarity") = true, py::arg("dvar") = true)
      .def("add_clause", [](Solver &solver, py::iterable ps) {
          vec<Lit> ls;
          for (auto p : ps)
              ls.push(p.cast<Lit>());
          return solver.addClause(ls);
        })
      .def("add_empty_clause", &Solver::addEmptyClause)

      // Solving
      .def("simplify", &Solver::simplify)
      .def("solve",
        [](Solver &solver, py::iterable assumps) {
          vec<Lit> ls;
          for (auto p : assumps)
              ls.push(p.cast<Lit>());
          return solver.solve(ls);
        },
        py::call_guard<py::gil_scoped_release>())
      .def("solve_limited",
        [](Solver &solver, py::iterable assumps) {
          vec<Lit> ls;
          for (auto p : assumps)
              ls.push(p.cast<Lit>());
          return solver.solveLimited(ls);
        },
        py::call_guard<py::gil_scoped_release>())
      .def("solve", py::overload_cast<>(&Solver::solve), py::call_guard<py::gil_scoped_release>())
      .def_property_readonly("okay", &Solver::okay)

      // Convenience versions of 'toDimacs()'
      .def("to_dimacs", py::overload_cast<const char*>(&Solver::toDimacs))

      // Display clauses and literals

      // Variable mode:

      // Read state:
      .def("value", py::overload_cast<Var>(&Solver::value, py::const_))
      .def("value", py::overload_cast<Lit>(&Solver::value, py::const_))
      .def("model_value", py::overload_cast<Var>(&Solver::modelValue, py::const_))
      .def("model_value", py::overload_cast<Lit>(&Solver::modelValue, py::const_))
      .def_property_readonly("nassigns", &Solver::nAssigns)
      .def_property_readonly("nclauses", &Solver::nClauses)
      .def_property_readonly("nlearnts", &Solver::nLearnts)
      .def_property_readonly("nvars", &Solver::nVars)
      .def_property_readonly("nfreevars", &Solver::nFreeVars)

      // Incremental mode
      .def("set_incremental_mode", &Solver::setIncrementalMode)
      .def("init_nb_initial_vars", &Solver::initNbInitialVars)
      .def_property_readonly("is_incremental", &Solver::isIncremental)

      // Resource contraints:
      .def("set_conf_budget", &Solver::setConfBudget)
      .def("set_prop_budget", &Solver::setPropBudget)
      .def("budget_off", &Solver::budgetOff)
      .def("interrupt", &Solver::interrupt)
      .def("clear_interrupt", &Solver::clearInterrupt)

      // Memory managment:

      // Extra results: (read-only member variable)
      .def_property_readonly("model", [](Solver &solver) {
            std::vector<lbool> ret;
            for (int i = 0; i < solver.model.size(); i++)
                ret.push_back(solver.model[i]);
            return ret;
        })
      .def_property_readonly("conflict", [](Solver &solver) {
            std::vector<Lit> ret;
            for (int i = 0; i < solver.conflict.size(); i++)
                ret.push_back(solver.conflict[i]);
            return ret;
        })

      // Mode of operation:
      .def_readwrite("verbosity", &Solver::verbosity)
      .def_readwrite("verb_every_conflicts", &Solver::verbEveryConflicts)
      .def_property("show_model",
                    [](Solver &solver) { return solver.showModel; },
                    [](Solver &solver, bool flag) { solver.showModel = flag; }
                    )

      // Statistics
      /*
      .def_property_readonly("stats", [](Solver &solver) {
	    std::vector<uint64_t> ret;
	    for (int i = 0; i < solver.stats.size(); i++)
	        ret.push_back(solver.stats[i]);
	    return ret;
	})
      */
      // Important stats completely related to search. Keep here
      .def_readonly("solves", &Solver::solves)
      .def_readonly("starts", &Solver::starts)
      .def_readonly("decisions", &Solver::decisions)
      .def_readonly("propagations", &Solver::propagations)
      .def_readonly("conflicts", &Solver::conflicts)
      .def_readonly("conflictsRestarts", &Solver::conflictsRestarts)
      ;

    py::class_<SimpSolver, Solver>(m, "SimpSolver")
      .def(py::init<>());
}
