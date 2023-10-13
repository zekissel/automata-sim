from lxml import etree
import networkx as nx
import matplotlib.pyplot as plt

class DFA:

    def __init__(self, dfa=None, filepath=None):
        if type(dfa) == DFA:
            self.desc = dfa.desc
            self.sigma = dfa.sigma
            self.Q = dfa.Q
            self.nQ = dfa.nQ
            self.start = dfa.start
            self.accept = dfa.accept
        elif filepath is not None:
            self.parse_from_xml(filepath=filepath)

    def __repr__(self) -> str:
        return "NFA {}\n[s: {}; a: {}]: \n{}".format(self.desc, self.start, self.accept, '\n'.join([str(s) for s in self.Q]))
    
    def graph (self):
        nfa_graph = nx.DiGraph()

        nodes = [state['id'] for state in self.Q]
        nodes.append('start')
        nfa_graph.add_nodes_from(nodes)

        edge_labels = {}
        edge_labels_0 = {}
        for state in self.Q:
            for sym in self.sigma:
                if sym == self.sigma[0]:
                    if ((state['id'], 'q' + str(state[sym])) in edge_labels_0.keys()):
                        edge_labels_0[(state['id'], 'q' + str(state[sym]))].append(sym)
                    else: edge_labels_0[(state['id'], 'q' + str(state[sym]))] = [sym]
                else:
                    if ((state['id'], 'q' + str(state[sym])) in edge_labels.keys()):
                        edge_labels[(state['id'], 'q' + str(state[sym]))].append(sym)
                    else: edge_labels[(state['id'], 'q' + str(state[sym]))] = [sym]
        for edge in edge_labels.keys(): 
            edge_labels[edge] = ', '.join(edge_labels[edge])
        for edge in edge_labels_0.keys(): 
            edge_labels_0[edge] = ', '.join(edge_labels_0[edge])

        edgelist = list(edge_labels.keys())
        edgelist0 = list(edge_labels_0.keys())
        labels = {node: node for node in nfa_graph.nodes()}

        node_color = ['#CCC' for n in nfa_graph.nodes()]
        node_color[-1] = '#FFF'
        for ind in self.accept:
            node_color[ind] = '#898'

        self_edge = {e: l + '\n\n' for e, l in edge_labels.items() if e[0] == e[1]}
        self_edge_0 = {e: l + '\n\n' for e, l in edge_labels_0.items() if e[0] == e[1]}
        sedgelist = list(self_edge.keys())
        sedgelist0 = list(self_edge_0.keys())

        edgelist = [e for e in edgelist if e not in sedgelist]
        edgelist0 = [e for e in edgelist0 if e not in sedgelist0]
        
        pos=nx.spring_layout(nfa_graph)

        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=self_edge, label_pos=1, font_size=10, verticalalignment='bottom', alpha=.8)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=sedgelist)
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=self_edge_0, label_pos=1, font_color='#444', font_size=10, verticalalignment='bottom', alpha=.8)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edge_color='#444', edgelist=sedgelist0)
        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)

        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=edgelist, arrowsize=13)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.2, edge_color='#444', edgelist=edgelist0, arrowsize=13)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1, style=':', edgelist=[('start','q' + str(self.start))])
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels, label_pos=0.7)
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels_0, label_pos=0.7, font_color='#444')

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