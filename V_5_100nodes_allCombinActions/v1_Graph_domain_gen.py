"""

THINK combining position (motion) and task where it is interconnected and not separable into task and motion plans

x_nodes are position nodes. Think of a robot navigating through a building. Or in this case a linear path.
At each step it can do other things that change it's state. It can hitch a ride with another robot, it can ask a human to help.
and do so many other things. It LOSES it's position in the linear path when this is done, and returning back is hard.

THE STATE GRAPH is NOT what the PETRI-NET (fluent action) embedding/graph will look like

The x_position fluent will be singly linked between it's neighbors.


"""

import networkx as nx
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import itertools
import random
import pickle

pickle_dest_file_name = "abstract_graph_domain.p"
num_properties = 9 #prop1, prop2 etc.
value_ranges = [[0,1]]*num_properties #can be diff range of values too
dict_prop_to_value_range = {}
odds_of_edge = 0.125
odds_return_to_x = 0.1
num_props_per_operator = 2 #so an operator changes 2 properties. (can change only 1 value, but conditioned on two)


state_graph = nx.DiGraph()
#can add special or specific states and properties here. Afterwards its all random generation

num_x_property_graph_nodes = 20 #also the length of the x property
x_prop_nodes = set()
prop_dict = {}
edge_propositions = []
dict_prop_to_value_range["propx"] = list(range(num_x_property_graph_nodes))

for i in range(num_x_property_graph_nodes-1):
    prop_dict["x_"+str(i)] = {"propx":i}
    prop_dict["x_"+str(i+1)] = {"propx":i+1}
    state_graph.add_edge("x_" + str(i), "x_" + str(i + 1))
    x_prop_nodes.add("x_"+str(i))
    x_prop_nodes.add("x_"+str(i+1))
    edge_propositions.append("Allow_propx_end_" + "v"+str(i) + "_" + "v"+str(i+1))


#now we have nodes x_0 to x_n connected by edges in between

# plt.subplot(111)
# pos = nx.kamada_kawai_layout(base_graph)
# labels = {x:str(x) for x in pos.keys()}
# nx.draw(base_graph,pos = pos)
# nx.draw_networkx_labels(base_graph,pos,labels,font_size=16)
# plt.show()



#generate nodes for each possible value. so 2^num_properties.
all_nodes_properties = [[x,y] for x in value_ranges[0] for y in value_ranges[1]]
for i in range(2,len(value_ranges)):
    all_nodes_properties = [x + [y] for x in all_nodes_properties for y in value_ranges[i]]
#end for
num_random_property_cases = len(all_nodes_properties)
# print(len(all_nodes_properties),list(all_nodes_properties))
# print(value_ranges)
ordered_all_random_prop_names = ["prop" + str(i) for i in range(num_properties)]
dict_prop_to_value_range = {**dict_prop_to_value_range ,
                            **{"prop" + str(i): value_ranges[i] for i in range(num_properties)}} #merge dicts
for i in range(len(all_nodes_properties)):
    node_name = "Rand_"+str(i)
    state_graph.add_node(node_name)
    prop_values = all_nodes_properties[i]
    node_properties_dict = {"prop"+str(i):prop_values[i] for i in range(num_properties)}
    prop_dict[node_name] = node_properties_dict

#Also assign these extra properties to the x_nodes

for a_node in x_prop_nodes:
    prop_values = all_nodes_properties[random.choice(range(num_random_property_cases))]
    node_properties_dict = {"prop" + str(i): prop_values[i] for i in range(num_properties)}
    prop_dict[a_node] = {**prop_dict[a_node], **node_properties_dict} #merge dicts
#end for loop

nx.set_node_attributes(state_graph, prop_dict)


for a_node in state_graph.nodes():
    for b_node in state_graph.nodes():
        if a_node == b_node or (a_node in x_prop_nodes and b_node in x_prop_nodes):
        # if a_node == b_node or (b_node in x_prop_nodes):
            continue
        #check if x and y are 1 or 2 attributes apart, only then can they be connected
        differences = [int(prop_dict[a_node][x] != prop_dict[b_node][x]) for x in ordered_all_random_prop_names]
        if sum(differences)!= num_props_per_operator:
            continue
        if b_node in x_prop_nodes: #then it is returning to an x (position) node
            if random.random() > odds_return_to_x:
                continue
        else: #it is just a standard edge
            if random.random() > odds_of_edge:
                continue
        #else we have an operator to transition the two states.
        #find the properties and add the allowable transition propositions
        indices = [i for i, x in enumerate(differences) if x == 1]
        #these are the indicies
        new_proposition = "Allow"
        for index in indices:
            new_proposition += "_prop" + str(index)
        new_proposition += "_end"
        for index in indices:
            new_proposition += "_"+"v"+str(prop_dict[a_node][ordered_all_random_prop_names[index]])\
                                                    +"_"+"v"+str(prop_dict[b_node][ordered_all_random_prop_names[index]])
        edge_propositions.append(new_proposition)
        state_graph.add_edge(a_node, b_node)
    #end inner for
#end outer for

# plt.subplot(111)
# pos = nx.kamada_kawai_layout(state_graph)
# labels = {x:str(x) for x in pos.keys()}
# nx.draw(state_graph, pos = pos)
# nx.draw_networkx_labels(state_graph, pos, labels, font_size=16)
# plt.show()


#Create operators for each pair of properties.
operators = []
#todo extend this to allow 3 props per operator and such.
prop_pairs = [(x,y) for x in range(num_properties) for y in range(x+1,num_properties)]
for single_pair in prop_pairs:
    operator_name = "op" + "_prop" + str(single_pair[0])+ "_prop" + str(single_pair[1])
    operators.append(operator_name)
operator_name = "op" + "_propx"
operators.append(operator_name)

print(edge_propositions)

with open(pickle_dest_file_name,"wb") as dest:
    pickle.dump(state_graph, dest)
    pickle.dump(edge_propositions,dest)
    pickle.dump(operators,dest)
    pickle.dump(ordered_all_random_prop_names,dest)
    pickle.dump(dict_prop_to_value_range,dest)






# For each node, and action applicable on it, decide if a transition is
# permissible to another node based on odds_of_edge


#display graph
