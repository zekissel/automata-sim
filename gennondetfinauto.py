import networkx as nx
import matplotlib.pyplot as plt

class GNFA:

    def __init__(self, d=None, E=[], Q=[], nQ=0, s=None, a=[]) -> None:
        if d is not None and E != [] and Q != [] and nQ > 0:
            self.desc = d
            self.sigma = E
            self.Q = Q
            self.nQ = nQ
            self.start = s
            self.accept = a
            
            self.shift()
    

    # convert states transitions from { 'symbol': 'target_index' }
    #                              to { (cur_id, target_id): 'symbol' }
    # add state 's' with ε transition to start state
    # add state 'a' receiving ε trans from all accept states
    def shift (self):
        for s in self.Q: 
            if s['id'] == 's': return

        zero = self.sigma[0]
        one = self.sigma[1]

        newQ = [{'id':'s', ('s', self.Q[self.start]['id']):'e'}]
        for i, state in enumerate(self.Q):
            newS = {'id': state['id']}
            if state[zero] == state[one]:
                newS[(state['id'], 'q' + state[zero])] = zero + 'U' + one
            else:
                newS[(state['id'], 'q' + str(state[zero]))] = zero
                newS[(state['id'], 'q' + str(state[one]))] = one

            if i in self.accept: newS[(state['id'], 'a')] = 'e'
            newQ.append(newS)
        newQ.append({'id':'a'})
        
        self.Q = newQ
        self.nQ = len(newQ)
        self.sigma.append('e')
        self.start = 0
        self.accept = self.nQ - 1


    def __repr__(self) -> str:
        return "GNFA {}\n{}".format(self.desc, '\n'.join([str(s) for s in self.Q]))


    # remove state at specified index from automata
    def collapse(self, index=1):
        if (self.nQ <= 2): raise Exception('GNFA fully collapsed')
        if index < 1 or index >= self.nQ - 1: raise Exception('Index out of range for removal')
        
        # collect all transitions into and out of state at index
        # star is the symbol (if any) of the self edge at this index
        enter = {}
        star = ''
        exit = {}

        for trans, lab in self.Q[index].items():
            if trans == 'id': continue
            if trans[0] == trans[1]:
                if len(lab) > 1 and ')' in lab[2:-2]: star = '(' + lab + ')*'
                else: star = lab + '*'
            else: exit[trans] = lab

        remID = self.Q[index]['id']
        for i, state in enumerate(self.Q):
            if i == index: continue
            for trans, lab in state.items():
                if trans == 'id': continue
                if trans[1] == remID: enter[trans] = lab


        # build new transitions:
        # x enter states, y exit states = x*y new trans
        new_trans = {}
        for tran0 in enter.keys():
            for tran1 in exit.keys():
                label = enter[tran0] + star + exit[tran1]
                if len(label) > 1: label = label.replace('e', '')

                edge = (tran0[0], tran1[1])
                new_trans[edge] = label

        # update Q with new transitions
        # union if edge already exists
        # remove transitions to index state from persistings states
        rem = []
        for trans, sym in new_trans.items():
            for i, state in enumerate(self.Q):
                uni = ''
                if state['id'] != trans[0]: continue
                for edge in state.keys():
                    if edge == 'id': continue
                    if edge == trans: uni = state[edge]
                    if edge[1] == remID: rem.append((i, edge))
                
                if len(uni) > 0: state[trans] = '(' + sym + 'U' + uni + ')'
                else: state[trans] = sym
        for ind in rem: 
            if ind[1] in self.Q[ind[0]].keys(): del self.Q[ind[0]][ind[1]]
        
        del self.Q[index]
        
        self.nQ -= 1
        self.accept -= 1

        
    def graph (self):

        edge_labels = {}
        edge_labels_e = {}
        edge_labels_self = {}
        for s in self.Q:
            for e, l in s.items():
                if e == 'id': continue
                if l == 'e': edge_labels_e[e] = 'ε'
                elif e[0] == e[1]: edge_labels_self[e] = l + '\n\n'
                else: edge_labels[e] = l

        edgelist = list(edge_labels.keys())
        edgelist_e = list(edge_labels_e.keys())
        s_edgelist = list(edge_labels_self.keys())

        nodes = [state['id'] for state in self.Q]
        labels = {node: node for node in nodes}
        node_color = ['#CCC' for _ in nodes]
        node_color[self.accept] = '#898'


        nfa_graph = nx.DiGraph()
        nfa_graph.add_nodes_from(nodes)
        pos=nx.spring_layout(nfa_graph)
        
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels_self, label_pos=1, font_size=10, verticalalignment='bottom', alpha=.8)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=s_edgelist)

        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels, label_pos=0.7)
        nx.draw_networkx_edge_labels(nfa_graph, pos, edge_labels=edge_labels_e, label_pos=0.7, font_color='#444')

        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1.5, edgelist=edgelist, arrowsize=13)
        nx.draw_networkx_edges(nfa_graph, pos, connectionstyle='arc3, rad=0.15', width=1, style='--', edge_color='#333', alpha=.7, edgelist=edgelist_e)

        nx.draw_networkx_labels(nfa_graph, pos, labels, font_size=12)
        nx.draw(nfa_graph,pos, node_color=node_color, alpha=.9)

        plt.show()