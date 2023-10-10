from lxml import etree
import networkx as nx
import matplotlib.pyplot as plt

class NFA:

    def __init__(self, desc=None, sigma=[], Q=[], nQ=0, start=None, accept=[]):
        self.desc = desc
        self.sigma = sigma
        self.Q = Q
        self.nQ = nQ
        self.start = start
        self.accept = accept

    def __repr__(self) -> str:
        return "NFA ({})\n[s: {}; a: {}]: \n{}".format(self.desc, self.start, self.accept, '\n'.join([str(s) for s in self.Q]))
    
    def graph (self):
        
        nfa_graph = nx.DiGraph()

        nodes = [state['id'] for state in self.Q]
        nodes.append('start')
        nfa_graph.add_nodes_from(nodes)

        edge_labels = {}
        for state in self.Q:
            for sym in self.sigma:
                if (sym in state.keys()):
                    for trans in state[sym]:
                        if (trans >= 0):
                            edge_labels[(state['id'], 'q' + str(trans))] = sym
        
        edgelist = list(edge_labels.keys())
        labels = {node: node for node in nfa_graph.nodes()}

        node_color = ['#CCC' for n in nfa_graph.nodes()]
        node_color[-1] = '#FFF'
        for ind in self.accept:
            node_color[ind] = '#787'
        
        pos=nx.spring_layout(nfa_graph)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=edgelist)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1, style='--', edgelist=[('start','q' + str(self.start))])
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12, font_color="black")
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)

        plt.show()

    

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
                    
                output = trans.find('output').text.split(',')
                output = [int(o) for o in output]
                for o in output:
                    if (o >= self.nQ or o < -1):
                        raise Exception('Cannot transition to a state outside of max range')
                    
                s[trans.find('input').text] = output
            self.Q.append(s)

        return self
        

    def process_string (self, input: str) -> bool:
        
        state_tree = []
        state_tree.append([self.start])

        test_sigma = [sym for sym in self.sigma if sym != 'e']
        for sym in list(input):
            if sym not in test_sigma: raise Exception('Input contains symbols not in sigma')

        # inspect each symbol of input string
        for i, symbol in enumerate(input):
            level = []
            # inspect each node of state tree at current place in string
            for state in state_tree[i]:
                if 'e' in self.Q[state].keys():
                    for trans in self.Q[state]['e']:
                        # append to end of 2nd loop from outside
                        if (trans > -1): state_tree[i].append(trans)
                if symbol in self.Q[state].keys():
                    for trans in self.Q[state][symbol]:
                        level.append(trans)
            states = []
            states = [s for s in level if (s not in states and s > -1)]
            if (len(states) < 1): return False
            else: state_tree.append(states)


        for state in state_tree[-1]:
            if state in self.accept: return True

        return False
    
    # concatenate two NFA (argument is unchanged)
    def concat (self, NFA2):
        for state in NFA2.Q:
            self.Q.append(state)

        self.desc = self.desc + ' ⚬ ' + NFA2.desc

        for ind in self.accept:
            self.Q[ind]['e'].append(self.nQ + NFA2.start)

        # change name and transition indexes of appended automata
        for i in range(self.nQ, self.nQ + NFA2.nQ):
            self.Q[i]['id'] = 'q' + str(i)
            for trans in self.sigma:
                self.Q[i][trans] = [t + self.nQ for t in self.Q[i][trans] if t >= 0]

        self.accept = [a + self.nQ for a in NFA2.accept]
        self.nQ = self.nQ + NFA2.nQ

        
    def union (self, NFA2):
        self.desc = '({} U {})'.format(self.desc, NFA2.desc)

        for state in NFA2.Q:
            self.Q.append(state)

        for i in range(self.nQ + NFA2.nQ):
            self.Q[i]['id'] = 'q' + str(i + 1)
            for trans in self.sigma:
                if (i >= self.nQ):
                    self.Q[i][trans] = [t + self.nQ + 1 for t in self.Q[i][trans] if t >= 0]
                else: self.Q[i][trans] = [t + 1 for t in self.Q[i][trans] if t >= 0]

        self.accept = [a + 1 for a in self.accept]
        app_acc = [a + self.nQ + 1 for a in NFA2.accept]
        for acc in app_acc:
            self.accept.append(acc)

        self.Q.insert(0, {'id': 'q0', '0': [], '1': [], 'e': [self.start + 1, NFA2.start + self.nQ + 1]})
        self.nQ = self.nQ + NFA2.nQ + 1
        self.start = 0

    
    def star (self):
        self.desc = '({})*'.format(self.desc)

        for s in self.accept: self.Q[s]['e'].append(self.start)
        for i in range(self.nQ):
            self.Q[i]['id'] = 'q' + str(i + 1)
            for sym in self.sigma:
                self.Q[i][sym] = [s + 1 for s in self.Q[i][sym] if s >= 0]
        self.Q = [{'id':'q0','0':[],'1':[],'e':[self.start + 1]}] + self.Q
        
        self.nQ += 1
        self.accept = [a + 1 for a in self.accept]
        self.accept = [0] + self.accept
        self.start = 0


        
        


if __name__ == '__main__':

    nfa = NFA()
    nfa.parse_from_xml('models/nfa/nfa_config.xml')
    print(nfa.__repr__())
    print(nfa.process_string('001'))
    print(nfa.process_string('110'))
    print(nfa.process_string('01'))

    nfa1 = NFA()
    nfa1.parse_from_xml('models/nfa/nfa_config1.xml')
    nfa1.star()
    print(nfa1.__repr__())
    print(nfa1.process_string('0000'))