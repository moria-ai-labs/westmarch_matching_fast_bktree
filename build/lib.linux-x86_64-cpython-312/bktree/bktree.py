from . import _bktree_cpp # Import the C++ extension module

class BKTree:
    def __init__(self, words, distance='Levenshtein'):
        """
        Initializes the BKTree.

        The BKTree is built from the provided list of words. The query method
        will return indices corresponding to the positions in this original list.

        Args:
            words (list of str): A list of strings to build the tree from.
            distance (str): The distance metric to use.
                          Currently, only 'Levenshtein' is supported.
        """
        if not isinstance(words, list) or not all(isinstance(word, str) for word in words):
            raise TypeError("Input 'words' must be a list of strings.")

        if distance != 'Levenshtein':
            # This check could also be moved to C++ or made more extensible later
            raise ValueError("Currently, only 'Levenshtein' distance is supported.")

        self.original_corpus = list(words) # Store a copy of the original list
        self.distance_metric = distance

        # The C++ BKTreeImpl constructor will build its own internal list of unique words
        # (_corpus_words) from original_corpus and store them in order of first appearance.
        # The indices returned by its query method will refer to this internal _corpus_words.
        self._cpp_tree = _bktree_cpp.BKTreeImpl(self.original_corpus)

        # We need to map indices from the C++ tree's internal corpus
        # (which are unique words in order of first appearance)
        # back to the indices in the user's original_corpus list.
        # _map_cpp_idx_to_original_idx[cpp_corpus_idx] = original_corpus_idx
        self._map_cpp_idx_to_original_idx = []
        seen_for_mapping = {}
        for i, word in enumerate(self.original_corpus):
            if word not in seen_for_mapping:
                seen_for_mapping[word] = i # Store first original index
                self._map_cpp_idx_to_original_idx.append(i)

        # If the original_corpus is empty, _map_cpp_idx_to_original_idx will also be empty.
        # _cpp_tree will also be empty. This is fine.

    def query(self, query_words, k=1):
        """
        Queries the BKTree for the k nearest neighbors for each query word.

        Args:
            query_words (list of str): A list of query strings.
            k (int): The number of nearest neighbors to find for each query string.
                     Must be a positive integer.

        Returns:
            tuple: A tuple containing two lists:
                   dd (list of list of int): `dd[i]` contains the distances to the
                                             k nearest neighbors of `query_words[i]`.
                                             Each inner list is sorted by distance.
                   ii (list of list of int): `ii[i]` contains the indices (into the
                                             original corpus provided at construction)
                                             of the k nearest neighbors of `query_words[i]`.
                                             Each inner list is sorted corresponding to `dd[i]`.
        """
        if not isinstance(query_words, list) or not all(isinstance(word, str) for word in query_words):
            raise TypeError("Input 'query_words' must be a list of strings.")
        if not isinstance(k, int) or k < 1:
            raise ValueError("'k' must be a positive integer.")

        if not self.original_corpus: # If the tree is empty
            # Return empty results for each query word, matching scipy.spatial.KDTree behavior
            empty_distances_for_one_query = []
            empty_indices_for_one_query = []
            # Depending on k, KDTree might return NaNs or infs, and out-of-bounds indices.
            # For simplicity, let's return empty lists if k > 0 and tree is empty.
            # If k=0, it's an invalid input handled by k<1 check.
            # If k > num_items_in_tree, it returns all items. Here, 0 items.

            all_dd = [list(empty_distances_for_one_query) for _ in query_words]
            all_ii = [list(empty_indices_for_one_query) for _ in query_words]
            return all_dd, all_ii


        all_dd = []
        all_ii = []

        for query_word in query_words:
            # cpp_results is a list of (distance, cpp_corpus_idx) tuples, sorted by distance
            cpp_results = self._cpp_tree.query(query_word, k)

            current_dd = []
            current_ii = []
            for dist, cpp_idx in cpp_results:
                current_dd.append(dist)
                # Map cpp_idx back to an index in the original user-supplied corpus
                original_idx = self._map_cpp_idx_to_original_idx[cpp_idx]
                current_ii.append(original_idx)

            all_dd.append(current_dd)
            all_ii.append(current_ii)

        return all_dd, all_ii

