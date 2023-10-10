from lxml import etree

class TM:

    def __init__(self, desc=None):
        self.desc = desc

    def __repr__(self) -> str:
        return 'TM ({})'.format(self.desc)
    
    def parse_from_xml (self, filepath: str):
        tree = etree.parse(filepath)
        root = tree.getroot()

        self.desc = root.find('desc').text
        self.sigma = (root.find('sigma').text).split(',')
        self.gamma = (root.find('gamma').text).split(',')
        self.nQ = int(root.find('num').text)
        self.start = int(root.find('start').text)

        delta = list(root.find('states'))
        if (len(delta) != self.nQ):
            raise Exception('# of states and delta transitions do not match')
        
        self.Q = []

        for state in delta:
            s = { 'id': state.tag }

            for trans in list(state):
                if (trans.find('read').text not in self.gamma):
                    raise Exception('Input symbol not in gamma')
                if (trans.find('write').text not in self.gamma):
                    raise Exception('Output symbol not in gamma')
                try:
                    next = int(trans.find('next').text)
                    if (next >= self.nQ or next < -1): raise Exception('state cannot transition outside of min/max range')
                except: raise Exception('next state must be indexed by integer')
                
                if (trans.find('tape').text.lower() not in ['l', 'r']):
                    raise Exception('Invalid <tape> tag, head must move L or R')

                s[trans.find('read').text] = (trans.find('write').text, trans.find('tape').text.lower(), next)

            self.Q.append(s)
        self.Q.append({ 'id': 'qA'})

        return self
    
    def process_input (self, input: str):
        input = list(input)
        for sym in input:
            if sym not in self.sigma:
                raise Exception('input contains symbols not in sigma')
        
        head = 0
        current = self.start

        while (self.Q[current]['id'] != 'qA'):
            if (head >= len(input)): input.append('_')
            
            if (input[head] not in self.Q[current].keys()): return False, ''.join(input)
            write, tape, next = self.Q[current][input[head]]

            input[head] = write
            if (tape == 'r'): head += 1
            else: head = max([0, head - 1])
            current = next

        return True, ''.join(input)
    
    def trace_input (self, input: str) -> str:
        input = list(input)
        for sym in input:
            if sym not in self.sigma:
                print(sym)
                print(self.sigma)
                raise Exception('input contains symbols not in sigma')
        
        head = 0
        current = self.start
        ret = 'Run TM on ' + ''.join(input) + ':\n'

        while (self.Q[current]['id'] != 'qA'):
            if (head >= len(input)): input.append('_')
            ret += ('{}[{}]{}\n'.format(''.join(input[:head]), self.Q[current]['id'], ''.join(input[head:])))
            
            if (input[head] not in self.Q[current].keys()):
                ret += ('{}[{}]{}\n'.format(''.join(input[:head]), 'qR', ''.join(input[head:])))
                return ret
            write, tape, next = self.Q[current][input[head]]

            input[head] = write
            if (tape == 'r'): head += 1
            else: head = max([0, head - 1])
            current = next

        ret += ('{}[{}]{}\n'.format(''.join(input[:head]), 'qA', ''.join(input[head:])))
        return ret
    

if __name__ == '__main__':
    tm = TM()
    tm.parse_from_xml('tm_config.xml')
    print(tm)
    print(tm.trace_input('1010'))
    print(tm.process_input('10'))

    tm1 = TM()
    tm1.parse_from_xml('tm_config1.xml')
    print(tm1.trace_input('01#01'))
    print(tm1.trace_input('0#1'))