# pyglucose

[![Build Status (Travis-CI)](https://secure.travis-ci.org/msakai/glucose-pybind11.png?branch=master)](http://travis-ci.org/msakai/glucose-pybind11)
[![Build status (AppVeyor)](https://ci.appveyor.com/api/projects/status/c3dve9477wgs49c1?svg=true)](https://ci.appveyor.com/project/msakai/glucose-pybind11)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[pybind11](https://github.com/pybind/pybind11)-based binding of [glucose SAT solver](http://www.labri.fr/perso/lsimon/glucose/).

## Installation

```
pip install git+https://github.com/msakai/glucose-pybind11/
```

## Basic Usage

The `pyglucose` module exports `Solver` and `Lit`.

A SAT problem can be solved as follows:

1. Construct a solver instance using `solver = Solver()`.
2. Allocate variables using `var = solver.new_var()`.
   A variable is returned as integer value and can be converted to `Lit` by `Lit(var)`.
   A literal `lit` can be negated as `~lit`.
3. Add clauses using `solver.add_clause(clause)`. A clause is represented as `Iterable[Lit]`.
4. Solve the problem using `solver.solve()`
5. If `solver.okay` property is `True` then the problem is `SATISFIABLE`, and
   satisfying assignment can be retrieved using `solver.model` property.
   Otherwise, the problem is `UNSATISFIABLE`.
   
## License

[MIT License](LICENSE)
