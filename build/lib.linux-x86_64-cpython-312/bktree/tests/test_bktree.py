import unittest
import bktree._bktree_cpp as bk_cpp_module # Corrected import

class TestBKTreeCPP(unittest.TestCase):

    def test_levenshtein_distance_cpp(self):
        self.assertEqual(bk_cpp_module.levenshtein_distance("apple", "apply"), 1)
        self.assertEqual(bk_cpp_module.levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(bk_cpp_module.levenshtein_distance("", "abc"), 3)
        self.assertEqual(bk_cpp_module.levenshtein_distance("abc", ""), 3)
        self.assertEqual(bk_cpp_module.levenshtein_distance("abc", "abc"), 0)

    def test_bktree_impl_construction_cpp(self):
        words = ["hello", "help", "shell", "smell"]
        try:
            tree_impl = bk_cpp_module.BKTreeImpl(words)
            self.assertIsNotNone(tree_impl)
            # We can add more assertions here later, e.g., checking number of words,
            # or properties of the root node if exposed.
        except Exception as e:
            self.fail(f"BKTreeImpl construction failed: {e}")

    def test_bktree_impl_add_cpp(self):
        try:
            tree_impl = bk_cpp_module.BKTreeImpl([]) # Start with an empty tree
            self.assertIsNotNone(tree_impl)
            tree_impl.add("apple")
            tree_impl.add("apply")
            # More assertions can be added if there are methods to inspect the tree
            # For now, just ensuring 'add' doesn't crash.
        except Exception as e:
            self.fail(f"BKTreeImpl add method failed: {e}")

    def test_bktree_impl_constructor_with_empty_list_cpp(self):
        words = []
        try:
            tree_impl = bk_cpp_module.BKTreeImpl(words)
            self.assertIsNotNone(tree_impl)
            tree_impl.add("newword") # Should still be able to add words
        except Exception as e:
            self.fail(f"BKTreeImpl construction with empty list failed: {e}")


class TestBKTreePythonWrapper(unittest.TestCase):
    # Test the Python BKTree wrapper

    def test_initialization(self):
        from bktree import BKTree
        corpus = ["apple", "apply", "tuple", "supple"]
        tree = BKTree(corpus)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.original_corpus, corpus)
        self.assertEqual(tree.distance_metric, "Levenshtein")

        with self.assertRaises(TypeError):
            BKTree(None) # type: ignore
        with self.assertRaises(TypeError):
            BKTree([123, "word"]) # type: ignore
        with self.assertRaises(ValueError):
            BKTree(corpus, distance="Hamming")

    def test_empty_corpus(self):
        from bktree import BKTree
        tree = BKTree([])
        self.assertIsNotNone(tree)
        dd, ii = tree.query(["apple"], k=1)
        self.assertEqual(dd, [[]])
        self.assertEqual(ii, [[]])

        dd, ii = tree.query(["apple", "banana"], k=2)
        self.assertEqual(dd, [[], []])
        self.assertEqual(ii, [[], []])

    def test_query_simple(self):
        from bktree import BKTree
        corpus = ["apple", "apply", "apricot", "banana"]
        tree = BKTree(corpus)

        # Query for "apple"
        dd, ii = tree.query(["apple"], k=1)
        self.assertEqual(len(dd), 1)
        self.assertEqual(len(ii), 1)
        self.assertEqual(dd[0], [0]) # Distance to itself
        self.assertEqual(ii[0], [0]) # Index of "apple"

        # Query for "axply" (closest to "apply")
        dd, ii = tree.query(["axply"], k=1)
        self.assertEqual(dd[0], [1]) # Levenshtein distance("axply", "apply") = 1
        self.assertEqual(ii[0], [1]) # Index of "apply"

    def test_query_multiple_results_and_k(self):
        from bktree import BKTree
        corpus = ["book", "books", "cook", "cake", "cape"]
        # Levenshtein distances from "boon":
        # book: 1
        # books: 2
        # cook: 1
        # cake: 3
        # cape: 3
        tree = BKTree(corpus)

        # k=1, should get one of "book" or "cook"
        dd, ii = tree.query(["boon"], k=1)
        self.assertEqual(len(dd[0]), 1)
        self.assertEqual(dd[0][0], 1)
        self.assertTrue(ii[0][0] in [0, 2]) # Index of "book" or "cook"

        # k=2, should get "book" and "cook" (order might vary for same distance)
        dd, ii = tree.query(["boon"], k=2)
        self.assertEqual(len(dd[0]), 2)
        self.assertEqual(sorted(dd[0]), [1, 1])
        self.assertEqual(set(ii[0]), {0, 2}) # Indices of "book" and "cook"

        # k=3, should get "book", "cook", and "books"
        dd, ii = tree.query(["boon"], k=3)
        self.assertEqual(len(dd[0]), 3)
        self.assertEqual(sorted(dd[0]), [1, 1, 2])
        expected_indices_k3 = {0, 2, 1} # book, cook, books
        self.assertEqual(set(ii[0]), expected_indices_k3)

        # k > corpus size
        dd, ii = tree.query(["boon"], k=10)
        self.assertEqual(len(dd[0]), len(corpus))
        self.assertEqual(len(ii[0]), len(corpus))
        # Check if all original indices are present
        self.assertEqual(set(ii[0]), set(range(len(corpus))))

    def test_query_with_duplicates_in_corpus(self):
        from bktree import BKTree
        corpus = ["apple", "apply", "apple", "apricot"]
        # C++ internal unique words: "apple", "apply", "apricot"
        # C++ indices: 0 ("apple"), 1 ("apply"), 2 ("apricot")
        # Python wrapper mapping: cpp_idx_to_original_idx = [0, 1, 3]
        # (original "apple" at 0, "apply" at 1, "apricot" at 3)

        tree = BKTree(corpus)
        # Query for "apple"
        dd, ii = tree.query(["apple"], k=1)
        self.assertEqual(dd[0], [0])
        self.assertEqual(ii[0], [0]) # Should be the first "apple" at index 0

        # Query for "aple" (closest to "apple" with dist 1)
        dd, ii = tree.query(["aple"], k=1)
        self.assertEqual(dd[0], [1])
        self.assertEqual(ii[0], [0]) # Index of first "apple"

        # Query for "aply" (closest to "apply" with dist 1)
        dd, ii = tree.query(["aply"], k=1)
        self.assertEqual(dd[0], [1])
        self.assertEqual(ii[0], [1]) # Index of "apply"

    def test_multiple_query_words(self):
        from bktree import BKTree
        corpus = ["cat", "bat", "hat", "cart"]
        tree = BKTree(corpus)

        queries = ["coat", "bar"]
        # "coat": "cat" (1), "cart" (1)
        # "bar": "bat" (1)

        dd, ii = tree.query(queries, k=2)

        # Results for "coat"
        self.assertEqual(len(dd[0]), 2) # "cat", "cart"
        self.assertEqual(sorted(dd[0]), [1, 1])
        self.assertEqual(set(ii[0]), {0, 3}) # Indices of "cat", "cart"

        # Results for "bar"
        self.assertEqual(len(dd[1]), 1) # Only "bat" is close enough for k=2, or only one within dist 1
        self.assertEqual(dd[1], [1])
        self.assertEqual(ii[1], [1]) # Index of "bat"

    def test_query_word_not_in_corpus(self):
        from bktree import BKTree
        corpus = ["hello", "world"]
        tree = BKTree(corpus)
        dd, ii = tree.query(["greetings"], k=1)
        # "greetings" vs "hello" = Levenshtein dist (should be >0)
        # "greetings" vs "world" = Levenshtein dist (should be >0)
        # Example: levenshtein("greetings", "hello") is 7
        # levenshtein("greetings", "world") is 8
        self.assertEqual(dd[0], [7])
        self.assertEqual(ii[0], [0]) # Index of "hello"

    def test_query_empty_list_of_query_words(self):
        from bktree import BKTree
        corpus = ["hello", "world"]
        tree = BKTree(corpus)
        dd, ii = tree.query([], k=1)
        self.assertEqual(dd, [])
        self.assertEqual(ii, [])


if __name__ == '__main__':
    unittest.main()
