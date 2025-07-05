import time
import random
import string
# Will import bktree.BKTree later when benchmarking it

# --- Pure Python BK-Tree Implementation ---

def levenshtein_distance_py(s1, s2):
    """
    Calculates the Levenshtein distance between two strings (pure Python).
    """
    if len(s1) < len(s2):
        return levenshtein_distance_py(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

# --- Placeholder for Python BK-Tree components (to be implemented next) ---
class BKNodePy:
    def __init__(self, word, word_idx):
        self.word = word
        self.word_idx = word_idx # Index in the original corpus (of unique words for this tree)
        self.children = {}  # distance -> BKNodePy

class BKTreePy:
    def __init__(self, words, distance_func=levenshtein_distance_py):
        self.root = None
        self.distance_func = distance_func
        self.original_words_ref = words # Keep reference to original list for final index mapping

        # For Python version, we need to build its internal corpus of unique words
        # and a mapping from its internal indices to the original user-provided list's indices.
        self._internal_corpus = [] # Stores unique words for this Python BK-Tree
        self._internal_to_original_idx_map = [] # Maps index in _internal_corpus to index in original_words_ref

        seen_words_for_internal_corpus = {}
        for i, word_from_user_list in enumerate(words):
            if word_from_user_list not in seen_words_for_internal_corpus:
                seen_words_for_internal_corpus[word_from_user_list] = len(self._internal_corpus)
                self._internal_corpus.append(word_from_user_list)
                self._internal_to_original_idx_map.append(i) # Store original index of first occurrence

        # Add words from the unique internal_corpus to the tree structure
        for internal_idx, word_to_add in enumerate(self._internal_corpus):
            self._add_to_tree_structure(word_to_add, internal_idx)

    def _add_to_tree_structure(self, word, internal_idx): # internal_idx refers to self._internal_corpus
        if self.root is None:
            self.root = BKNodePy(word, internal_idx)
            return

        current_node = self.root
        while True:
            dist = self.distance_func(word, current_node.word)
            if dist == 0: # Word is identical to current node's word
                return

            if dist not in current_node.children:
                current_node.children[dist] = BKNodePy(word, internal_idx)
                return
            else:
                current_node = current_node.children[dist]

    def _query_recursive(self, node, query_word, k, results_pq, max_dist_in_results_ref):
        if node is None:
            return

        dist = self.distance_func(query_word, node.word)
        current_max_dist = max_dist_in_results_ref[0]

        if len(results_pq) < k:
            heapq.heappush(results_pq, (-dist, node.word_idx)) # Use negative dist for max-heap behavior
            if len(results_pq) == k:
                max_dist_in_results_ref[0] = -results_pq[0][0] # Update current_max_dist
        elif dist < current_max_dist:
            heapq.heapreplace(results_pq, (-dist, node.word_idx)) # Pop smallest (largest neg) and push new
            max_dist_in_results_ref[0] = -results_pq[0][0]
        elif dist == current_max_dist: # Tie for the k-th spot
             heapq.heapreplace(results_pq, (-dist, node.word_idx))
             # max_dist_in_results_ref[0] remains 'dist'

        for edge_d, child_node in node.children.items():
            # Update current_max_dist for pruning based on the most up-to-date results_pq
            if len(results_pq) == k:
                 current_max_dist_for_pruning = -results_pq[0][0]
            else:
                 current_max_dist_for_pruning = float('inf')

            # Pruning condition: explore child if its edge distance 'edge_d' is within the range
            # [dist_to_current_node - tolerance, dist_to_current_node + tolerance]
            # where tolerance is current_max_dist_for_pruning (the k-th best distance found so far).
            if edge_d >= dist - current_max_dist_for_pruning and \
               edge_d <= dist + current_max_dist_for_pruning:
                 self._query_recursive(child_node, query_word, k, results_pq, max_dist_in_results_ref)

    def query(self, query_word, k=1):
        """
        Queries the Python BKTree for k nearest neighbors.
        Returns a list of (distance, original_corpus_index) tuples.
        """
        if self.root is None or k == 0:
            return []

        # results_pq is a min-heap of (-distance, internal_word_idx) to simulate a max-heap of distances
        results_pq = []
        # max_dist_in_results_ref is a list with one element to pass by reference effectively
        max_dist_in_results_ref = [float('inf')]

        self._query_recursive(self.root, query_word, k, results_pq, max_dist_in_results_ref)

        # Extract and sort results
        # Convert from (-distance, internal_idx) to (distance, original_idx)
        final_results = []
        while results_pq:
            neg_dist, internal_idx = heapq.heappop(results_pq)
            original_idx = self._internal_to_original_idx_map[internal_idx]
            final_results.append((-neg_dist, original_idx))

        final_results.reverse() # Heap pop gives smallest (-dist) first, so largest dist. Reverse for smallest dist first.
        return final_results


# --- Benchmarking Logic (to be implemented later) ---
import heapq # For Python BKTree query
def generate_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def run_benchmark():
    print("Setting up benchmark...")
    # Parameters
    corpus_size = 1000
    query_size = 100
    word_length_min = 5
    word_length_max = 10
    k_neighbors = 5

    # Generate corpus
    # print(f"Generating corpus of {corpus_size} words...")
    # corpus = [generate_random_string(random.randint(word_length_min, word_length_max)) for _ in range(corpus_size)]
    # query_words = [generate_random_string(random.randint(word_length_min, word_length_max)) for _ in range(query_size)]

    # --- Configuration ---
    USE_RANDOM_CORPUS = False # Set to True for larger, random corpus
    corpus_size = 1000
    query_size = 100
    word_length_min = 5
    word_length_max = 10
    k_neighbors = 3


    if USE_RANDOM_CORPUS:
        print(f"Generating random corpus of {corpus_size} words and {query_size} query words...")
        corpus = list(set([generate_random_string(random.randint(word_length_min, word_length_max)) for _ in range(corpus_size)]))
        query_words = [generate_random_string(random.randint(word_length_min, word_length_max)) for _ in range(query_size)]
        corpus_size = len(corpus) # Update actual corpus size after set conversion
    else:
        print("Using fixed small corpus for benchmark.")
        corpus = ["apple", "apply", "appeal", "apricot", "banana", "bandana",
                  "orange", "oracle", "book", "books", "boon", "cook", "cake",
                  "hello", "help", "hell", "shell", "smell", "fell", "tell", "yell"]
        query_words = ["appel", "bandanna", "booking", "cooky", "shill", "hellos", "apply", "cake"]
        corpus_size = len(corpus)
        query_size = len(query_words)

    print(f"Actual Corpus size: {corpus_size}, Query words: {query_size}, k: {k_neighbors}")

    # --- Test Levenshtein ---
    print("\n--- Testing Levenshtein implementations ---")
    s1, s2 = "kitten", "sitting"
    dist_py = levenshtein_distance_py(s1, s2)
    print(f"Python Levenshtein ('{s1}', '{s2}'): {dist_py}")

    try:
        from bktree import _bktree_cpp
        dist_cpp = _bktree_cpp.levenshtein_distance(s1, s2)
        print(f"C++ Levenshtein ('{s1}', '{s2}'): {dist_cpp}")
        assert dist_py == dist_cpp
    except ImportError:
        print("C++ BKTree module not available for Levenshtein comparison.")
        _bktree_cpp = None # Ensure it's defined for later checks

    # --- Pure Python BKTree Benchmark ---
    print("\nBenchmarking Pure Python BKTree:")

    # Construction
    start_time = time.time()
    py_tree = BKTreePy(corpus, distance_func=levenshtein_distance_py)
    py_construction_time = time.time() - start_time
    print(f"  Python BKTree construction time: {py_construction_time:.6f} seconds")

    # Querying
    start_time = time.time()
    py_results_all = []
    for qw in query_words:
        py_results_all.append(py_tree.query(qw, k=k_neighbors))
    py_query_time = time.time() - start_time
    print(f"  Python BKTree query time ({query_size} queries): {py_query_time:.6f} seconds")


    # --- C++ Accelerated BKTree Benchmark ---
    if _bktree_cpp: # Check if C++ module was imported successfully earlier
        try:
            from bktree import BKTree as CPPBKTree
            print("\nBenchmarking C++ Accelerated BKTree:")

            # Construction
            start_time = time.time()
            cpp_tree = CPPBKTree(corpus) # Uses C++ Levenshtein internally
            cpp_construction_time = time.time() - start_time
            print(f"  C++ BKTree construction time: {cpp_construction_time:.6f} seconds")

            # Querying
            start_time = time.time()
            cpp_dd_all, cpp_ii_all = cpp_tree.query(query_words, k=k_neighbors)
            cpp_query_time = time.time() - start_time
            print(f"  C++ BKTree query time ({query_size} queries): {cpp_query_time:.6f} seconds")

            # Optional: Compare results for one query word if Python query is fully implemented
            # For now, Python query is a placeholder.
            # print("\nExample query results (C++):")
            # for i, qw in enumerate(query_words[:1]):
            #     print(f"  Query: {qw}")
            #     for j in range(len(cpp_dd_all[i])):
            #         print(f"    Dist: {cpp_dd_all[i][j]}, Index: {cpp_ii_all[i][j]} (Word: {corpus[cpp_ii_all[i][j]]})")

            # print("\nExample query results (Python - placeholder):")
            # for i, qw in enumerate(query_words[:1]):
            #     print(f"  Query: {qw}")
            #     for dist, original_idx in py_results_all[i]:
            #          print(f"    Dist: {dist}, Index: {original_idx} (Word: {corpus[original_idx]})")

            # --- Result Comparison (for validation) ---
            print("\n--- Comparing query results for first few queries (for validation) ---")
            max_queries_to_compare = min(5, query_size)
            for i in range(max_queries_to_compare):
                qw = query_words[i]
                print(f"  Query: \"{qw}\"")

                py_res_tuples = sorted(py_results_all[i]) # list of (dist, original_idx)

                cpp_res_tuples = sorted(list(zip(cpp_dd_all[i], cpp_ii_all[i])))

                print(f"    Python BKTreePy: {py_res_tuples}")
                print(f"    C++ BKTree:    {cpp_res_tuples}")

                # Basic check: compare number of results and first result if available
                if len(py_res_tuples) != len(cpp_res_tuples):
                    print(f"    WARN: Different number of results! Py: {len(py_res_tuples)}, Cpp: {len(cpp_res_tuples)}")
                elif py_res_tuples and cpp_res_tuples and py_res_tuples != cpp_res_tuples:
                     # Sort by distance then index for stable comparison if multiple items have same distance
                    if py_res_tuples == cpp_res_tuples:
                         print("    Results match (after sorting).")
                    else:
                         print("    WARN: Results differ!")
                elif not py_res_tuples and not cpp_res_tuples:
                    print("    Results match (both empty).")
                else: # One is empty, other is not (already caught by len check) or both non-empty and match
                    print("    Results match.")


        except ImportError:
            print("C++ Accelerated BKTree (bktree.BKTree) not available for benchmarking.")
        except Exception as e:
            print(f"Error during C++ BKTree benchmark: {e}")
    else:
        print("\nSkipping C++ Accelerated BKTree benchmark as module was not imported.")

if __name__ == "__main__":
    run_benchmark()
