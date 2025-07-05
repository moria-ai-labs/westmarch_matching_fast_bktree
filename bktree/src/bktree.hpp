#ifndef BKTREE_HPP
#define BKTREE_HPP

#include <string>
#include <vector>
#include <map>
#include <memory> // For std::unique_ptr
#include <queue>  // For std::priority_queue

class BKTree {
public:
    BKTree();
    ~BKTree(); // Destructor to free allocated memory

    // Add a word to the tree. The word is stored internally,
    // and its index in the internal storage is used in nodes.
    void add(const std::string& word);

    // Query the tree for k nearest neighbors to the query_word
    // Returns a vector of pairs (distance, word_index)
    std::vector<std::pair<int, int>> query(const std::string& query_word, int k) const;

private:
    struct BKNode {
        // std::string word; // Store word itself, or index to a central repository
        int word_idx;    // Index into the BKTree::_words vector
        std::map<int, std::unique_ptr<BKNode>> children;

        BKNode(int idx) : word_idx(idx) {}
    };

    std::unique_ptr<BKNode> root;
    std::vector<std::string> _corpus_words; // Stores all unique words added to the tree.
                                         // The index stored in BKNode refers to this vector.

    // Recursive helper for the query method
    void query_recursive(const BKNode* node, const std::string& query_word, int k,
                         std::priority_queue<std::pair<int, int>>& results,
                         int& max_dist_in_results) const;


public:
    // Made public and static for potential direct use or binding
    static int levenshteinDistance(const std::string& s1, const std::string& s2);
};

#endif // BKTREE_HPP
