from django.core.management.base import BaseCommand

from interview.models import CodingQuestion


CODING_SKELETON_QUESTIONS = [
    {
        'title': 'Reverse a String',
        'question_text': 'Write a function that takes a string and returns the reversed string. Example: "hello" -> "olleh".',
        'difficulty': 'EASY',
        'expected_keywords': 'def,return,[::-1]',
        'test_cases': [
            {'input': 'hello', 'expected': 'olleh'},
            {'input': 'placement', 'expected': 'tnemecalp'},
            {'input': 'a', 'expected': 'a'},
        ],
    },
    {
        'title': 'Find Max in List',
        'question_text': 'Write a function that returns the maximum element in a list of integers without using built-in max().',
        'difficulty': 'EASY',
        'expected_keywords': 'def,for,if,return',
        'test_cases': [
            {'input': [1, 5, 3], 'expected': 5},
            {'input': [-2, -10, -3], 'expected': -2},
            {'input': [42], 'expected': 42},
        ],
    },
    {
        'title': 'First Non-Repeating Character',
        'question_text': 'Given a string, return the first non-repeating character. Return None if all characters repeat.',
        'difficulty': 'MEDIUM',
        'expected_keywords': 'dict,for,return,None',
        'test_cases': [
            {'input': 'aabbcddee', 'expected': 'c'},
            {'input': 'abcabcde', 'expected': 'd'},
            {'input': 'aabbcc', 'expected': None},
        ],
    },
]


def _build_bulk_coding_questions():
    questions = []

    for idx in range(1, 41):
        shift = (idx % 7) + 1
        questions.append(
            {
                'title': f'String Caesar Shift {idx}',
                'question_text': (
                    f'Write a function that shifts each lowercase alphabet character forward by {shift} positions '
                    'with wrap-around (a-z). Keep non-letters unchanged.'
                ),
                'difficulty': 'EASY',
                'expected_keywords': 'def,for,ord,chr,return',
                'test_cases': [
                    {'input': 'abc', 'expected': ''.join(chr(((ord(ch) - 97 + shift) % 26) + 97) for ch in 'abc')},
                    {'input': 'xyz', 'expected': ''.join(chr(((ord(ch) - 97 + shift) % 26) + 97) for ch in 'xyz')},
                    {'input': 'hi-5', 'expected': ''.join(chr(((ord(ch) - 97 + shift) % 26) + 97) if 'a' <= ch <= 'z' else ch for ch in 'hi-5')},
                ],
            }
        )

    for idx in range(1, 41):
        mod = idx + 3
        questions.append(
            {
                'title': f'Sum Multiples Mod {mod}',
                'question_text': (
                    f'Write a function that returns the sum of all numbers from 1 to n that are divisible by {mod}.'
                ),
                'difficulty': 'EASY',
                'expected_keywords': 'def,for,if,return',
                'test_cases': [
                    {'input': 20, 'expected': sum(x for x in range(1, 21) if x % mod == 0)},
                    {'input': 50, 'expected': sum(x for x in range(1, 51) if x % mod == 0)},
                    {'input': 7, 'expected': sum(x for x in range(1, 8) if x % mod == 0)},
                ],
            }
        )

    for idx in range(1, 41):
        window = (idx % 5) + 2
        questions.append(
            {
                'title': f'Moving Window Max Sum {idx}',
                'question_text': (
                    f'Given a list of integers, return maximum sum of any contiguous subarray of size {window}. '
                    'Return None if list length is smaller than window size.'
                ),
                'difficulty': 'MEDIUM',
                'expected_keywords': 'def,for,return,None',
                'test_cases': [
                    {
                        'input': [1, 3, 2, 6, 4, 5],
                        'expected': None if len([1, 3, 2, 6, 4, 5]) < window else max(
                            sum([1, 3, 2, 6, 4, 5][i:i + window]) for i in range(len([1, 3, 2, 6, 4, 5]) - window + 1)
                        ),
                    },
                    {
                        'input': [10, -2, 7, -1, 5],
                        'expected': None if len([10, -2, 7, -1, 5]) < window else max(
                            sum([10, -2, 7, -1, 5][i:i + window]) for i in range(len([10, -2, 7, -1, 5]) - window + 1)
                        ),
                    },
                    {
                        'input': [4, 1],
                        'expected': None if len([4, 1]) < window else max(
                            sum([4, 1][i:i + window]) for i in range(len([4, 1]) - window + 1)
                        ),
                    },
                ],
            }
        )

    return questions


class Command(BaseCommand):
    help = 'Seeds Stage 2 coding questions (100+ bank, random per session).'

    def handle(self, *args, **options):
        all_questions = CODING_SKELETON_QUESTIONS + _build_bulk_coding_questions()
        created_count = 0
        for item in all_questions:
            question, created = CodingQuestion.objects.update_or_create(
                title=item['title'],
                defaults={
                    'question_text': item['question_text'],
                    'difficulty': item['difficulty'],
                    'expected_keywords': item.get('expected_keywords', ''),
                    'test_cases': item.get('test_cases', []),
                    'is_active': True,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Coding seed completed. Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total coding questions in bank: {CodingQuestion.objects.count()}'))
