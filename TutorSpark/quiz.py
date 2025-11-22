from __future__ import annotations

from typing import List

import db
from engine import AdaptiveEngine
from models import LearnerProfile, Question
from strategies import RandomStrategy


def build_question_bank() -> List[Question]:
    """
    CS fundamentals + software engineering question bank.
    25 questions total so we can scale per 'level'.
    """
    q: List[Question] = []

    q.append(Question(
        id=1,
        topic="Algorithms",
        prompt="What is the time complexity of binary search on a sorted array?",
        options=["O(n)", "O(log n)", "O(n log n)", "O(1)"],
        correct_index=1,
    ))
    q.append(Question(
        id=2,
        topic="Data Structures",
        prompt="Which data structure uses FIFO (First In, First Out) ordering?",
        options=["Stack", "Queue", "Binary Tree", "Hash Map"],
        correct_index=1,
    ))
    q.append(Question(
        id=3,
        topic="Programming Fundamentals",
        prompt="In Python, which keyword is used to define a function?",
        options=["func", "define", "def", "fn"],
        correct_index=2,
    ))
    q.append(Question(
        id=4,
        topic="Complexity",
        prompt="Which of the following is typically the fastest for large input sizes?",
        options=["O(n^2)", "O(n log n)", "O(2^n)", "O(n!)"],
        correct_index=1,
    ))
    q.append(Question(
        id=5,
        topic="Software Engineering",
        prompt="Why do we write automated tests?",
        options=[
            "To make the code harder to read",
            "To document expected behavior and catch regressions",
            "To slow down deployment",
            "To avoid using version control",
        ],
        correct_index=1,
    ))
    q.append(Question(
        id=6,
        topic="Version Control",
        prompt="What does 'git commit' do?",
        options=[
            "Downloads the latest changes from the remote",
            "Records a snapshot of your changes in the local repository",
            "Deletes all untracked files",
            "Sends your code directly to production",
        ],
        correct_index=1,
    ))
    q.append(Question(
        id=7,
        topic="Complexity",
        prompt="An algorithm that doubles its work for each extra input element is usually described as:",
        options=["O(n)", "O(log n)", "O(n^2)", "O(2^n)"],
        correct_index=3,
    ))
    q.append(Question(
        id=8,
        topic="Data Structures",
        prompt="Which data structure naturally supports LIFO (Last In, First Out)?",
        options=["Queue", "Stack", "Linked List", "Graph"],
        correct_index=1,
    ))
    q.append(Question(
        id=9,
        topic="Programming Fundamentals",
        prompt="Which of these is a Boolean value in Python?",
        options=["yes", "True", "TRUE", "1"],
        correct_index=1,
    ))
    q.append(Question(
        id=10,
        topic="Software Design",
        prompt="Which principle is about hiding internal details and exposing a clear interface?",
        options=["Encapsulation", "Recursion", "Iteration", "Memoization"],
        correct_index=0,
    ))
    q.append(Question(
        id=11,
        topic="Algorithms",
        prompt="Which algorithm is commonly used to find the shortest path in a weighted graph without negative edges?",
        options=["Depth-first search", "Dijkstra's algorithm", "Bubble sort", "Quick sort"],
        correct_index=1,
    ))
    q.append(Question(
        id=12,
        topic="Data Structures",
        prompt="A hash table on average provides which time complexity for search?",
        options=["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        correct_index=0,
    ))
    q.append(Question(
        id=13,
        topic="Programming Fundamentals",
        prompt="What does 'PEP 8' refer to in Python?",
        options=[
            "A debugging tool",
            "A style guide for Python code",
            "A type of list",
            "A built-in testing framework",
        ],
        correct_index=1,
    ))
    q.append(Question(
        id=14,
        topic="Software Engineering",
        prompt="Which testing type focuses on individual units or functions of the code?",
        options=["Integration testing", "System testing", "Unit testing", "Acceptance testing"],
        correct_index=2,
    ))
    q.append(Question(
        id=15,
        topic="Version Control",
        prompt="What does 'git pull' do?",
        options=[
            "Uploads local commits to the remote",
            "Fetches and merges changes from the remote to local",
            "Deletes the local repository",
            "Resets the repository to the initial commit",
        ],
        correct_index=1,
    ))
    q.append(Question(
        id=16,
        topic="Algorithms",
        prompt="Which sorting algorithm has an average time complexity of O(n log n)?",
        options=["Bubble sort", "Insertion sort", "Selection sort", "Merge sort"],
        correct_index=3,
    ))
    q.append(Question(
        id=17,
        topic="Data Structures",
        prompt="Which of the following is a self-balancing binary search tree?",
        options=["AVL tree", "Array", "Stack", "Queue"],
        correct_index=0,
    ))
    q.append(Question(
        id=18,
        topic="Complexity",
        prompt="Big-O notation describes:",
        options=[
            "Exact runtime in seconds",
            "Upper bound of growth rate as input size increases",
            "Number of lines of code",
            "Amount of memory on disk",
        ],
        correct_index=1,
    ))
    q.append(Question(
        id=19,
        topic="Programming Fundamentals",
        prompt="In Python, what is the result of len([1, 2, 3, 4])?",
        options=["3", "4", "5", "Error"],
        correct_index=1,
    ))
    q.append(Question(
        id=20,
        topic="Software Design",
        prompt="The Strategy pattern is mainly about:",
        options=[
            "Sharing global state between objects",
            "Selecting an algorithm's behavior at runtime",
            "Restricting object creation",
            "Providing a simplified interface to a complex system",
        ],
        correct_index=1,
    ))
    q.append(Question(
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
    ))
    q.append(Question(
        id=22,
        topic="Version Control",
        prompt="What is a 'branch' in Git?",
        options=[
            "A copy of the repository that diverges to develop features independently",
            "A backup stored in the cloud",
            "The first commit in a repo",
            "A type of test",
        ],
        correct_index=0,
    ))
    q.append(Question(
        id=23,
        topic="Algorithms",
        prompt="Which algorithm is typically used for traversing a tree level by level?",
        options=["Depth-first search", "Binary search", "Breadth-first search", "Merge sort"],
        correct_index=2,
    ))
    q.append(Question(
        id=24,
        topic="Data Structures",
        prompt="Which structure is ideal for implementing a priority queue?",
        options=["Array", "Heap", "Stack", "Linked list"],
        correct_index=1,
    ))
    q.append(Question(
        id=25,
        topic="Programming Fundamentals",
        prompt="In Python, what does '==' check for when comparing two variables?",
        options=[
            "If they are the same object in memory",
            "If they have the same value",
            "If they are both integers",
            "If they are both strings",
        ],
        correct_index=1,
    ))

    return q


def run_quiz_for_profile(profile: LearnerProfile) -> None:
    """
    Run a quiz session for the given learner profile.

    Question count scales with experience:
      - 1st quiz: 15 questions
      - 2nd quiz: 20
      - 3rd+ quiz: all available (up to 25)
    """
    question_bank = build_question_bank()
    completed = 0
    if profile.id is not None:
        completed = db.count_quiz_sessions_for_profile(profile.id)

    base_questions = 15
    extra_per_quiz = 5
    requested = base_questions + completed * extra_per_quiz
    limit = min(requested, len(question_bank))

    strategy = RandomStrategy()
    engine = AdaptiveEngine(selection_strategy=strategy)
    engine.run_quiz_session(profile, question_bank, limit=limit)
