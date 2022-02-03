from collections import Counter
import math

from progress.bar import IncrementalBar

all_answers = []
allowed = []

with open('answers.txt') as f:
    all_answers = [line.strip() for line in f]

# allowed = answers
with open('allowed.txt') as f:
    allowed = [line.strip() for line in f] + all_answers


def get_hint(answer, guess):
    assert len(guess) == len(answer)

    green = []
    letters = set()

    for i in range(len(guess)):
        if guess[i] in answer:
            letters.add(guess[i])
        if guess[i] == answer[i]:
            green.append(i)

    return tuple(green), tuple(letters)

def parse_hint(guess, hint_vals):
    assert len(guess) == len(hint_vals)

    green = []
    letters = set()

    for i in range(len(guess)):
        if hint_vals[i] > 0:
            letters.add(guess[i])
        if hint_vals[i] == 2:
            green.append(i)

    return tuple(green), tuple(letters)


def guess_entropy(answers, guess):
    hints_freqs =  Counter([get_hint(x, guess) for x in answers])
    return sum(
        (hints_freqs[h] / hints_freqs.total()) *
        math.log(hints_freqs.total() / hints_freqs[h], 2)
        for h in hints_freqs
    )

def get_best_guesses(answers, showbar=True):
    scores = {}

    N = len(allowed)

    if showbar:
        bar = IncrementalBar('Scoring', max=N, suffix='%(index)d/%(max)d ETA: %(eta)ds')

    for guess in allowed[:N]:
        scores[guess] = guess_entropy(answers, guess)
        if showbar: bar.next()
    if showbar: bar.finish()

    return scores


def test(answer, file=None):
    print(f'TEST: {answer}')
    answers = all_answers
    guess = 'soare'
    n = 1

    while guess != answer:
        print(f'guess {n}: {guess}')

        if file is not None: file.write(f'{guess},')

        hint = get_hint(answer, guess)
        answers = [x for x in answers if get_hint(x, guess) == hint]
        print(f'{len(answers)} left ({math.log(len(answers), 2):.3} bits)')

        g = get_best_guesses(answers, showbar=False)
        sorted_scores = [ (k, v) for k,v in sorted(g.items(), key=lambda item: item[1], reverse=True) ]
        guess = sorted_scores[0][0]
        for x in answers:
            if g[x] == math.log(len(answers), 2):
                guess = x

        n += 1

    print(f'guess {n}: {guess}')
    if file is not None: file.write(f'{guess}\n')

    return n




def interactive():
    answers = all_answers

    while len(answers) > 1:
        print(f'{len(answers)} left ({math.log(len(answers), 2):.3} bits)')
        if len(answers) <= 10:
            [print(f'{x} ({guess_entropy(answers, x):.3} bits)', end='  ') for x in answers]
            print()

        best = 'soare'

        if input('run? ') == 'y':
            g = get_best_guesses(answers)
            sorted_scores = [ (k, v) for k,v in sorted(g.items(), key=lambda item: item[1], reverse=True) ]
            best = sorted_scores[0][0]

            for guess in answers:
                if g[guess] == math.log(len(answers), 2):
                    best = guess

            for k, v in sorted_scores[:10]:
                print(f'{k}  {v:.3} bits')
            
        guess = ''
        while guess not in allowed:
            guess = input('guess: ')
            if guess == '': guess = best

        hint = parse_hint(guess, [int(x) for x in input('hint: ')])

        answers = [x for x in answers if get_hint(x, guess) == hint]

    if len(answers) == 0:
        print('word list exhausted')

    if len(answers) == 1:
        print('1 left')
        print(answers[0])


if __name__ == '__main__':
    total_guesses = 0

    sorted_answers = sorted(all_answers)

    with open('results.txt', 'w') as f:
        for i in range(len(sorted_answers)):
            total_guesses += test(sorted_answers[i], f)
            print(f'TOTAL GUESSES: {total_guesses} / {i + 1} words')
            print(f'AVG GUESSES: {total_guesses / (i+1):.4}')
            print()
