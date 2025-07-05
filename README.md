# BKTree Library

A Python library for fast nearest neighbor searches for strings using a BK-Tree implemented in C++.

This library is inspired by `scipy.spatial.KDTree` and aims to provide a similar interface for string data.

## Features (Planned)

- BK-Tree data structure for efficient string querying.
- Levenshtein distance as the primary metric.
- Pythonic API for ease of use.

## Prerequisites

- A C++14 compatible compiler (e.g., GCC, Clang, MSVC).
- Python 3.6+ and Pip.
- `pybind11` (will be installed automatically as a dependency if not present).

## Installation

To use this library, you can install it directly from the source code.

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd bktree
    ```
    (Or, if you just have the source code, navigate to the root directory where `setup.py` is located.)

2.  **Standard Installation:**
    For most use cases, a standard installation is recommended. This will compile the C++ extension and install the package into your Python environment's `site-packages` directory.
    ```bash
    pip install .
    ```

3.  **Editable (Development) Installation:**
    If you are planning to modify the Python source code of this library and want your changes to be immediately reflected without reinstalling, you can use an editable install:
    ```bash
    pip install -e .
    ```
    **Note:** If you modify the C++ source files (`.cpp`, `.hpp`), you will need to re-run `pip install -e .` (or `pip install .`) to recompile the C++ extension. Changes to Python files will be live immediately.

    Using a virtual environment is highly recommended for development:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .
    ```

## Usage

```python
from bktree import BKTree

corpus = ["apple", "apply", "tuple", "supple", "apricot", "appeal"]
tree = BKTree(corpus, distance='Levenshtein')

queries = ["appeal", "supper", "apply"]
distances, indices = tree.query(queries, k=2)

for i, query_word in enumerate(queries):
    print(f"Query: {query_word}")
    for j in range(len(distances[i])):
        neighbor_idx = indices[i][j]
        neighbor_word = corpus[neighbor_idx]
        dist = distances[i][j]
        print(f"  Neighbor: {neighbor_word} (Index: {neighbor_idx}), Distance: {dist}")
```
