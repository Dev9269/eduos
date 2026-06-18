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
        "question": "What does CPU stand for?",
        "options": ["Central Processing Unit", "Computer Processing Unit",
                    "Central Program Utility", "Core Processing Unit"],
        "correct": 0,
        "topic": "Computer Basics",
        "difficulty": "Easy"
    },
    {
        "id": 2,
        "question": "Which programming language is commonly used for web development?",
        "options": ["HTML", "Python", "JavaScript", "All of the Above"],
        "correct": 3,
        "topic": "Web Technologies",
        "difficulty": "Easy"
    },
    {
        "id": 3,
        "question": "Which of the following is an operating system?",
        "options": ["Windows", "Linux", "macOS", "All of the Above"],
        "correct": 3,
        "topic": "Operating Systems",
        "difficulty": "Easy"
    },
    {
        "id": 4,
        "question": "What is the full form of RAM?",
        "options": ["Random Access Memory", "Rapid Access Memory",
                    "Read Access Memory", "Run Access Memory"],
        "correct": 0,
        "topic": "Computer Basics",
        "difficulty": "Easy"
    },
    {
        "id": 5,
        "question": "Which command is used to list files in Linux?",
        "options": ["dir", "ls", "list", "show"],
        "correct": 1,
        "topic": "Linux",
        "difficulty": "Easy"
    },
    {
        "id": 6,
        "question": "Which protocol is commonly used for secure web browsing?",
        "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
        "correct": 2,
        "topic": "Networking",
        "difficulty": "Easy"
    },
    {
        "id": 7,
        "question": "Which company developed Git?",
        "options": ["Microsoft", "Google", "Linus Torvalds", "Apple"],
        "correct": 2,
        "topic": "Version Control",
        "difficulty": "Easy"
    },
    {
        "id": 8,
        "question": "What is the extension of a Python file?",
        "options": [".java", ".py", ".cpp", ".html"],
        "correct": 1,
        "topic": "Programming",
        "difficulty": "Easy"
    },
    {
        "id": 9,
        "question": "Which database language is used to query databases?",
        "options": ["SQL", "CSS", "XML", "JSON"],
        "correct": 0,
        "topic": "Databases",
        "difficulty": "Easy"
    },
    {
        "id": 10,
        "question": "Which of the following is a cybersecurity tool?",
        "options": ["Wireshark", "Nmap", "Burp Suite", "All of the Above"],
        "correct": 3,
        "topic": "Cybersecurity",
        "difficulty": "Easy"
    }
]

CODING_CHALLENGE = {
    "title": "Palindrome Checker",
    "description": (
        "Write a program that checks whether a given word is a palindrome.\n\n"
        "A palindrome is a word that reads the same forwards and backwards.\n\n"
        "Examples:\n"
        "  Input: madam\n"
        "  Output: Palindrome\n\n"
        "  Input: hello\n"
        "  Output: Not Palindrome\n\n"
        "Your program should read the input string and print "
        "\"Palindrome\" or \"Not Palindrome\" accordingly."
    ),
    "test_cases": [
        {"input": "madam", "expected": "Palindrome"},
        {"input": "racecar", "expected": "Palindrome"},
        {"input": "hello", "expected": "Not Palindrome"},
        {"input": "level", "expected": "Palindrome"},
        {"input": "world", "expected": "Not Palindrome"},
    ],
    "starter_code": {
        "Python": 'word = input()\n# Your code here\n',
        "C": '#include <stdio.h>\n#include <string.h>\n\nint main() {\n    char word[100];\n    scanf("%s", word);\n    // Your code here\n    return 0;\n}',
        "C++": '#include <iostream>\n#include <string>\nusing namespace std;\n\nint main() {\n    string word;\n    cin >> word;\n    // Your code here\n    return 0;\n}',
        "Java": 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        String word = sc.next();\n        // Your code here\n    }\n}'
    }
}
