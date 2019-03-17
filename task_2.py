import re, string, argparse
def Postfix(regex):
	postfix, out = [], []
	for i, c in enumerate(regex):
		if c in ['|', '&']:
			if out and out[-1] != '(':
				postfix.append(out.pop())
			out.append(c)
		elif c == '(':
			out.append(c)
		elif c == ')':
			try:
				if out[-1] != '(':
					postfix.append(out.pop())
				out.pop()
			# If we hit the start of the operator stack without encountering a 
			# matching left-bracket, we raise an error.
			except IndexError:
				raise RuntimeError('Unmatched brackets')
		else:
			# This case handles both the unary operators and any literals, 
			# which can both be added directly to the queue.
			postfix.append(c)
	# If there is an operator left on the stack, we pop it onto the queue.
	if out:
		postfix.append(out.pop())
	postfixRegex = ''.join(postfix)
	return postfixRegex

def AddConcat(regex):
	# adds concatenation operators to a regex
	# returns: a regex with concatenation operators
	concat = []
	for i, c in enumerate(regex):
		concat.append(c)
		# Add concatenation operators between cacters.
		if (c not in ['(', '|'] and i + 1 < len(regex) and 
		  regex[i+1] not in ['*','+','?',')','|']):
			concat.append('&')
	result = ''.join(concat)
	return result

class State:
    def __init__(self, name, value):
        self.epsilonClosure = []
        self.transitions = {}
        self.name = name
        self.value = value
        self.isEnd = False

class nfa:
    def __init__(self, start, end):
        self.start = start
        self.end = end 
        end.isEnd = True

    def addState(self, state, stateSet): # add state + recursively add epsilon transitions
        if state in stateSet:
            return
        stateSet.add(state)
        for eps in state.epsilonClosure:
            self.addState(eps, stateSet)

