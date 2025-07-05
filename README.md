# BKTree Library

A Python library for fast nearest neighbor searches for strings using a BK-Tree implemented in C++.

This library is inspired by `scipy.spatial.KDTree` and aims to provide a similar interface for string data.

## Features (Planned)

- BK-Tree data structure for efficient string querying.
- Levenshtein distance as the primary metric.
- Pythonic API for ease of use.

## Installation (Planned)

```bash
pip install .
```

## Usage (Planned)

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
