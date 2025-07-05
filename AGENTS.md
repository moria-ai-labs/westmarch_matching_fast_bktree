This file provides instructions for AI agents working on this codebase.

## General Guidelines
- Follow standard Python (PEP 8) and C++ coding conventions.
- Ensure all Python code is well-documented with docstrings (Google style).
- Ensure all C++ code is well-commented.
- Add unit tests for new functionality and ensure all tests pass before submitting.

## Build Process
- The C++ core is bound to Python using `pybind11`.
- The project is built using `setup.py`.
- To build and install locally for testing: `pip install .`
- To run tests: `python -m unittest discover -s bktree/tests` (after installation)

## BKTree Specifics
- The `BKTree` class in Python (`bktree/bktree.py`) is a wrapper around the C++ implementation.
- The C++ implementation is in `bktree/src/`.
  - `bktree.hpp` contains class and function declarations.
  - `bktree.cpp` contains class and function implementations.
  - `main.cpp` contains the `pybind11` bindings.
- The primary distance metric to implement first is Levenshtein distance.
- The `query(queries, k)` method should return two lists:
    - `dd`: A list of lists, where `dd[i]` contains the distances to the `k` nearest neighbors of `queries[i]`.
    - `ii`: A list of lists, where `ii[i]` contains the indices (from the original input corpus) of the `k` nearest neighbors of `queries[i]`. Both `dd[i]` and `ii[i]` should be sorted by distance.

## Testing
- Test cases should cover:
    - Empty input corpus.
    - Queries for words in the corpus and words not in the corpus.
    - Different values of `k`.
    - Correctness of returned distances and indices.
    - Handling of duplicate words in the input corpus (the first occurrence's index should be stored).
