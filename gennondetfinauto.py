import networkx as nx
import matplotlib.pyplot as plt

class GNFA:

    def __init__(self, d=None, E=[], Q=[], nQ=0, s=None, a=[]) -> None:
        if d is not None and E != [] and Q != [] and nQ > 0 and a != []:
            self.desc = d
            self.sigma = E
            self.Q = Q
            self.nQ = nQ
            self.start = s
            self.accept = a

    def __repr__(self) -> str:
        return "GNFA {}\n{}".format(self.desc, '\n'.join([str(s) for s in self.Q]))

    def collapse(self, index=1):
        if (self.nQ <= 2):
            raise Exception('GNFA fully collapsed')
        
        print('test collapse')

        
    def graph (self):
        nfa_graph = nx.DiGraph()

        nodes = [state['id'] for state in self.Q]
        nfa_graph.add_nodes_from(nodes)

        e_edge_labels = {}
        edge_labels = {}
        for state in self.Q:
            for sym in self.sigma:
                if (sym in state.keys()):
                    for trans in state[sym]:
                        if trans == 'a':
                            if (sym == 'e'): e_edge_labels[(state['id'], 'a')] = 'ε'
                            else: edge_labels[(state['id'], 'a')] = sym
                        elif (trans >= 0):
                            if (sym == 'e'): e_edge_labels[(state['id'], 'q' + str(trans))] = 'ε'
                            else: edge_labels[(state['id'], 'q' + str(trans))] = sym
        
        edgelist = list(edge_labels.keys())
        edgeliste = list(e_edge_labels.keys())
        labels = {node: node for node in nfa_graph.nodes()}

        self_edge = {e: l + '\n\n' for e, l in edge_labels.items() if e[0] == e[1]}
        sedgelist = list(self_edge.keys())

        edgelist = [e for e in edgelist if e not in sedgelist]

        node_color = ['#CCC' for n in nfa_graph.nodes()]
        for ind in self.accept:
            node_color[ind] = '#898'
        
        pos=nx.spring_layout(nfa_graph)
        
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=self_edge, label_pos=1, font_size=10, verticalalignment='bottom', alpha=.8)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=sedgelist)

        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)

        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=edgelist, arrowsize=13)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1, style='--', edge_color='#333', alpha=.7, edgelist=edgeliste)

        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels, label_pos=0.7)
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=e_edge_labels, label_pos=0.7, font_color='#444')

        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)
        

        plt.figlegend
        plt.show()