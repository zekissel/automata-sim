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

    def collapse(self, index=0):
        if (self.nQ <= 2):
            raise Exception('GNFA fully collapsed')
        
        sender = {}
        receiver = {}

        for sym in self.sigma:
            if (sym in self.Q[index].keys()):
                for t in self.Q[index][sym]:
                    if (t not in receiver.keys()): receiver[t] = [sym]
                    else: receiver.append(sym)

        for i, state in enumerate(self.Q):
            if i >= self.nQ - 2: break
            for sym in self.sigma:
                if (sym in state.keys() and index in state[sym]):
                    if ('s' not in sender.keys()): sender['s'] = []
                    if (i not in sender.keys()): sender[i] = []
                    if state['id'] == 's': sender['s'].append(sym)
                    else: sender[i].append(sym)

        for sym in self.sigma:
            if sym in self.Q[self.nQ - 1].keys() and index in self.Q[self.nQ - 1][sym]:
                if ('a' not in receiver.keys()): receiver['a'] = []
                receiver['a'].append(sym)
            if sym in self.Q[self.start].keys() and index in self.Q[self.start][sym]:
                if ('s' not in sender.keys()): sender['s'] = []
                sender['s'].append(sym)


        s_ind = [s for s in sender.keys()]
        r_ind = [r for r in receiver.keys()]
        starsym = None
        if index in s_ind and index in r_ind:
            starsym = [sym for sym in self.sigma if sym in self.Q[index] and index in self.Q[index][sym]]
        if starsym is not None:
            for i, s in enumerate(starsym):
                if len(s) == 1: starsym[i] = s + '*'
                else: starsym[i] = "(" + s + ")*"

        sender = {ind: sym for ind, sym in sender.items() if ind != index}
        receiver = {ind: sym for ind, sym in receiver.items() if ind != index}

        new_trans = {}
        for s in sender.keys():
            for r in receiver.keys():
                if len(sender[s]) > 1: 
                    sender[s] = [t for t in sender[s] if t != 'e']
                    send = "(" + 'U'.join(sender[s]) + ")"
                if len(sender[s]) == 1: send = sender[s][0]
                elif len(sender[s]) == 0: send = ''

                if len(receiver[r]) > 1: 
                    receiver[r] = [t for t in receiver[r] if t != 'e']
                    receive = "(" + 'U'.join(receiver[r]) + ")"
                if len(receiver[r]) == 1: receive = receiver[r][0]
                elif len(receiver[r]) == 0: receive = ''

                if starsym is not None and len(starsym) == 1: star = starsym[0]
                elif starsym is not None: star = "(" + 'U'.join(starsym) + ")"
                else: star = ''

                new_sym = send + star + receive
                new_sym = new_sym.replace('e', '')
                new_trans[str(s) + str(r)] = new_sym

        for s in new_trans.values():
            self.sigma.append(s)

        for t, s in new_trans.items():
            if 's' in list(t) and 'a' in list(t):
                self.Q[self.start][s] = [self.accept[0]]
            elif 's' in list(t) or 'a' in list(t):
                if 's' in list(t): self.Q[self.start][s] = [int(list(t)[1])]
                else: self.Q[int(list(t)[0])][s] = [self.accept[0]]
            else:
                ind = [int(t) for t in list(t)]
                self.Q[ind[0]][s] = [ind[1]]
        
        
        del self.Q[index]
        for state in self.Q:
            for sym in self.sigma:
                if (sym in state.keys()):
                    trans = state[sym]
                    for i, t in enumerate(trans):
                        if type(t) == int and t != index: trans[i] = t - 1
                        elif (type(t) == int and t == index): del trans[i]
                        else: 
                            for s in state.keys():
                                if (s != 'id' and s != 'e') and 'a' in state[s]: \
                                state['e'] = []
        self.nQ -= 1
        self.start -= 1
        self.accept = [a - 1 for a in self.accept]

        for s in self.Q[self.start].keys():
            if (s != 'id' and s != 'e') and 'a' in self.Q[self.start][s]: self.Q[self.start]['e'] = []

        
    def graph (self):
        nfa_graph = nx.DiGraph()

        nodes = [state['id'] for state in self.Q]
        nfa_graph.add_nodes_from(nodes)

        temp_n = [s['id'] for s in self.Q]

        e_edge_labels = {}
        edge_labels = {}
        for state in self.Q:
            for sym in self.sigma:
                if (sym in state.keys()):
                    for trans in state[sym]:
                        if type(trans) == int:
                            if (sym == 'e' and (state['id'], temp_n[trans]) not in e_edge_labels.keys()): e_edge_labels[(state['id'], temp_n[trans])] = 'ε'

                            elif (sym != 'e' and (state['id'], temp_n[trans]) not in edge_labels.keys()): edge_labels[(state['id'], temp_n[trans])] = sym

                            else: edge_labels[(state['id'], temp_n[trans])] = sym + 'U' + edge_labels[(state['id'], temp_n[trans])]
                        else:
                            if (sym == 'e' and (state['id'], 'a') not in e_edge_labels.keys()): e_edge_labels[(state['id'], 'a')] = 'ε'

                            elif (sym != 'e' and (state['id'], 'a') not in edge_labels.keys()): edge_labels[(state['id'], 'a')] = sym

                            else: edge_labels[(state['id'], 'a')] = sym + 'U' + edge_labels[(state['id'], 'a')]
        
        edgelist = list(edge_labels.keys())
        edgeliste = list(e_edge_labels.keys())
        labels = {node: node for node in nfa_graph.nodes()}

        self_edge = {e: l + '\n\n' for e, l in edge_labels.items() if e[0] == e[1]}
        sedgelist = list(self_edge.keys())

        edge_labels = {e: l for e, l in edge_labels.items() if e not in sedgelist}
        edgelist = [e for e in edgelist if e not in sedgelist]

        node_color = ['#CCC' for n in nfa_graph.nodes()]
        for ind in self.accept:
            node_color[ind] = '#898'
        
        pos=nx.spring_layout(nfa_graph)
        
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=self_edge, label_pos=1, font_size=10, verticalalignment='bottom', alpha=.8)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=sedgelist)

        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)

        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels, label_pos=0.7)
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=e_edge_labels, label_pos=0.7, font_color='#444')

        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=edgelist, arrowsize=13)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1, style='--', edge_color='#333', alpha=.7, edgelist=edgeliste)

        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)
        

        plt.figlegend
        plt.show()