class nfaStack:
    def __init__(self, allAlphabet, regex):
        self.states = []
        self.allAlphabet = allAlphabet
        self.startState = ""
        self.finalStates = []
        self.transitions = []
        self.regex = regex
        self.alphabet = []
        self.nfaStack = []
        self.postfix = Postfix(AddConcat(regex))
        print(self.postfix)
        self.stateIndex = 0
        self.calculateNFA()
        self.printResult()

        
    def createState(self):
        s = State('q' + str(self.stateIndex), self.stateIndex)
        self.stateIndex += 1
        return s

    def printAlphabet(self, x):
        return ','.join(map(str, x))

    def printAlphabet2(self, x):
        return ', '.join(map(str, x))
        
    def addStates(self, start, end):
        if start not in self.states:
            self.states.append(start)
        for i in start.epsilonClosure:
            if i not in self.states:
                self.addStates(i, end)
        for j in start.transitions:
            if start.transitions[j] not in self.states:
                self.addStates(start.transitions[j], end)

    def handleItems(self, listX):
        return "[" + ", ".join( str(x) for x in listX) + "]"

    def printTransitions(self, states):
        for i in states:
            listE = []
            for x in i.epsilonClosure:
                listE.append(x.name)
            if listE:
                for t in listE:
                    self.transitions.append("(" + i.name +", "+", ["+ t +"])")
                # self.transitions.append("(" + i.name +", "+", "+ self.handleItems(listE) +")")
            for y in i.transitions:
                self.transitions.append("(" + i.name + ", " + str(y) + ", [" + i.transitions[y].name + "])")
      
    def printResult(self):
        nfaFinal = self.nfaStack.pop()
        start = nfaFinal.start
        end = nfaFinal.end
        self.startState = start.name
        self.finalStates.append(end.name)
        self.addStates(start, end)
        sortedStates = sorted(self.states, key=lambda x: x.value, reverse=False)
        printingStates = []
        printingFinalStates = []
        for i in sortedStates:
            printingStates.append(i.name)
        for i in self.finalStates:
            printingFinalStates.append(i)
        self.printTransitions(sortedStates)
        # Output File
        output_file = open("task_2_result.txt", "w+", encoding="utf-8")
        output_file.write(self.printAlphabet(printingStates) + "\n")
        output_file.write(self.printAlphabet(self.alphabet) + "\n")
        output_file.write(self.startState + "\n")
        output_file.write(self.printAlphabet(printingFinalStates) + "\n")
        output_file.write(self.printAlphabet2(self.transitions) + "\n")

    def calculateNFA(self):
        for i in self.postfix:
            if i in self.allAlphabet:
                self.handleChar(i)
            elif i == "&":
                self.handleConcat()
            elif i == "+":
                self.handlePlus()
            elif i == "*":
                self.handleAstrix()
            elif i == "?":
                self.handleQmark()
            elif i == "|":
                self.handleOr()
            elif i == "\u03B5":
                self.handleEpsilon()
            else:
                self.handleEpsilon()

    def handleOr(self):
        if not " " in self.alphabet:
            self.alphabet = [" "] + self.alphabet
        n2 = self.nfaStack.pop()
        n1 = self.nfaStack.pop()
        s0 = self.createState()
        s0.epsilonClosure = [n1.start, n2.start]
        s3 = self.createState()
        n1.end.epsilonClosure.append(s3)
        n2.end.epsilonClosure.append(s3)
        n1.end.is_end = False
        n2.end.is_end = False
        nfaCreated = nfa(s0, s3)
        self.nfaStack.append(nfaCreated)
    
    def handleConcat(self):
        n2 = self.nfaStack.pop()
        n1 = self.nfaStack.pop()
        n1.end.isEnd = False
        self.stateIndex -= 1
        tempState = n2.start
        n2.end.name = "q" + str(self.stateIndex - 1)
        n2.end.value = self.stateIndex - 1
        n2.start = n1.end
        n2.start.transitions.update(tempState.transitions)
        n2.start.epsilonClosure = n2.start.epsilonClosure + tempState.epsilonClosure
        # n1.end.epsilonClosure.append(n2.start)
        # n2.start = n1.end
        nfaCreated = nfa(n1.start, n2.end)
        self.nfaStack.append(nfaCreated)

    def handleQmark(self):
        if not " " in self.alphabet:
            self.alphabet = [" "] + self.alphabet
        n1 = self.nfaStack.pop()
        s0 = self.createState()
        s1 = self.createState()
        s0.epsilonClosure = [n1.start]
        s0.epsilonClosure.append(s1)
        n1.end.epsilonClosure.extend([s1])
        n1.end.isEnd = False
        nfaCreated = nfa(s0, s1)
        self.nfaStack.append(nfaCreated)

    def handleChar(self, t):
        if not t in self.alphabet:
            self.alphabet.append(t)
        s1 = self.createState()
        s2 = self.createState()
        s1.transitions[t] = s2
        nfaCreated = nfa(s1, s2)
        self.nfaStack.append(nfaCreated)

    def handleEpsilon(self):
        if not " " in self.alphabet:
            self.alphabet = [" "] + self.alphabet
        s1 = self.createState()
        s2 = self.createState()
        s1.epsilonClosure = [s2]
        # s1.transitions["\u03B5"] = s2
        nfaCreated = nfa(s1, s2)
        self.nfaStack.append(nfaCreated)

    def handlePlus(self):
        if not " " in self.alphabet:
            self.alphabet = [" "] + self.alphabet
        n1 = self.nfaStack.pop()
        s0 = self.createState()
        s1 = self.createState()
        s0.epsilonClosure = [n1.start]
        n1.end.epsilonClosure.extend([s1, n1.start])
        n1.end.isEnd = False
        nfaCreated = nfa(s0, s1)
        self.nfaStack.append(nfaCreated)

    def handleAstrix(self):
        if not " " in self.alphabet:
            self.alphabet = [" "] + self.alphabet
        n1 = self.nfaStack.pop()
        s0 = self.createState()
        s1 = self.createState()
        s0.epsilonClosure = [n1.start]
        s0.epsilonClosure.append(s1)
        n1.end.epsilonClosure.extend([s1, n1.start])
        n1.end.isEnd = False
        nfaCreated = nfa(s0, s1)
        self.nfaStack.append(nfaCreated)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")
    args = parser.parse_args()
    print(args.file)
    output_file = open("task_2_result.txt", "w+")
    with open(args.file, "r") as f:
        for line in f:
            allAlphabet = list(string.ascii_letters) + list(string.digits)
            obj = nfaStack(allAlphabet, line)


