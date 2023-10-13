from nondetfinauto import NFA
from detfinauto import DFA
from gennondetfinauto import GNFA
import copy

class Builder:

    def __init__(self) -> None:
        self.g_layout = 'spring'

    def config_layout(self, layout: str):
        self.g_layout = layout

    def parseDFA (self, filepath: str) -> DFA:
        dfa = DFA(filepath=filepath)
        return dfa

    def parseNFA (self, filepath: str) -> NFA:
        nfa = NFA(filepath=filepath)
        return nfa
    
    def plot (self, fa: NFA or DFA or GNFA) -> None:
        print(fa)
        fa.graph()



    def generalize(self, dfa: DFA) -> GNFA:
        gen = copy.deepcopy(dfa)
        return GNFA(d=gen.desc, E=gen.sigma, Q=gen.Q, nQ=gen.nQ, s=gen.start, a=gen.accept)
    
    def collapseGNFA(self, gnfa: GNFA):
        while gnfa.nQ > 2:
            gnfa.collapse()
    
    def proceduralCollapse(self, gnfa: GNFA) -> GNFA:
        gnfa = copy.deepcopy(gnfa)
        self.plot(gnfa)
        while gnfa.nQ > 2:
            try:
                ind = int(input('Enter index of state to remove (0 - {}): '.format(gnfa.nQ - 3))) + 1
            except:
                raise Exception('Must enter numerical index in provided range')
            gnfa.collapse(index=ind)
            self.plot(gnfa)

        return gnfa
    
    def concatNFA (self, nfaA: NFA, nfaB: NFA) -> NFA:
        ret = copy.deepcopy(nfaA)
        conc = copy.deepcopy(nfaB)
        ret.concat(conc)

        return ret
    
    def unionNFA (self, nfaA: NFA, nfaB: NFA) -> NFA:
        ret = copy.deepcopy(nfaA)
        uni = copy.deepcopy(nfaB)
        ret.union(uni)

        return ret
    
    def starNFA (self, nfa: NFA) -> NFA:
        ret = copy.deepcopy(nfa)
        ret.star()

        return ret
    



if __name__ == '__main__':

    b = Builder()
    nfa0 = b.parseNFA('./models/nfa/nfa_config0.xml')
    nfa1 = b.parseNFA('./models/nfa/nfa_config1.xml')

    nfa0u1 = b.unionNFA(nfa0, nfa1)
    print(nfa0u1)
    print(nfa0u1.process_string('0'))
    print(nfa0u1.process_string('1'))

    print(nfa0)
    print(nfa1)

    print(nfa0.process_string('0'))
    print(nfa1.process_string('0'))