if __name__ == '__main__':
    # Example Usage
    corpus = ["apple", "apply", "tuple", "supple", "apricot", "appeal", "appeal"] # "appeal" is duplicated
    print(f"Original Corpus: {corpus}")

    tree = BKTree(corpus, distance='Levenshtein')
    print("BKTree initialized.")
    # Expected mapping:
    # cpp_corpus: ["apple", "apply", "tuple", "supple", "apricot", "appeal"]
    # cpp_indices:   0,       1,       2,       3,         4,         5
    # original_indices:0,       1,       2,       3,         4,         5 (first "appeal")
    # self._map_cpp_idx_to_original_idx should be [0, 1, 2, 3, 4, 5]

    queries = ["appeal", "supper", "apply", "orange", "apple"]
    k_neighbors = 2
    print(f"\nQuerying for {k_neighbors} nearest neighbors for: {queries}")

    distances, indices = tree.query(queries, k=k_neighbors)

    for i, query_word in enumerate(queries):
        print(f"\nQuery: \"{query_word}\"")
        if not distances[i]:
            print("  No neighbors found (or tree was empty).")
        for j in range(len(distances[i])):
            neighbor_original_idx = indices[i][j]
            dist = distances[i][j]
            print(f"  Neighbor: \"{corpus[neighbor_original_idx]}\" (Original Index: {neighbor_original_idx}), Distance: {dist}")

    print("\n--- Testing with empty corpus ---")
    empty_tree = BKTree([])
    distances_empty, indices_empty = empty_tree.query(["test"], k=1)
    print(f"Query 'test', k=1 on empty tree: dd={distances_empty}, ii={indices_empty}")
    assert distances_empty == [[]]
    assert indices_empty == [[]]

    print("\n--- Testing with k larger than corpus size ---")
    small_corpus = ["one", "two"]
    small_tree = BKTree(small_corpus)
    distances_small, indices_small = small_tree.query(["three"], k=5)
    print(f"Query 'three', k=5 on corpus {small_corpus}:")
    for j in range(len(distances_small[0])):
        print(f"  Neighbor: \"{small_corpus[indices_small[0][j]]}\", Dist: {distances_small[0][j]}, Idx: {indices_small[0][j]}")
    # Expected: should return all items in sorted order of distance.
    # For "three": "one" (dist 2), "two" (dist 3)
    assert distances_small[0] == [2, 3] or distances_small[0] == [2,3] # Order can vary for same distance
    assert set(indices_small[0]) == {0, 1}


    print("\n--- Testing with duplicate word in corpus, query for it ---")
    # corpus = ["apple", "apply", "tuple", "supple", "apricot", "appeal", "appeal"]
    # original_corpus_indices for "appeal" are 5 and 6.
    # C++ internal corpus will have "appeal" at index 5, mapped to original index 5.
    tree_with_dupes = BKTree(corpus)
    distances_dupe, indices_dupe = tree_with_dupes.query(["appeal"], k=3)
    # Expect: "appeal" (original idx 5, dist 0), then "apple" (original idx 0, dist 1)
    print(f"Query 'appeal', k=3 on corpus with duplicates: dd={distances_dupe[0]}, ii={indices_dupe[0]}")
    assert distances_dupe[0][0] == 0
    assert indices_dupe[0][0] == 5 # Should be the first occurrence
    if len(distances_dupe[0]) > 1:
        assert distances_dupe[0][1] == 1 # "apple"
        assert indices_dupe[0][1] == 0   # "apple"

    print("\nAll basic Python wrapper tests seem to pass based on example run.")
