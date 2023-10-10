from lxml import etree

class DFA:

    def __init__(self, desc=None, sigma=[], Q=[], nQ=0, start=None, accept=[]):
        self.desc = desc
        self.sigma = sigma
        self.Q = Q
        self.nQ = nQ
        self.start = start
        self.accept = accept

    def __repr__(self) -> str:
        return "NFA ({})\n[s: {}; a: {}]: \n{}".format(self.desc, self.start, self.accept, '\n'.join([str(s) for s in self.Q]))
    

    def parse_from_xml (self, filepath: str):
        tree = etree.parse(filepath)
        root = tree.getroot()

        self.desc = root.find('desc').text
        self.sigma = (root.find('sigma').text).split(',')
        self.nQ = int(root.find('num').text)
        self.start = int(root.find('start').text)

        acc = (root.find('accept').text).split(',')
        self.accept = [int(s) for s in acc]

        delta = list(root.find('states'))
        if (len(delta) != self.nQ):
            raise Exception('# of states and delta transitions do not match')

        self.Q = []

        for state in delta:
            s = { 'id': state.tag }

            for trans in list(state):
                if (trans.find('input').text not in self.sigma):
                    raise Exception('Input symbol not in sigma')
                    
                if (int(trans.find('output').text) >= self.nQ or int(trans.find('output').text) < 0):
                    raise Exception('Cannot transition to a state outside of max range')
                s[trans.find('input').text] = int(trans.find('output').text)
            self.Q.append(s)

        return self

    
    def process_string (self, input: str) -> bool:
        current = self.start
        string = list(input)
        for s in string:
            if s not in self.sigma:
                raise Exception('input contains symbols not in sigma')
            
        for symbol in string:
            current = self.Q[current][symbol]

        if current in self.accept:
            return True
        else:
            return False


if __name__ == '__main__':
    dfa = DFA()
    dfa.parse_from_xml('dfa_config.xml')
    print(dfa.__repr__())
    print(dfa.process_string('001'))
    print(dfa.process_string('110'))
    print()