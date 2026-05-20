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
    Question(
        id=26,
        topic="Arithmetic",
        prompt="What is 18 + 27?",
        options=["35", "45", "46", "55"],
        correct_index=1,
    ),
    Question(
        id=27,
        topic="Arithmetic",
        prompt="What is 9 x 6?",
        options=["42", "48", "54", "63"],
        correct_index=2,
    ),
    Question(
        id=28,
        topic="Fractions",
        prompt="Which fraction is equal to 0.5?",
        options=["1/4", "1/3", "1/2", "2/3"],
        correct_index=2,
    ),
    Question(
        id=29,
        topic="Geometry",
        prompt="How many sides does a hexagon have?",
        options=["5", "6", "7", "8"],
        correct_index=1,
    ),
    Question(
        id=30,
        topic="Algebra",
        prompt="If x + 4 = 10, what is x?",
        options=["4", "5", "6", "14"],
        correct_index=2,
    ),
    Question(
        id=31,
        topic="Data Literacy",
        prompt="A bar chart is most useful for comparing:",
        options=["Categories", "Chemical formulas", "Computer passwords", "Keyboard shortcuts"],
        correct_index=0,
    ),
    Question(
        id=32,
        topic="Life Science",
        prompt="Which part of a plant is mainly responsible for photosynthesis?",
        options=["Root", "Stem", "Leaf", "Flower petal"],
        correct_index=2,
    ),
    Question(
        id=33,
        topic="Earth Science",
        prompt="Which layer of Earth do people live on?",
        options=["Inner core", "Outer core", "Mantle", "Crust"],
        correct_index=3,
    ),
    Question(
        id=34,
        topic="Physical Science",
        prompt="Water freezes at what temperature on the Celsius scale?",
        options=["0 degrees", "32 degrees", "50 degrees", "100 degrees"],
        correct_index=0,
    ),
    Question(
        id=35,
        topic="Space Science",
        prompt="Which object is at the center of our solar system?",
        options=["Earth", "The Moon", "The Sun", "Mars"],
        correct_index=2,
    ),
    Question(
        id=36,
        topic="Scientific Method",
        prompt="A testable explanation in science is called a:",
        options=["Hypothesis", "Conclusion", "Measurement", "Variable"],
        correct_index=0,
    ),
    Question(
        id=37,
        topic="Physical Science",
        prompt="Which state of matter has a fixed shape and fixed volume?",
        options=["Solid", "Liquid", "Gas", "Plasma"],
        correct_index=0,
    ),
    Question(
        id=38,
        topic="U.S. History",
        prompt="Who was the first president of the United States?",
        options=["Thomas Jefferson", "George Washington", "Abraham Lincoln", "John Adams"],
        correct_index=1,
    ),
    Question(
        id=39,
        topic="World History",
        prompt="Ancient Egypt developed along which major river?",
        options=["Amazon", "Nile", "Mississippi", "Danube"],
        correct_index=1,
    ),
    Question(
        id=40,
        topic="Civics",
        prompt="In the U.S. government, which branch makes federal laws?",
        options=["Executive", "Judicial", "Legislative", "Military"],
        correct_index=2,
    ),
    Question(
        id=41,
        topic="Geography",
        prompt="Which continent is Brazil located in?",
        options=["Africa", "South America", "Europe", "Asia"],
        correct_index=1,
    ),
    Question(
        id=42,
        topic="World History",
        prompt="The Renaissance is best known as a period of renewed interest in:",
        options=["Art, science, and classical learning", "Space travel", "Modern smartphones", "Factory robotics"],
        correct_index=0,
    ),
    Question(
        id=43,
        topic="U.S. History",
        prompt="The Declaration of Independence was adopted in which year?",
        options=["1492", "1776", "1865", "1945"],
        correct_index=1,
    ),
    Question(
        id=44,
        topic="Digital Literacy",
        prompt="What is a strong password most likely to include?",
        options=["Only your first name", "A short common word", "A mix of letters, numbers, and symbols", "Your birthday only"],
        correct_index=2,
    ),
    Question(
        id=45,
        topic="Internet Safety",
        prompt="What should you do before clicking a suspicious link in an email?",
        options=["Click it quickly", "Forward it to everyone", "Check the sender and link destination", "Reply with your password"],
        correct_index=2,
    ),
    Question(
        id=46,
        topic="Hardware Basics",
        prompt="Which computer part is often called the brain of the computer?",
        options=["CPU", "Monitor", "Keyboard", "Printer"],
        correct_index=0,
    ),
    Question(
        id=47,
        topic="Software Basics",
        prompt="Which of these is an operating system?",
        options=["Python", "Windows", "HTML", "USB"],
        correct_index=1,
    ),
    Question(
        id=48,
        topic="Productivity Tools",
        prompt="Which tool is best for organizing rows and columns of data?",
        options=["Spreadsheet", "Photo editor", "Web browser", "Video player"],
        correct_index=0,
    ),
    Question(
        id=49,
        topic="Internet Safety",
        prompt="Two-factor authentication improves security by requiring:",
        options=["A second proof of identity", "A shorter password", "No login at all", "Public Wi-Fi only"],
        correct_index=0,
    ),
    Question(
        id=50,
        topic="Arithmetic",
        prompt="What is 72 divided by 8?",
        options=["6", "8", "9", "12"],
        correct_index=2,
    ),
    Question(
        id=51,
        topic="Arithmetic",
        prompt="What is 14 + 19?",
        options=["23", "31", "33", "39"],
        correct_index=2,
    ),
    Question(
        id=52,
        topic="Fractions",
        prompt="Which fraction is larger?",
        options=["1/5", "1/4", "1/8", "1/10"],
        correct_index=1,
    ),
    Question(
        id=53,
        topic="Geometry",
        prompt="A right angle measures how many degrees?",
        options=["45", "90", "120", "180"],
        correct_index=1,
    ),
    Question(
        id=54,
        topic="Algebra",
        prompt="If 3x = 15, what is x?",
        options=["3", "5", "12", "18"],
        correct_index=1,
    ),
    Question(
        id=55,
        topic="Data Literacy",
        prompt="The average of 2, 4, and 6 is:",
        options=["3", "4", "6", "12"],
        correct_index=1,
    ),
    Question(
        id=56,
        topic="Life Science",
        prompt="Which body system moves blood through the body?",
        options=["Digestive system", "Circulatory system", "Skeletal system", "Nervous system"],
        correct_index=1,
    ),
    Question(
        id=57,
        topic="Earth Science",
        prompt="Weather describes conditions in the atmosphere over:",
        options=["A short time", "Millions of years", "Only oceans", "Only mountains"],
        correct_index=0,
    ),
    Question(
        id=58,
        topic="Physical Science",
        prompt="A magnet is most likely to attract:",
        options=["Wood", "Plastic", "Iron", "Glass"],
        correct_index=2,
    ),
    Question(
        id=59,
        topic="Space Science",
        prompt="Earth takes about how long to orbit the Sun once?",
        options=["One day", "One month", "One year", "Ten years"],
        correct_index=2,
    ),
    Question(
        id=60,
        topic="Scientific Method",
        prompt="In an experiment, the variable you change on purpose is the:",
        options=["Independent variable", "Conclusion", "Control group", "Observation"],
        correct_index=0,
    ),
    Question(
        id=61,
        topic="U.S. History",
        prompt="The U.S. Constitution begins with which phrase?",
        options=["We the People", "Four score", "I have a dream", "Give me liberty"],
        correct_index=0,
    ),
    Question(
        id=62,
        topic="World History",
        prompt="The Great Wall is strongly associated with which country?",
        options=["India", "China", "Greece", "Mexico"],
        correct_index=1,
    ),
    Question(
        id=63,
        topic="Civics",
        prompt="Voting is one way citizens can:",
        options=["Participate in government", "Avoid all laws", "Skip taxes", "Replace courts"],
        correct_index=0,
    ),
    Question(
        id=64,
        topic="Geography",
        prompt="Which is the largest ocean on Earth?",
        options=["Atlantic", "Indian", "Pacific", "Arctic"],
        correct_index=2,
    ),
    Question(
        id=65,
        topic="U.S. History",
        prompt="The Civil Rights Movement worked to expand:",
        options=["Equal rights", "Ocean travel", "Space mining", "Currency printing"],
        correct_index=0,
    ),
    Question(
        id=66,
        topic="Digital Literacy",
        prompt="A file saved in the cloud is stored:",
        options=["Only on paper", "On remote internet-connected servers", "Inside a keyboard", "Only on a monitor"],
        correct_index=1,
    ),
    Question(
        id=67,
        topic="Hardware Basics",
        prompt="Which device is used to display visual output from a computer?",
        options=["Monitor", "Mouse", "Router", "Microphone"],
        correct_index=0,
    ),
    Question(
        id=68,
        topic="Software Basics",
        prompt="An app is an example of:",
        options=["Hardware", "Software", "Electricity", "A cable"],
        correct_index=1,
    ),
    Question(
        id=69,
        topic="Productivity Tools",
        prompt="Which tool is commonly used to write and format documents?",
        options=["Word processor", "Router", "Graphics card", "Power supply"],
        correct_index=0,
    ),
    Question(
        id=70,
        topic="Internet Safety",
        prompt="Phishing messages often try to make users:",
        options=["Think carefully", "Share private information", "Update good notes", "Read a textbook"],
        correct_index=1,
    ),
    Question(
        id=71,
        topic="Algorithms",
        prompt="An algorithm is best described as:",
        options=["A random guess", "A step-by-step procedure", "Only a computer part", "A type of cable"],
        correct_index=1,
    ),
    Question(
        id=72,
        topic="Complexity",
        prompt="O(1) time means the work stays roughly the same as input size:",
        options=["Grows", "Shrinks", "Stays constant", "Becomes impossible"],
        correct_index=2,
    ),
    Question(
        id=73,
        topic="Data Structures",
        prompt="A linked list stores items using nodes that point to:",
        options=["The next node", "Only the first node", "A web browser", "A compiler"],
        correct_index=0,
    ),
    Question(
        id=74,
        topic="Python",
        prompt="Which Python collection stores key-value pairs?",
        options=["List", "Tuple", "Dictionary", "String"],
        correct_index=2,
    ),
    Question(
        id=75,
        topic="Software Testing",
        prompt="A regression test helps check that old behavior:",
        options=["Still works after changes", "Is deleted immediately", "Never needs testing", "Only runs on paper"],
        correct_index=0,
    ),
]


