"""
100 (or so) nodes, each with some unique value of the properties


"""

import networkx as nx
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import itertools
import random
import pickle
import copy



# todo NEXT TRY ADDING SUBGRAPHS !! easy ! DUPLICATE the graph,
#     i think this will work well !! why ? because many more cases to try in each action, and many more restrictions.
#
# todo FIRST do EMBED PLANNER with new embeddings. on the 14 properties problem. Real easy.
# MAYBE easier to go direct from the graph OR EDGE PROPOSITIONS, which map to actions and precond and effects

pickle_dest_file_name = "abstract_graph_domain.p"
num_rand_properties = 5 #prop1, prop2 etc. #INCREASES time the most (exponentially). So the number of actions affects it.
value_ranges = [[0,1]] * num_rand_properties #can be diff range of values too, Increases time by very little
dict_prop_to_value_range = {}
odds_of_edge = 0.125 #increases time moderately
odds_of_core_node_transition = 0.0005 #barely affects time taken by Fast Downward
num_rand_nodes = 100 #increase time moderately


state_graph = nx.Graph()
#can add special or specific states and properties here. Afterwards its all random generation

num_x_property_graph_nodes = 10 #also the length of the x property
x_prop_nodes = set()
prop_dict = {}
true_edge_propositions = []
dict_prop_to_value_range["propx"] = list(range(num_x_property_graph_nodes))



for i in range(num_x_property_graph_nodes-1):
    prop_dict["x_"+str(i)] = {"propx":i}
    prop_dict["x_"+str(i+1)] = {"propx":i+1}
    state_graph.add_edge("x_" + str(i), "x_" + str(i + 1))
    x_prop_nodes.add("x_"+str(i))
    x_prop_nodes.add("x_"+str(i+1))
    true_edge_propositions.append("Allow_propx_end_" + "v" + str(i) + "_" + "v" + str(i + 1))

#add N random nodes
rand_nodes = set()
for i in range(num_rand_nodes):
    node_name = "rand"+str(i)
    rand_nodes.add(node_name)
    state_graph.add_node(node_name)
    prop_dict[node_name] = {"propx": 100*random.choice(range(1,num_x_property_graph_nodes+1))}
    #add a random instance of the properties
    random_prop_values_dict = {"prop"+str(x):random.choice(value_ranges[x]) for x in range(len(value_ranges))}
    prop_dict[node_name] = {**prop_dict[node_name],**random_prop_values_dict}
#end for loop


ordered_all_random_prop_names = ["prop" + str(i) for i in range(num_rand_properties)]
dict_prop_to_value_range = {**dict_prop_to_value_range ,
                            **{"prop" + str(i): value_ranges[i] for i in range(num_rand_properties)}} #merge dicts


#Also assign these extra properties to the x_nodes

for node_name in x_prop_nodes:
    random_prop_values_dict = {"prop" + str(x): random.choice(value_ranges[x]) for x in range(len(value_ranges))}
    prop_dict[node_name] = {**prop_dict[node_name], **random_prop_values_dict}
#end for loop

nx.set_node_attributes(state_graph, prop_dict)


