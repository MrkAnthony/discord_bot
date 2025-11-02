"""
Total Number of Problems: 57
print(len(NEETCODE_LIST["easy"]) + len(NEETCODE_LIST["medium"]) + len(NEETCODE_LIST["hard"]))
Topic included
- Two Pointers
- Binary Search
- Tree's
- Stacks
- Array + Hashing
- Sliding Windows
- Linked List

"""
NEETCODE_LIST = {
    "easy": [
        {'name': 'Contains Duplicate', 'link': 'https://neetcode.io/problems/duplicate-integer?list=neetcode150'},
        {'name': 'Valid Anagram', 'link': 'https://neetcode.io/problems/is-anagram?list=neetcode150'},
        {'name': 'Two Sum', 'link': 'https://neetcode.io/problems/two-integer-sum?list=neetcode150'},
        {'name': 'Valid Palindrome', 'link': 'https://neetcode.io/problems/is-palindrome?list=neetcode150'},
        {'name': 'Best Time to Buy and Sell Stock',
         'link': 'https://neetcode.io/problems/buy-and-sell-crypto?list=neetcode150'},
        {'name': 'Valid Parentheses', 'link': 'https://neetcode.io/problems/validate-parentheses?list=neetcode150'},
        {'name': 'Group Anagrams', 'link': 'https://neetcode.io/problems/anagram-groups?list=neetcode150'},
        {'name': 'Binary Search', 'link': 'https://neetcode.io/problems/binary-search?list=neetcode150'},
        {'name': 'Reverse Linked List', 'link': 'https://neetcode.io/problems/reverse-a-linked-list?list=neetcode150'},
        {'name': 'Linked List Cycle Detection',
         'link': 'https://neetcode.io/problems/linked-list-cycle-detection?list=neetcode150'},
        {'name': 'Merge Two Sorted Linked Lists',
         'link': 'https://neetcode.io/problems/merge-two-sorted-linked-lists?list=neetcode150'},
        {'name': 'Invert Binary Tree', 'link': 'https://neetcode.io/problems/invert-a-binary-tree?list=neetcode150'},
        {'name': 'Maximum Depth of Binary Tree',
         'link': 'https://neetcode.io/problems/depth-of-binary-tree?list=neetcode150'},
        {'name': 'Diameter of Binary Tree',
         'link': 'https://neetcode.io/problems/binary-tree-diameter?list=neetcode150'},
        {'name': 'Balanced Binary Tree', 'link': 'https://neetcode.io/problems/balanced-binary-tree?list=neetcode150'},
        {'name': 'Same Binary Tree', 'link': 'https://neetcode.io/problems/same-binary-tree?list=neetcode150'},
        {'name': 'Subtree of Another Tree',
         'link': 'https://neetcode.io/problems/subtree-of-a-binary-tree?list=neetcode150'},

    ],
    'medium': [
        {'name': 'Group Anagrams', 'link': 'https://neetcode.io/problems/anagram-groups?list=neetcode150'},
        {'name': 'Top K Frequent Elements',
         'link': 'https://neetcode.io/problems/top-k-elements-in-list?list=neetcode150'},
        {'name': 'Encode and Decode Strings',
         'link': 'https://neetcode.io/problems/string-encode-and-decode?list=neetcode150'},
        {'name': 'Products of Array Except Self',
         'link': 'https://neetcode.io/problems/products-of-array-discluding-self?list=neetcode150'},
        {'name': 'Valid Sudoku', 'link': 'https://neetcode.io/problems/valid-sudoku?list=neetcode150'},
        {'name': 'Longest Consecutive Sequence',
         'link': 'https://neetcode.io/problems/longest-consecutive-sequence?list=neetcode150'},
        {'name': 'Two Integer Sum II', 'link': 'https://neetcode.io/problems/two-integer-sum-ii?list=neetcode150'},
        {'name': '3Sum', 'link': 'https://neetcode.io/problems/three-integer-sum?list=neetcode150'},
        {'name': 'Container With Most Water',
         'link': 'https://neetcode.io/problems/max-water-container?list=neetcode150'},
        {'name': 'Longest Substring Without Repeating Characters',
         'link': 'https://neetcode.io/problems/longest-substring-without-duplicates?list=neetcode150'},
        {'name': 'Longest Repeating Character Replacement',
         'link': 'https://neetcode.io/problems/longest-repeating-substring-with-replacement?list=neetcode150'},
        {'name': 'Permutation in String', 'link': 'https://neetcode.io/problems/permutation-string?list=neetcode150'},
        {'name': 'Minimum Stack', 'link': 'https://neetcode.io/problems/minimum-stack?list=neetcode150'},
        {'name': 'Evaluate Reverse Polish Notation',
         'link': 'https://neetcode.io/problems/evaluate-reverse-polish-notation?list=neetcode150'},
        {'name': 'Daily Temperatures', 'link': 'https://neetcode.io/problems/daily-temperatures?list=neetcode150'},
        {'name': 'Car Fleet', 'link': 'https://neetcode.io/problems/car-fleet?list=neetcode150'},
        {'name': 'Search a 2D Matrix', 'link': 'https://neetcode.io/problems/search-2d-matrix?list=neetcode150'},
        {'name': 'Koko Eating Bananas', 'link': 'https://neetcode.io/problems/eating-bananas?list=neetcode150'},
        {'name': 'Find Minimum in Rotated Sorted Array',
         'link': 'https://neetcode.io/problems/find-minimum-in-rotated-sorted-array?list=neetcode150'},
        {'name': 'Search in Rotated Sorted Array',
         'link': 'https://neetcode.io/problems/find-target-in-rotated-sorted-array?list=neetcode150'},
        {'name': 'Time Based Key-Value Store',
         'link': 'https://neetcode.io/problems/time-based-key-value-store?list=neetcode150'},
        {'name': 'Reorder Linked List', 'link': 'https://neetcode.io/problems/reorder-linked-list?list=neetcode150'},
        {'name': 'Remove Node From End of Linked List',
         'link': 'https://neetcode.io/problems/remove-node-from-end-of-linked-list?list=neetcode150'},
        {'name': 'Copy Linked List with Random Pointer',
         'link': 'https://neetcode.io/problems/copy-linked-list-with-random-pointer?list=neetcode150'},
        {'name': 'Add Two Numbers', 'link': 'https://neetcode.io/problems/add-two-numbers?list=neetcode150'},
        {'name': 'Find the Duplicate Number',
         'link': 'https://neetcode.io/problems/find-duplicate-integer?list=neetcode150'},
        {'name': 'LRU Cache', 'link': 'https://neetcode.io/problems/lru-cache?list=neetcode150'},
        {'name': 'Lowest Common Ancestor in Binary Search Tree',
         'link': 'https://neetcode.io/problems/lowest-common-ancestor-in-binary-search-tree?list=neetcode150'},
        {'name': 'Binary Tree Level Order Traversal',
         'link': 'https://neetcode.io/problems/level-order-traversal-of-binary-tree?list=neetcode150'},

    ],
    'hard': [
        {'name': 'Trapping Rain Water', 'link': 'https://neetcode.io/problems/trapping-rain-water?list=neetcode150'},
        {'name': 'Minimum Window Substring',
         'link': 'https://neetcode.io/problems/minimum-window-with-characters?list=neetcode150'},
        {'name': 'Sliding Window Maximum',
         'link': 'https://neetcode.io/problems/sliding-window-maximum?list=neetcode150'},
        {'name': 'Largest Rectangle In Histogram',
         'link': 'https://neetcode.io/problems/largest-rectangle-in-histogram?list=neetcode150'},
        {'name': 'Median of Two Sorted Arrays',
         'link': 'https://neetcode.io/problems/median-of-two-sorted-arrays?list=neetcode150'},
        {'name': 'Merge K Sorted Linked Lists',
         'link': 'https://neetcode.io/problems/merge-k-sorted-linked-lists?list=neetcode150'},
        {'name': 'Reverse Nodes in K-Group',
         'link': 'https://neetcode.io/problems/reverse-nodes-in-k-group?list=neetcode150'},
    ]
}