SUBJECT_CATEGORIES = {
    "math": {
        "title": "Math",
        "subjects": ["basic_math"],
    },
    "science": {
        "title": "Science",
        "subjects": ["general_science"],
    },
    "history": {
        "title": "History",
        "subjects": ["history_civics"],
    },
    "tech": {
        "title": "Tech",
        "subjects": ["digital_literacy", "internet_safety"],
    },
    "computer_knowledge": {
        "title": "Computer Knowledge",
        "subjects": [
            "cs_fundamentals",
            "algorithms_complexity",
            "data_structures",
            "python_programming",
            "software_engineering",
        ],
    },
}


SUBJECT_QUIZZES = {
    "basic_math": {
        "title": "Basic Math",
        "category": "math",
        "topics": {"Arithmetic", "Fractions", "Geometry", "Algebra", "Data Literacy"},
    },
    "general_science": {
        "title": "General Science",
        "category": "science",
        "topics": {
            "Life Science",
            "Earth Science",
            "Physical Science",
            "Space Science",
            "Scientific Method",
        },
    },
    "history_civics": {
        "title": "History & Civics",
        "category": "history",
        "topics": {"U.S. History", "World History", "Civics", "Geography"},
    },
    "digital_literacy": {
        "title": "Digital Literacy",
        "category": "tech",
        "topics": {"Digital Literacy", "Hardware Basics", "Software Basics", "Productivity Tools"},
    },
    "internet_safety": {
        "title": "Internet Safety",
        "category": "tech",
        "topics": {"Internet Safety"},
    },
    "cs_fundamentals": {
        "title": "CS Fundamentals",
        "category": "computer_knowledge",
        "topics": {
            "Programming Fundamentals",
            "Python",
            "OOP",
            "Software Design",
            "Version Control",
        },
    },
    "algorithms_complexity": {
        "title": "Algorithms & Complexity",
        "category": "computer_knowledge",
        "topics": {"Algorithms", "Complexity"},
    },
    "data_structures": {
        "title": "Data Structures",
        "category": "computer_knowledge",
        "topics": {"Data Structures"},
    },
    "python_programming": {
        "title": "Python Programming",
        "category": "computer_knowledge",
        "topics": {"Programming Fundamentals", "Python", "OOP"},
    },
    "software_engineering": {
        "title": "Software Engineering",
        "category": "computer_knowledge",
        "topics": {
            "Software Engineering",
            "Software Testing",
            "Software Design",
            "Version Control",
        },
    },
}


def get_category_title(category_key: str) -> str:
    category = SUBJECT_CATEGORIES.get(category_key)
    if category is None:
        return "Computer Knowledge"
    return category["title"]


def get_subjects_for_category(category_key: str) -> list[tuple[str, dict]]:
    category = SUBJECT_CATEGORIES.get(category_key)
    if category is None:
        category = SUBJECT_CATEGORIES["computer_knowledge"]
    return [
        (subject_key, SUBJECT_QUIZZES[subject_key])
        for subject_key in category["subjects"]
        if subject_key in SUBJECT_QUIZZES
    ]


def get_subject_title(subject_key: str) -> str:
    subject = SUBJECT_QUIZZES.get(subject_key)
    if subject is None:
        return SUBJECT_QUIZZES["cs_fundamentals"]["title"]
    return subject["title"]


def get_questions_for_subject(subject_key: str) -> List[Question]:
    subject = SUBJECT_QUIZZES.get(subject_key)
    if subject is None:
        return list(QUESTION_BANK)
    topics = subject["topics"]
    return [question for question in QUESTION_BANK if question.topic in topics]
