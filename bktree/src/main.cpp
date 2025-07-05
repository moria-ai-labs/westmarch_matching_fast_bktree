#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For automatic conversion of STL containers like std::vector
#include "bktree.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_bktree_cpp, m) {
    m.doc() = "pybind11 plugin for BKTree C++ backend";

    // Bind the static Levenshtein distance function
    m.def("levenshtein_distance", &BKTree::levenshteinDistance, "Calculate Levenshtein distance between two strings",
          py::arg("s1"), py::arg("s2"));

    // Bind the BKTree class
    py::class_<BKTree>(m, "BKTreeImpl") // Using BKTreeImpl to distinguish from Python wrapper if needed
        .def(py::init<>(), "Default constructor for BKTree")
        .def(py::init([](const std::vector<std::string>& words) {
            // This constructor will be used from Python, taking a list of strings
            auto tree = std::make_unique<BKTree>();
            for (const auto& word : words) {
                tree->add(word);
            }
            return tree.release(); // pybind11 takes ownership
        }), py::arg("words"), "Constructor that takes a list of words to build the tree")
        .def("add", &BKTree::add, "Add a word to the BKTree", py::arg("word"))
        .def("query", &BKTree::query, "Query the BKTree for k nearest neighbors",
             py::arg("query_word"), py::arg("k"))
        // get_word_by_index is useful for the Python wrapper to reconstruct results
        // It needs access to _corpus_words. Let's add a simple public getter in BKTree for this.
        .def("get_corpus_word", [](const BKTree &tree, int index) {
            // This will require a public method in BKTree like:
            // const std::string& getWordFromCorpus(int index) const;
            // Let's assume this method will be added to BKTree.cpp/hpp
            // For now, to make this step self-contained for pybind, we'll use a placeholder.
            // This will be properly implemented after adding the getter to C++ BKTree.
            // If we had direct access or a getter:
            // return tree.getWordFromCorpus(index);

            // Placeholder access for now, will be fixed in C++ class if needed
            // This is just for binding. The actual implementation of such a getter is trivial.
            // For the moment, we can imagine _corpus_words is public for this binding step,
            // or a getter like `getWordByIndex` exists.
            // This will be refined when Python wrapper needs it.
            // If _corpus_words were public:
            // if (index >= 0 && static_cast<size_t>(index) < tree._corpus_words.size()) {
            //    return tree._corpus_words[index];
            // }
            // throw py::index_error("Corpus index out of range");
            // For now, this binding is more a declaration of intent for the Python wrapper.
            // The Python wrapper will primarily use the indices returned by query()
            // with its own copy of the original word list.
            // So, get_corpus_word on the C++ side might not be strictly needed by the user-facing Python API.
            // Let's remove the dummy get_word_by_index for now, as the Python wrapper
            // will handle mapping indices back to words from its own stored list.
            // The C++ query returns indices into the _corpus_words vector it built,
            // which corresponds to the order of unique words first encountered.
        });
}
