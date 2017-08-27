#!/usr/bin/python3

import argparse, sys, re
import numpy as np

parser = argparse.ArgumentParser(description='Text justification')
parser.add_argument('-w', '--textwidth', default=80, type=int)
parser.add_argument('infile', type=argparse.FileType('r'), help='Config file to parse, otherwise stdin', default=sys.stdin)
args = parser.parse_args()

def length_line(line):
    """
    Takes a list of words and returns the number of characters including whitespaces
    """
    sum = len(line)-1
    for word in line:
        sum += len(word)

    return sum


def badness(list,textwidth):

    sum = length_line(list)

    if sum > args.textwidth:return float('inf')

    return (args.textwidth-sum)**3

def reconstruct_text(text,breaks):

    lines = []
    linebreaks = []
    
    i = 0
    while True:
        linebreaks.append(breaks[i])
        i = breaks[i]
        if i == len(text):break

    for i in range(len(linebreaks)):
        if i == 0: lines.append( ' '.join(text[ 0:linebreaks[0] ]).strip() )
        else: lines.append( ' '.join(text[ linebreaks[i-1]:linebreaks[i] ]).strip() )

    return lines

def justify(text,textwidth):
    DP = [0]*(len(text)+1)
    breaks = [0]*(len(text)+1)
    for i in range(len(text)-1,-1,-1):
        temp = [DP[j] + badness(text[i:j],args.textwidth) for j in range(i+1,len(text)+1)]
        index = np.argmin(temp)
        # Index plus position in upper list
        breaks[i] = index+i+1
        DP[i] = temp[index]

    text = reconstruct_text(text,breaks)
    text = spacing(text,textwidth)

    return text

def spacing(text,textwidth,maxspace=4):

    for i in range(len(text)):

        length_line = len(text[i])

        if length_line < textwidth:

            status_length = length_line
            whitespaces_remain = textwidth - status_length
            Nwhitespaces = text[i].count(' ')

            # If whitespaces (to add) per whitespace exeeds
            # maxspace, don't do anything.
            if not Nwhitespaces or whitespaces_remain/Nwhitespaces > maxspace-1:pass
            else:
                text[i] = text[i].replace(' ',' '*( 1 + int(whitespaces_remain/Nwhitespaces)) )
                status_length = len(text[i])

                # Periods have highest priority for whitespace insertion
                periods = text[i].split('.')

                # Can we add a whitespace behind each period?
                if len(periods) - 1 + status_length <= textwidth:
                    text[i] = '. '.join(periods).strip()
                    
                status_length = len(text[i])
                whitespaces_remain = textwidth - status_length
                Nwords = len(text[i].split())
                Ngaps = Nwords - 1

                if whitespaces_remain != 0:factor = Ngaps / whitespaces_remain

                # List of whitespaces in line i
                gaps = re.findall('\s+', text[i])

                temp = text[i].split()
                for k in range(Ngaps):
                    temp[k] = ''.join([temp[k],gaps[k]])

                for j in range(whitespaces_remain):
                    if status_length >= textwidth:pass
                    else:
                        replace = temp[int(factor*j)]
                        replace = ''.join([replace, " "])
                        temp[int(factor*j)] = replace

                text[i] = ''.join(temp)

    return text

infile = list(args.infile)
breaks = [i[0] for i in list(enumerate(infile)) if i[1] == '\n']
words=dict()
i=0
j=0
for item in breaks:
    words[j] = infile[i:item]
    i = item
    j += 1

words[j] = infile[i:]

for key in words:
    words[key] = [word.strip() for line in words[key] for word in line.split()]
    words[key] = justify(words[key],args.textwidth)

for key in words:
    for line in words[key]:
        print(line)
    if not key == list(words.keys())[-1]:
        print('\n')

