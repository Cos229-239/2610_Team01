import os
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# Force 64-bit target architecture environment variables on Windows
os.environ["TARGET_ARCH"] = "x64"
os.environ["VSCMD_ARG_TGT_ARCH"] = "x64"

ext_modules = [
    Pybind11Extension(
        "sim_engine",
        ["sim_engine.cpp"],
    ),
]

setup(
    name="sim_engine",
    version="1.0.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)