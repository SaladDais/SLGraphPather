#!/bin/bash

# Comment this out if you don't want to build the python testcases,
# or set BUILD_PYTHON_HARNESSES env var to 0.
BUILD_PYTHON_HARNESSES="${BUILD_PYTHON_HARNESSES:-1}"

shopt -s nullglob

if [ -z "${LSL_PYOPTIMIZER_PATH}" ]; then
	>&2 echo "LSL_PYOPTIMIZER_PATH environment variable must be set"
	exit 1
fi

if [[ -z "$(which cpp)" ]]; then
	>&2 echo "GNU C Preprocessor must be installed"
	exit 1
fi

if [[ -z "$(which lummao)" && "${BUILD_PYTHON_HARNESSES}" == 1 ]]; then
	>&2 echo "lummao must be installed"
	exit 1
fi

pushd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null

mkdir -p compiled
mkdir -p pythonized
rm -rf compiled/*
rm -rf pythonized/*
touch pythonized/__init__.py

for f in *."lsl"; do
	echo "$f"
	basef=$(basename "$f" ".lsl")
	compiledf="compiled/${basef}.o.lsl"
	pythonizedf="pythonized/${basef}.py"
	python "${LSL_PYOPTIMIZER_PATH}/main.py" -P "-I" -P "include" -H -O addstrings,-extendedglobalexpr -p gcpp --precmd=cpp "$f" -o "$compiledf"
	if [ "${BUILD_PYTHON_HARNESSES}" == 1 ]; then
		lummao "$compiledf" "$pythonizedf"
	fi
done

popd > /dev/null