#now connect randomly,
for node_a in state_graph.nodes():
    for node_b in state_graph.nodes():
        if node_a == node_b or (node_a in x_prop_nodes and node_b in x_prop_nodes):
            continue
        core_node = False
        if node_a in x_prop_nodes or node_b in x_prop_nodes:
            if random.random() > odds_of_core_node_transition:
                continue
            core_node = True
        elif random.random() > odds_of_edge: #failure check, not pass check
            continue
        #else we add an edge, the proposition and associated operator
        #create the proposition that will allow this transition
        differences = [int(prop_dict[node_a][x] != prop_dict[node_b][x]) for x in ordered_all_random_prop_names]

        #do 'allow" difference prop names and prior posterior values for each of the diffs.
        indices = [i for i, x in enumerate(differences) if x == 1]
        #these are the indicies
        if core_node: #i.e. atleast one of them is a core node, if both were, the iter would have reset and not made it this far
            indices = ["x"] + indices #the x property is gauranteed to be different. The random nodes have a different range of x values
        if len(indices) == 0:
            continue
        new_proposition = "Allow"
        for index in indices:
            new_proposition += "_prop" + str(index)
        new_proposition += "_end"
        for index in indices:
            if type(index) == int:
                new_proposition += "_"+"v"+str(prop_dict[node_a][ordered_all_random_prop_names[index]])\
                                                        +"_"+"v"+str(prop_dict[node_b][ordered_all_random_prop_names[index]])
            else:
                new_proposition += "_"+"v"+str(prop_dict[node_a]["prop"+index])\
                                                        +"_"+"v"+str(prop_dict[node_b]["prop"+index])
        #todo NOTE this is to make it bidirectional
        # WEIRDLY it makes FD slightly faster. But no real difference.
        # for index in indices:
        #     if type(index) == int:
        #         new_proposition += "_"+"v"+str(prop_dict[node_b][ordered_all_random_prop_names[index]])\
        #                                                 +"_"+"v"+str(prop_dict[node_a][ordered_all_random_prop_names[index]])
        #     else:
        #         new_proposition += "_"+"v"+str(prop_dict[node_b]["prop"+index])\
        #                                                 +"_"+"v"+str(prop_dict[node_a]["prop"+index])



        if node_a in x_prop_nodes or node_b in x_prop_nodes:
            print(new_proposition)
        true_edge_propositions.append(new_proposition)
        state_graph.add_edge(node_a,node_b)

        #todo add operator here, rather than all possible operator
#end for loop through adding edges



# plt.subplot(111)
# pos = nx.kamada_kawai_layout(state_graph)
# labels = {x:str(x) for x in pos.keys()}
# nx.draw(state_graph, pos = pos)
# nx.draw_networkx_labels(state_graph, pos, labels, font_size=16)
# plt.show()

#now add the operators
operators = []
all_properties = ["propx"] + ordered_all_random_prop_names
possible_prop_indices = list(range(num_rand_properties+1)) #+1 because we include the x property
def build_op_strings(op_size_left,possible_prop_indices, all_properties):
    if op_size_left == 0:
        return [""]
    allowed_indices = possible_prop_indices[:-(op_size_left-1)]
    if -(op_size_left-1) == -0: #if we are down to the last entry, then we allow all possible indices left over
        allowed_indices = possible_prop_indices

    all_op_strings = []
    for curr_op_prop_index in allowed_indices: #need atleast opsize_left-1 in the remainder list to recurse.
        left_indices = copy.deepcopy(possible_prop_indices)
        left_indices = left_indices[left_indices.index(curr_op_prop_index)+1:]
        op_string = "_" + all_properties[curr_op_prop_index]
        all_suffixes = build_op_strings(op_size_left-1,left_indices, all_properties)
        all_op_strings += [op_string+x for x in all_suffixes]
    #end for loop
    return all_op_strings
#end def

#---NOW call the recursive function to build operators of all sizes
for op_size in range(1,num_rand_properties+1):
    op_string = "op"
    all_suffixes = build_op_strings(op_size,possible_prop_indices,all_properties)
    for op_name in [op_string+x for x in all_suffixes]:
        operators.append(op_name)
#end for loop

#ADD all possible propositions to the all_possible_prop_list
all_possible_prop_list = []
for op_string in operators:
    curr_prop_string = copy.deepcopy(op_string)
    curr_prop_string = curr_prop_string.replace("op_","Allow_")
    all_possible_prop_list.append(curr_prop_string)




# print(len(true_edge_propositions), true_edge_propositions)

with open(pickle_dest_file_name,"wb") as dest:
    pickle.dump(state_graph, dest)
    pickle.dump(true_edge_propositions, dest)
    pickle.dump(all_possible_prop_list, dest)
    pickle.dump(operators,dest)
    pickle.dump(ordered_all_random_prop_names,dest)
    pickle.dump(dict_prop_to_value_range,dest)

print("NUM NODES =", len(state_graph.nodes))


#todo make these function calls, it is a terrible way of executing 3 scripts in order
import Graph_to_domainPddl
print("a")
import Graph_to_problemPddl
print("b")
import Testing_abstract_graph
print("c")
