#!/usr/bin/env python3

import csv
import sys

## CLASSES
class TM():
    def __init__(self, tape, transitions, headers):
        self.tape = tape
        self.transitions = {}
        self.headers = headers
        self.determinism = []
        for elem in transitions:
            if elem[0] in self.transitions.keys():
                self.transitions[elem[0]].append(elem[1:])
            else:
                self.transitions[elem[0]] = [elem[1:]]
        self.states = [[["", self.headers.start, self.tape]]]
        self.curr_state = self.states[-1]

    def run(self, steps=None, max_transitions=None):
        counter = 0
        transitions = 0
        while True:
            counter += 1
            new_states = self.step()
            if new_states == None:
                return 1, counter
            self.determinism.append(len(new_states))
            transitions += len(new_states)
            self.states.append(new_states)
            for state in new_states:
                if state[1] in self.headers.accept:
                    return 0, counter
            if steps and counter == steps:
                return 2, counter
            if max_transitions and transitions > max_transitions:
                return 3, transitions
    
    def step(self):
        new_states = []
        for state in self.states[-1]:
            if state[1] in self.headers.reject:
                continue
            if state[2] == '':
                symbol = "_"
            else:
                symbol = state[2][0]
            relevant_transitions = []
            for transition in self.transitions[state[1]]:
                if transition[0] == symbol:
                    relevant_transitions.append(transition)
            if not relevant_transitions:
                new_states.append([state[0], self.headers.reject[0], state[2]])
            for tr in relevant_transitions:
                append_state = gen_new_state(tr, symbol, state)
                new_states.append(append_state)
        if not new_states:
            return None
        self.curr_state = new_states
        return new_states
    
class Headers:
    def __init__(self, name, state_list, tape_chars, all_chars, start, accept, reject):
        self.name = ','.join(name)
        self.state_list = state_list
        self.tape_chars = tape_chars
        self.all_chars = all_chars
        self.start = ','.join(start)
        self.accept = accept
        self.reject = reject
    
    def __str__(self):
        return f"Name: {self.name}\nStates: {self.state_list}\nTape Characters: {self.tape_chars}\nAll Characters: {self.all_chars}\nStart State: {self.start}\nAccept State: {self.accept}\nReject State: {self.reject}"
    
## METHODS
def gen_new_state(tr, symbol, state):
    before = state[0]
    after = tr[2]+state[2][1:]
    new_state = tr[1]
    if tr[3] == 'R':
        before = before + tr[2]
        after = after[1:]
    elif tr[3] == 'L':
        if not before:
            before = "_"
        after = before[-1]+after
        before = before[:-1]
    if before == '_':
        before = ''
    if after and after[-1] == '_':
        after = after[:-1]
    if not after:
        after = '_'
        
    return [before, new_state, after]
    
def readTM(filename):
    transitions = []
    with open(filename, 'r') as file:
        reader = list(csv.reader(file))
        try:
            headers = Headers(reader[0], reader[1], reader[2], reader[3], reader[4], reader[5], reader[6])
            for row in reader[7:]:
                transitions.append(row)
        except KeyError:
            print("Error: CSV file is not formatted correctly")
    return transitions, headers

def usage(exitcode):
    print(
'''Usage: traceTM_tparisi.py [-t tape] [-f filename] [-d]
    -t [tape]: specify the tape to be used
    -f [filename]: specify the filename of the TM
    -d: show the diagram of the TM
    -T [transitions]: specify the maximum number of transitions to simulate
    -D [depth]: specify the maximum depth to simulate''')
    sys.exit(exitcode)

def parse_args(args):
    tape = None
    filename = None
    show_diagram = False
    max_transitions = -1
    max_depth = -1
    while args:
        arg = args.pop(0)
        if arg == '-t':
            tape = args.pop(0)
        elif arg == '-f':
            filename = args.pop(0)
        elif arg == '-d':
            show_diagram = True
        elif arg == '-T':
            max_transitions = int(args.pop(0))
        elif arg == '-D':
            max_depth = int(args.pop(0))
        elif arg == '-u':
            usage(0)
        elif arg[0] == '-':
            usage(1)
    if not tape:
        tape = input("Enter tape: ")
    if not filename:
        filename = input("Enter filename: ")
    return filename, tape, show_diagram, max_transitions, max_depth

def print_diagram(states):
    for state in states:
        print(state)

## MAIN
def main(args=sys.argv[1:]):
    max_steps = 1000
    filename, tape, show_diagram, max_transitions, max_depth = parse_args(args)
    transitions, headers = readTM(filename)
    print(f"TM Name: {headers.name}")
    turing = TM(tape, transitions, headers)
    if max_depth != -1:
        result, counter = turing.run(steps=max_depth)
    elif max_transitions != -1:
        result, counter = turing.run(max_transitions=max_transitions)
    else:
        result, counter = turing.run(steps=max_steps)
    if show_diagram:
        print_diagram(turing.states)
    print(f'Initial string: {tape}')
    if result == 0:
        print(f'String accepted')
    elif result == 1:
        print(f'String rejected at a depth of {counter}')
    elif result == 2:
        print(f'Execution stopped at a depth of {counter}')
    elif result == 3:
        print(f'Execution stopped after simulating {counter} transitions')
    print(f'Total transitions simulated: {sum(turing.determinism)}')
    print(f'Average determinism: {sum(turing.determinism)/counter}')
    
if __name__ == '__main__':
    main(sys.argv[1:])