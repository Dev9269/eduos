"""
EduOS Demo Exam — Configuration & Question Bank
Stores all demo questions, coding challenges, and exam metadata.
"""

DEMO_CREDENTIALS = {
    "student_id": "DEMO001",
    "exam_key": "EDUOS2026"
}

EXAM_CONFIG = {
    "title": "EduOS Engineering Entrance Demo Examination",
    "mcq_duration_minutes": 15,
    "coding_duration_minutes": 15,
    "total_duration_minutes": 30,
    "passing_percentage": 40,
    "instructions": [
        "This is a DEMO examination for demonstration purposes only.",
        "You have 30 minutes to complete both sections.",
        "Section 1: 10 Multiple Choice Questions (15 minutes).",
        "Section 2: 1 Programming Challenge (15 minutes).",
        "Answers are auto-saved every 30 seconds.",
        "The exam auto-submits when the timer expires.",
        "Do not attempt to switch applications during the exam.",
        "Your results will be available as JSON and PDF after submission."
    ]
}

MCQ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which data structure operates on the LIFO (Last In, First Out) principle?",
        "options": ["Queue", "Stack", "Linked List", "Tree"],
        "correct": 1,
        "topic": "Data Structures",
        "difficulty": "Easy"
    },
    {
        "id": 2,
        "question": "What is the time complexity of binary search on a sorted array of n elements?",
        "options": ["O(n)", "O(log n)", "O(n²)", "O(n log n)"],
        "correct": 1,
        "topic": "Algorithms",
        "difficulty": "Easy"
    },
    {
        "id": 3,
        "question": "Which SQL clause is used to filter records based on a condition?",
        "options": ["WHERE", "HAVING", "FILTER", "MATCH"],
        "correct": 0,
        "topic": "Databases",
        "difficulty": "Easy"
    },
    {
        "id": 4,
        "question": "Which protocol is used to reliably deliver web pages over the internet?",
        "options": ["FTP", "UDP", "HTTP/HTTPS", "SMTP"],
        "correct": 2,
        "topic": "Networking",
        "difficulty": "Easy"
    },
    {
        "id": 5,
        "question": "Which of the following is NOT an operating system?",
        "options": ["Linux", "Windows", "Python", "macOS"],
        "correct": 2,
        "topic": "Operating Systems",
        "difficulty": "Easy"
    },
    {
        "id": 6,
        "question": "What is the correct way to declare a variable in Python?",
        "options": ["int x = 10;", "x = 10", "var x = 10;", "let x = 10;"],
        "correct": 1,
        "topic": "Programming",
        "difficulty": "Easy"
    },
    {
        "id": 7,
        "question": "Which software development methodology follows an iterative, incremental approach?",
        "options": ["Waterfall", "Agile", "Spiral", "V-Model"],
        "correct": 1,
        "topic": "Software Engineering",
        "difficulty": "Medium"
    },
    {
        "id": 8,
        "question": "What does CPU stand for?",
        "options": ["Central Processing Unit", "Computer Personal Unit",
                    "Central Program Utility", "Core Processing Unit"],
        "correct": 0,
        "topic": "Computer Architecture",
        "difficulty": "Easy"
    },
    {
        "id": 9,
        "question": "Which of the following is a common cybersecurity attack where the attacker intercepts communication between two parties?",
        "options": ["Phishing", "Man-in-the-Middle", "Ransomware", "DDoS"],
        "correct": 1,
        "topic": "Cybersecurity",
        "difficulty": "Medium"
    },
    {
        "id": 10,
        "question": "Which HTML tag is used to create a hyperlink?",
        "options": ["<link>", "<a>", "<href>", "<url>"],
        "correct": 1,
        "topic": "Web Technologies",
        "difficulty": "Easy"
    }
]

CODING_CHALLENGE = {
    "title": "Palindrome Checker",
    "description": (
        "Write a function that checks whether a given string is a palindrome. "
        "A palindrome is a string that reads the same forwards and backwards, "
        "ignoring case, spaces, and punctuation.\n\n"
        "Examples:\n"
        "  Input: \"racecar\" → Output: True\n"
        "  Input: \"A man, a plan, a canal: Panama\" → Output: True\n"
        "  Input: \"hello\" → Output: False\n\n"
        "Your function should return True if the input is a palindrome, False otherwise."
    ),
    "test_cases": [
        {"input": "racecar", "expected": True},
        {"input": "hello", "expected": False},
        {"input": "A man, a plan, a canal: Panama", "expected": True},
        {"input": "12321", "expected": True},
        {"input": "not a palindrome", "expected": False},
    ],
    "starter_code": {
        "Python": 'def is_palindrome(s: str) -> bool:\n    # Your code here\n    pass\n\n# Test cases\nprint(is_palindrome("racecar"))\nprint(is_palindrome("hello"))',
        "C": '#include <stdio.h>\n#include <stdbool.h>\n#include <string.h>\n#include <ctype.h>\n\nbool is_palindrome(char *s) {\n    // Your code here\n    return false;\n}\n\nint main() {\n    printf("%d\\n", is_palindrome("racecar"));\n    printf("%d\\n", is_palindrome("hello"));\n    return 0;\n}',
        "C++": '#include <iostream>\n#include <string>\n#include <algorithm>\n#include <cctype>\n\nbool is_palindrome(const std::string& s) {\n    // Your code here\n    return false;\n}\n\nint main() {\n    std::cout << is_palindrome("racecar") << std::endl;\n    std::cout << is_palindrome("hello") << std::endl;\n    return 0;\n}',
        "Java": 'public class Solution {\n    public static boolean isPalindrome(String s) {\n        // Your code here\n        return false;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(isPalindrome("racecar"));\n        System.out.println(isPalindrome("hello"));\n    }\n}'
    }
}
