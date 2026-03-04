from django.core.management.base import BaseCommand

from interview.models import AptitudeQuestion


AI_GENERATED_QUESTIONS = [
    {
        'topic': 'Percentages',
        'question_text': 'A laptop marked at ₹50,000 is sold at 10% discount. What is the selling price?',
        'option_a': '₹44,500',
        'option_b': '₹45,000',
        'option_c': '₹46,000',
        'option_d': '₹47,500',
        'correct_option': 'B',
        'explanation': '10% of 50,000 is 5,000, so selling price is 45,000.',
    },
    {
        'topic': 'Ratios',
        'question_text': 'If A:B = 3:5 and B:C = 10:7, then A:B:C is:',
        'option_a': '3:10:7',
        'option_b': '6:10:7',
        'option_c': '6:5:7',
        'option_d': '3:5:7',
        'correct_option': 'B',
        'explanation': 'Make B common at 10: A:B = 6:10 and B:C = 10:7.',
    },
    {
        'topic': 'Averages',
        'question_text': 'Average of 5 numbers is 24. If one number is removed, average becomes 20. Removed number is:',
        'option_a': '32',
        'option_b': '36',
        'option_c': '40',
        'option_d': '44',
        'correct_option': 'C',
        'explanation': 'Total 5 numbers = 120, remaining total = 80, removed = 40.',
    },
    {
        'topic': 'Time and Work',
        'question_text': 'A can finish a job in 12 days, B in 18 days. Working together, they finish in:',
        'option_a': '6.2 days',
        'option_b': '7.2 days',
        'option_c': '8.4 days',
        'option_d': '9 days',
        'correct_option': 'B',
        'explanation': 'Combined rate = 1/12 + 1/18 = 5/36, time = 36/5 = 7.2 days.',
    },
    {
        'topic': 'Time Speed Distance',
        'question_text': 'A car covers 180 km in 3 hours. Its speed is:',
        'option_a': '45 km/h',
        'option_b': '50 km/h',
        'option_c': '60 km/h',
        'option_d': '65 km/h',
        'correct_option': 'C',
        'explanation': 'Speed = distance/time = 180/3 = 60 km/h.',
    },
    {
        'topic': 'Profit and Loss',
        'question_text': 'An item bought for ₹800 is sold for ₹920. Profit percent is:',
        'option_a': '10%',
        'option_b': '12%',
        'option_c': '15%',
        'option_d': '20%',
        'correct_option': 'C',
        'explanation': 'Profit = 120; 120/800 × 100 = 15%.',
    },
    {
        'topic': 'Simple Interest',
        'question_text': 'SI on ₹4,000 at 5% p.a. for 3 years is:',
        'option_a': '₹500',
        'option_b': '₹550',
        'option_c': '₹600',
        'option_d': '₹650',
        'correct_option': 'C',
        'explanation': 'SI = (P×R×T)/100 = 4000×5×3/100 = 600.',
    },
    {
        'topic': 'Compound Interest',
        'question_text': 'CI on ₹10,000 at 10% p.a. for 2 years is:',
        'option_a': '₹2,000',
        'option_b': '₹2,100',
        'option_c': '₹2,200',
        'option_d': '₹2,500',
        'correct_option': 'B',
        'explanation': 'Amount = 10000×1.1×1.1 = 12100, CI = 2100.',
    },
    {
        'topic': 'Number System',
        'question_text': 'Greatest common divisor of 36 and 48 is:',
        'option_a': '6',
        'option_b': '8',
        'option_c': '12',
        'option_d': '16',
        'correct_option': 'C',
        'explanation': 'Common factors highest is 12.',
    },
    {
        'topic': 'Algebra',
        'question_text': 'If x + 3 = 11, then x =',
        'option_a': '6',
        'option_b': '7',
        'option_c': '8',
        'option_d': '9',
        'correct_option': 'C',
        'explanation': 'x = 11 - 3 = 8.',
    },
    {
        'topic': 'Geometry',
        'question_text': 'Area of a rectangle of length 12 cm and width 7 cm is:',
        'option_a': '72 cm²',
        'option_b': '84 cm²',
        'option_c': '96 cm²',
        'option_d': '98 cm²',
        'correct_option': 'B',
        'explanation': 'Area = l × b = 12 × 7 = 84.',
    },
    {
        'topic': 'Data Interpretation',
        'question_text': 'If sales were 120, 150, 180 in three months, average sales is:',
        'option_a': '140',
        'option_b': '145',
        'option_c': '150',
        'option_d': '160',
        'correct_option': 'C',
        'explanation': 'Average = (120+150+180)/3 = 150.',
    },
    {
        'topic': 'Probability',
        'question_text': 'Probability of getting a 4 on a fair die is:',
        'option_a': '1/3',
        'option_b': '1/4',
        'option_c': '1/5',
        'option_d': '1/6',
        'correct_option': 'D',
        'explanation': 'Only one favorable outcome out of 6.',
    },
    {
        'topic': 'Permutation and Combination',
        'question_text': 'Number of ways to choose 2 students from 5 is:',
        'option_a': '5',
        'option_b': '10',
        'option_c': '12',
        'option_d': '20',
        'correct_option': 'B',
        'explanation': '5C2 = 10.',
    },
    {
        'topic': 'Logical Reasoning',
        'question_text': 'Find the next number: 2, 6, 12, 20, ?',
        'option_a': '28',
        'option_b': '30',
        'option_c': '32',
        'option_d': '34',
        'correct_option': 'B',
        'explanation': 'Pattern n(n+1): 1×2, 2×3, 3×4, 4×5, next 5×6 = 30.',
    },
    {
        'topic': 'Coding Aptitude',
        'question_text': 'In Python, which keyword defines a function?',
        'option_a': 'func',
        'option_b': 'define',
        'option_c': 'def',
        'option_d': 'lambda',
        'correct_option': 'C',
        'explanation': 'Python function declaration starts with def.',
    },
    {
        'topic': 'SQL Basics',
        'question_text': 'Which SQL statement is used to fetch data?',
        'option_a': 'GET',
        'option_b': 'FETCH',
        'option_c': 'SELECT',
        'option_d': 'READ',
        'correct_option': 'C',
        'explanation': 'SELECT retrieves rows from table.',
    },
    {
        'topic': 'Operating Systems',
        'question_text': 'Which of these is a process scheduling algorithm?',
        'option_a': 'DFS',
        'option_b': 'Round Robin',
        'option_c': 'Binary Search',
        'option_d': 'Merge Sort',
        'correct_option': 'B',
        'explanation': 'Round Robin is a CPU scheduling algorithm.',
    },
    {
        'topic': 'Computer Networks',
        'question_text': 'Which protocol is primarily used for web pages?',
        'option_a': 'FTP',
        'option_b': 'SMTP',
        'option_c': 'HTTP',
        'option_d': 'SNMP',
        'correct_option': 'C',
        'explanation': 'HTTP powers data transfer for web pages.',
    },
    {
        'topic': 'Verbal Ability',
        'question_text': 'Choose the correctly spelled word:',
        'option_a': 'Accomodation',
        'option_b': 'Acommodation',
        'option_c': 'Accommodation',
        'option_d': 'Accommadation',
        'correct_option': 'C',
        'explanation': 'Correct spelling is Accommodation.',
    },
    {
        'topic': 'Percentages',
        'question_text': 'What is 25% of 640?',
        'option_a': '120',
        'option_b': '140',
        'option_c': '160',
        'option_d': '180',
        'correct_option': 'C',
        'explanation': '25% = 1/4, and 640/4 = 160.',
    },
    {
        'topic': 'Ratios',
        'question_text': 'If boys:girls = 4:5 and total students are 45, number of boys is:',
        'option_a': '20',
        'option_b': '24',
        'option_c': '25',
        'option_d': '30',
        'correct_option': 'A',
        'explanation': 'Total parts 9, each part 5, boys = 4×5 = 20.',
    },
    {
        'topic': 'Averages',
        'question_text': 'Average of first 10 natural numbers is:',
        'option_a': '5',
        'option_b': '5.5',
        'option_c': '6',
        'option_d': '6.5',
        'correct_option': 'B',
        'explanation': 'Average of 1..n is (n+1)/2, so 11/2 = 5.5.',
    },
    {
        'topic': 'Time and Work',
        'question_text': 'If 5 workers complete a task in 12 days, 10 workers will complete it in:',
        'option_a': '4 days',
        'option_b': '5 days',
        'option_c': '6 days',
        'option_d': '7 days',
        'correct_option': 'C',
        'explanation': 'Work is inversely proportional to workers, so days halve to 6.',
    },
    {
        'topic': 'Time Speed Distance',
        'question_text': 'Distance covered at 80 km/h in 2.5 hours:',
        'option_a': '180 km',
        'option_b': '190 km',
        'option_c': '200 km',
        'option_d': '220 km',
        'correct_option': 'C',
        'explanation': 'Distance = speed × time = 80 × 2.5 = 200.',
    },
    {
        'topic': 'Profit and Loss',
        'question_text': 'Cost price ₹500, profit 20%. Selling price is:',
        'option_a': '₹550',
        'option_b': '₹580',
        'option_c': '₹600',
        'option_d': '₹620',
        'correct_option': 'C',
        'explanation': 'SP = 500 × 1.2 = 600.',
    },
    {
        'topic': 'Simple Interest',
        'question_text': 'At 8% p.a., SI for 2 years on ₹2,500 is:',
        'option_a': '₹300',
        'option_b': '₹350',
        'option_c': '₹400',
        'option_d': '₹450',
        'correct_option': 'C',
        'explanation': 'SI = 2500×8×2/100 = 400.',
    },
    {
        'topic': 'Probability',
        'question_text': 'A coin is tossed once. Probability of tail is:',
        'option_a': '0',
        'option_b': '1/4',
        'option_c': '1/2',
        'option_d': '1',
        'correct_option': 'C',
        'explanation': 'Coin has two equally likely outcomes.',
    },
    {
        'topic': 'Logical Reasoning',
        'question_text': 'If all roses are flowers and some flowers fade quickly, which is true?',
        'option_a': 'All roses fade quickly',
        'option_b': 'Some roses may fade quickly',
        'option_c': 'No roses fade quickly',
        'option_d': 'All flowers are roses',
        'correct_option': 'B',
        'explanation': 'From given statements, possibility is that some roses may be among those flowers.',
    },
    {
        'topic': 'Data Interpretation',
        'question_text': 'A value rises from 80 to 100. Percentage increase is:',
        'option_a': '20%',
        'option_b': '22%',
        'option_c': '24%',
        'option_d': '25%',
        'correct_option': 'D',
        'explanation': 'Increase = 20 on base 80, so 20/80 ×100 = 25%.',
    },
]


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _build_option_payload(correct_value, distractor_values):
    correct_text = _format_number(correct_value)
    option_pool = []
    for item in distractor_values:
        text = _format_number(item)
        if text != correct_text and text not in option_pool:
            option_pool.append(text)

    while len(option_pool) < 3:
        option_pool.append(str(int(float(correct_text)) + len(option_pool) + 1))

    option_values = option_pool[:3]
    insertion_index = sum(ord(ch) for ch in correct_text) % 4
    option_values.insert(insertion_index, correct_text)

    labels = ['A', 'B', 'C', 'D']
    return {
        'option_a': option_values[0],
        'option_b': option_values[1],
        'option_c': option_values[2],
        'option_d': option_values[3],
        'correct_option': labels[insertion_index],
    }


