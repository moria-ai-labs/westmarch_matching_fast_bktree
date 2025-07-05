#include "bktree.hpp"
#include <algorithm> // For std::min, std::reverse
#include <iostream>  // For potential debugging
#include <vector>
#include <string>
#include <map>
#include <queue>     // For std::priority_queue
#include <limits>    // For std::numeric_limits

// BKTree method implementations

BKTree::BKTree() : root(nullptr) {}

BKTree::~BKTree() {
    // The use of std::unique_ptr for root and children handles memory automatically.
    // If manual cleanup was needed (e.g., for raw pointers in BKNode children),
    // a recursive deletion function would be called here on root.
    // For now, unique_ptr should suffice.
}

// Recursive helper for destructor if not using unique_ptr for children or needing custom logic
// void BKTree::delete_nodes(BKNode* node) {
//     if (!node) return;
//     for (auto& pair : node->children) {
//         delete_nodes(pair.second); // Recursively delete children
//     }
//     delete node; // Delete the node itself
// }


void BKTree::add(const std::string& word) {
    // Check if word already exists in our corpus.
    // If we want to only store unique words and reuse their indices:
    auto it_word = std::find(_corpus_words.begin(), _corpus_words.end(), word);
    int word_idx;

    if (it_word == _corpus_words.end()) {
        _corpus_words.push_back(word);
        word_idx = _corpus_words.size() - 1;
    } else {
        // Word already exists, get its index.
        // Depending on requirements, we might not add duplicates to the tree structure itself,
        // or handle them in a specific way. For now, we assume each 'add' call
        // tries to place the word, but uses the index of its first occurrence.
        word_idx = std::distance(_corpus_words.begin(), it_word);
        // Optional: If a word is added multiple times, we might choose to not re-add it to the tree structure.
        // However, the BK-tree structure can handle "duplicate" structural additions if they end up in different
        // branches due to edit distances from their respective parents.
        // For simplicity, we'll use the word_idx. If the exact same string is added,
        // its path from the root should be identical if the tree is deterministic.
    }


    if (!root) {
        root = std::make_unique<BKNode>(word_idx);
        return;
    }

    BKNode* current_node = root.get();
    while (true) {
        const std::string& node_word = _corpus_words[current_node->word_idx];
        int dist = levenshteinDistance(word, node_word);

        if (dist == 0) { // Word is identical to the current node's word
            return; // Word already in tree at this exact node position
        }

        auto it = current_node->children.find(dist);
        if (it == current_node->children.end()) {
            // No child at this distance, add new node here
            current_node->children[dist] = std::make_unique<BKNode>(word_idx);
            return;
        } else {
            // Move to the child node
            current_node = it->second.get();
        }
    }
}

void BKTree::query_recursive(const BKNode* node, const std::string& query_word, int k,
                               std::priority_queue<std::pair<int, int>>& results,
                               int& max_dist_in_results) const {
    if (!node) {
        return;
    }

    const std::string& node_word = _corpus_words[node->word_idx];
    int dist = levenshteinDistance(query_word, node_word);

    if (results.size() < static_cast<size_t>(k)) {
        results.push({dist, node->word_idx});
        if (results.size() == static_cast<size_t>(k)) { // Queue just became full
            max_dist_in_results = results.top().first;
        }
    } else { // Queue is full (results.size() == k)
        // Note: max_dist_in_results should be results.top().first at this point.
        if (dist < max_dist_in_results) { // Strictly better
            results.pop();
            results.push({dist, node->word_idx});
            max_dist_in_results = results.top().first;
        } else if (dist == max_dist_in_results) { // Tie for the k-th position
            // Replace to allow different items with the same k-th distance.
            results.pop();
            results.push({dist, node->word_idx});
            // max_dist_in_results is still 'dist', no change needed to its value.
        }
        // If dist > max_dist_in_results, do nothing.
    }

    // Explore children within the range [dist - max_dist_in_results, dist + max_dist_in_results]
    for (const auto& pair : node->children) {
        int edge_dist = pair.first;
        const BKNode* child_node = pair.second.get();
        if (edge_dist >= dist - max_dist_in_results && edge_dist <= dist + max_dist_in_results) {
            query_recursive(child_node, query_word, k, results, max_dist_in_results);
        }
    }
}


std::vector<std::pair<int, int>> BKTree::query(const std::string& query_word, int k) const {
    std::vector<std::pair<int, int>> final_results;
    if (!root || k <= 0) {
        return final_results;
    }

    // Max-priority queue to store {distance, word_index}
    // Stores the k best matches found so far. The top element is the one with largest distance.
    std::priority_queue<std::pair<int, int>> results_pq;

    // Initially, any distance is acceptable.
    // This will be updated to results_pq.top().first once k elements are in the queue.
    int max_dist_in_results = std::numeric_limits<int>::max();

    query_recursive(root.get(), query_word, k, results_pq, max_dist_in_results);

    // Extract results from priority queue (they will be in reverse order of distance)
    while (!results_pq.empty()) {
        final_results.push_back(results_pq.top());
        results_pq.pop();
    }
    // Results are (distance, index). Sort by distance (first element of pair).
    // Priority queue extracts largest first, so reverse to get smallest first.
    std::reverse(final_results.begin(), final_results.end());

    return final_results;
}


// Implementation of Levenshtein distance
// It's a static method, so it doesn't use 'this' pointer
int BKTree::levenshteinDistance(const std::string& s1, const std::string& s2) {
    const std::size_t len1 = s1.size(), len2 = s2.size();

    // Create a 2D vector to store distances
    std::vector<std::vector<int>> d(len1 + 1, std::vector<int>(len2 + 1));

    // Initialize the distance matrix
    // The distance of any first string to an empty second string
    // is the number of operations to delete all characters of the first string
    for (std::size_t i = 0; i <= len1; ++i) {
        d[i][0] = i;
    }

    // The distance of any second string to an empty first string
    // is the number of operations to delete all characters of the second string
    for (std::size_t j = 0; j <= len2; ++j) {
        d[0][j] = j;
    }

    // Fill the matrix
    for (std::size_t i = 1; i <= len1; ++i) {
        for (std::size_t j = 1; j <= len2; ++j) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1; // Cost is 0 if characters are same, 1 otherwise

            d[i][j] = std::min({
                d[i - 1][j] + 1,        // Deletion from s1
                d[i][j - 1] + 1,        // Insertion into s1
                d[i - 1][j - 1] + cost  // Substitution/match
            });
        }
    }

    return d[len1][len2]; // The Levenshtein distance is the value in the bottom right corner
}
