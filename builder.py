from nondetfinauto import NFA
from detfinauto import DFA
import copy

class Builder:

    def __init__(self) -> None:
        pass

    def parseDFA (self, filepath: str) -> DFA:
        dfa = DFA(filepath=filepath)
        return dfa

    def parseNFA (self, filepath: str) -> NFA:
        nfa = NFA(filepath=filepath)
        return nfa
    
    def plot (self, fa: NFA or DFA) -> None:
        print(fa)
        fa.graph()
    
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