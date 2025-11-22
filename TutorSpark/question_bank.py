from __future__ import annotations

from typing import List

from models import Question

# Base CS fundamentals bank.
# IDs 1–25 match the _HINTS mapping in engine.py.
# You can extend this to 100+ questions (just keep IDs unique).

QUESTION_BANK: List[Question] = [
    Question(
        id=1,
        topic="Algorithms",
        prompt="Which algorithm uses divide-and-conquer to search a sorted list by repeatedly halving the search space?",
        options=["Linear search", "Binary search", "Depth-first search", "Breadth-first search"],
        correct_index=1,
    ),
    Question(
        id=2,
        topic="Data Structures",
        prompt="Which data structure best models customers lining up at a bank counter?",
        options=["Stack", "Queue", "Binary tree", "Hash map"],
        correct_index=1,
    ),
    Question(
        id=3,
        topic="Programming Fundamentals",
        prompt="In Python, which keyword is used to define a function?",
        options=["func", "define", "def", "fn"],
        correct_index=2,
    ),
    Question(
        id=4,
        topic="Complexity",
        prompt="Which time complexity grows slightly faster than linear but slower than quadratic?",
        options=["O(1)", "O(n)", "O(n log n)", "O(n^2)"],
        correct_index=2,
    ),
    Question(
        id=5,
        topic="Software Engineering",
        prompt="What is a primary purpose of unit tests?",
        options=[
            "To replace documentation",
            "To describe expected behavior and catch regressions",
            "To speed up the compiler",
            "To store application logs",
        ],
        correct_index=1,
    ),
    Question(
        id=6,
        topic="Version Control",
        prompt="In Git, which command records a snapshot of your changes to the local repository?",
        options=["git status", "git push", "git commit", "git reset"],
        correct_index=2,
    ),
    Question(
        id=7,
        topic="Complexity",
        prompt="Which of these time complexities grows exponentially with input size?",
        options=["O(n)", "O(n log n)", "O(2^n)", "O(n^2)"],
        correct_index=2,
    ),
    Question(
        id=8,
        topic="Data Structures",
        prompt="Which data structure is commonly compared to a stack of plates on a table?",
        options=["Queue", "Stack", "Graph", "Linked list"],
        correct_index=1,
    ),
    Question(
        id=9,
        topic="Programming Fundamentals",
        prompt="Which of these is a Boolean literal in Python?",
        options=["yes", "True", "TRUE", "1"],
        correct_index=1,
    ),
    Question(
        id=10,
        topic="OOP",
        prompt="Which OOP principle is mainly about hiding internal state and exposing a controlled interface?",
        options=["Inheritance", "Polymorphism", "Encapsulation", "Abstraction"],
        correct_index=2,
    ),
    Question(
        id=11,
        topic="Algorithms",
        prompt="Which algorithm is widely used to find the shortest path in a weighted graph without negative edges?",
        options=["Depth-first search", "Dijkstra's algorithm", "Bubble sort", "Quick sort"],
        correct_index=1,
    ),
    Question(
        id=12,
        topic="Data Structures",
        prompt="Which data structure typically offers average O(1) time complexity for lookups using keys?",
        options=["Array", "Linked list", "Hash table", "Binary search tree"],
        correct_index=2,
    ),
    Question(
        id=13,
        topic="Python",
        prompt="In Python, what is PEP 8?",
        options=[
            "A built-in debugger",
            "A style guide for Python code",
            "A package manager",
            "A testing framework",
        ],
        correct_index=1,
    ),
    Question(
        id=14,
        topic="Software Testing",
        prompt="Which type of testing focuses on the smallest testable parts of an application (like single functions or methods)?",
        options=["Integration testing", "System testing", "Unit testing", "Acceptance testing"],
        correct_index=2,
    ),
    Question(
        id=15,
        topic="Version Control",
        prompt="In Git, which command both fetches and integrates changes from a remote repository into your current branch?",
        options=["git fetch", "git pull", "git clone", "git merge"],
        correct_index=1,
    ),
    Question(
        id=16,
        topic="Algorithms",
        prompt="Which sorting algorithm is based on a divide-and-conquer strategy that splits, sorts, and then merges?",
        options=["Bubble sort", "Insertion sort", "Merge sort", "Selection sort"],
        correct_index=2,
    ),
    Question(
        id=17,
        topic="Data Structures",
        prompt="Which of the following is a self-balancing binary search tree?",
        options=["Binary heap", "AVL tree", "Hash table", "Queue"],
        correct_index=1,
    ),
    Question(
        id=18,
        topic="Complexity",
        prompt="Big-O notation is mainly used to describe:",
        options=[
            "Exact runtime in seconds",
            "Average number of bugs in code",
            "Upper bound on growth rate as input size increases",
            "Required amount of disk space",
        ],
        correct_index=2,
    ),
    Question(
        id=19,
        topic="Python",
        prompt="In Python, what does len([1, 2, 3, 4]) return?",
        options=["3", "4", "5", "An error"],
        correct_index=1,
    ),
    Question(
        id=20,
        topic="Software Design",
        prompt="Which design pattern allows selecting an algorithm's behavior at runtime by swapping strategy objects?",
        options=["Singleton", "Factory Method", "Strategy", "Observer"],
        correct_index=2,
    ),
    Question(
        id=21,
        topic="Software Engineering",
        prompt="Continuous Integration (CI) is primarily about:",
        options=[
            "Manually running tests once a year",
            "Automating builds and tests whenever code changes",
            "Deploying directly to production without tests",
            "Working without version control",
        ],
        correct_index=1,
    ),
    Question(
        id=22,
        topic="Version Control",
        prompt="In Git, what is the main purpose of a branch?",
        options=[
            "To back up the repository in the cloud",
            "To copy commits from another repository",
            "To develop features independently from the main line",
            "To store binary artifacts",
        ],
        correct_index=2,
    ),
    Question(
        id=23,
        topic="Algorithms",
        prompt="Which traversal algorithm visits a tree or graph level by level, using a queue?",
        options=["Depth-first search", "Breadth-first search", "Binary search", "Dijkstra's algorithm"],
        correct_index=1,
    ),
    Question(
        id=24,
        topic="Data Structures",
        prompt="Which data structure is most suitable for implementing a priority queue efficiently?",
        options=["Array", "Heap", "Stack", "Linked list"],
        correct_index=1,
    ),
    Question(
        id=25,
        topic="Programming Fundamentals",
        prompt="In Python, what does the '==' operator check when comparing two values?",
        options=[
            "Whether they are the same object in memory",
            "Whether they have the same value",
            "Whether both are integers",
            "Whether both are strings",
        ],
        correct_index=1,
    ),
]