def _build_bulk_aptitude_questions():
    questions = []

    for base in range(400, 2200, 60):
        for percent in [5, 10, 12, 15, 20, 25]:
            answer = round((base * percent) / 100, 2)
            payload = _build_option_payload(answer, [answer - 4, answer + 4, answer + 8])
            questions.append(
                {
                    'topic': 'Percentages',
                    'question_text': f'What is {percent}% of {base}?',
                    'explanation': f'{percent}% of {base} = {answer}.',
                    **payload,
                }
            )

    for left in range(2, 11):
        for right in range(3, 12):
            total = (left + right) * 8
            answer = int(total * left / (left + right))
            payload = _build_option_payload(answer, [answer - 4, answer + 4, answer + 8])
            questions.append(
                {
                    'topic': 'Ratios',
                    'question_text': f'If A:B = {left}:{right} and A+B = {total}, what is A?',
                    'explanation': f'Total parts = {left + right}, one part = {total // (left + right)}, so A = {answer}.',
                    **payload,
                }
            )

    for start in range(5, 90, 5):
        for count in [4, 5, 6, 8]:
            answer = start + (count - 1) / 2
            payload = _build_option_payload(answer, [answer - 1, answer + 1, answer + 2])
            questions.append(
                {
                    'topic': 'Averages',
                    'question_text': f'Average of {count} consecutive numbers starting from {start} is:',
                    'explanation': f'Average of consecutive sequence = first + (n-1)/2 = {_format_number(answer)}.',
                    **payload,
                }
            )

    for speed in range(30, 95, 5):
        for hours in [2, 3, 4, 5]:
            answer = speed * hours
            payload = _build_option_payload(answer, [answer - speed, answer + speed, answer + 2 * speed])
            questions.append(
                {
                    'topic': 'Time Speed Distance',
                    'question_text': f'Distance covered at {speed} km/h in {hours} hours is:',
                    'explanation': f'Distance = speed × time = {speed} × {hours} = {answer}.',
                    **payload,
                }
            )

    for cp in range(200, 2100, 100):
        for profit_percent in [5, 10, 15, 20, 25]:
            answer = round(cp * (1 + profit_percent / 100), 2)
            payload = _build_option_payload(answer, [answer - 10, answer + 10, answer + 20])
            questions.append(
                {
                    'topic': 'Profit and Loss',
                    'question_text': f'If cost price is ₹{cp} and profit is {profit_percent}%, selling price is:',
                    'explanation': f'SP = CP × (1 + p/100) = ₹{_format_number(answer)}.',
                    **payload,
                }
            )

    for principal in range(1000, 11000, 1000):
        for rate in [5, 8, 10, 12]:
            for years in [1, 2]:
                answer = round((principal * rate * years) / 100, 2)
                payload = _build_option_payload(answer, [answer - 50, answer + 50, answer + 100])
                questions.append(
                    {
                        'topic': 'Simple Interest',
                        'question_text': f'Find SI on ₹{principal} at {rate}% p.a. for {years} year(s).',
                        'explanation': f'SI = P×R×T/100 = ₹{_format_number(answer)}.',
                        **payload,
                    }
                )

    return questions


class Command(BaseCommand):
    help = 'Seeds Stage 1 aptitude questions (500+ question bank with random session selection support).'

    def handle(self, *args, **options):
        all_questions = AI_GENERATED_QUESTIONS + _build_bulk_aptitude_questions()
        created_count = 0
        for item in all_questions:
            _, created = AptitudeQuestion.objects.get_or_create(
                question_text=item['question_text'],
                defaults=item,
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Aptitude seed completed. Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total questions in bank: {AptitudeQuestion.objects.count()}'))
