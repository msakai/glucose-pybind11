import platform
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

__version__ = '0.0.1'


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'pyglucose',
        ['pyglucose.cpp',
         'glucose-syrup-4.1/core/Solver.cc',
         'glucose-syrup-4.1/simp/SimpSolver.cc'
        ],
        include_dirs=[
            "glucose-syrup-4.1",
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True)
        ],
        define_macros=[
            ('INCREMENTAL', '1'),
            ('INCREMNENTAL', '1'),
        ],
        language='c++'
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    def build_extensions(self):
        c_opts = []
        l_opts = []

        ct = self.compiler.compiler_type
        if ct == 'unix':
            c_opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            c_opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                c_opts.append('-fvisibility=hidden')
            if sys.platform == 'darwin':
                c_opts += ['-stdlib=libc++', '-mmacosx-version-min=10.7']
                l_opts += ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        elif ct == 'msvc':
            c_opts.append('/EHsc')
            c_opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())

        for ext in self.extensions:
            ext.extra_compile_args = c_opts
            ext.extra_link_args = l_opts
        build_ext.build_extensions(self)


setup(
    name='pyglucose',
    version=__version__,
    author='Masahiro Sakai',
    author_email="masahiro.sakai@gmail.com",
    url="https://github.com/msakai/glucose-pybind11",
    license='MIT License',
    description='pybind11-based binding of glucose SAT solver',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    ext_modules=ext_modules,
    setup_requires=['pybind11>=2.2'],
    install_requires=['pybind11>=2.2'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
    test_suite='tests'
)
