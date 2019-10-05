"""

Generates problem and domain file

"""
import pickle
import networkx as nx

pickle_source_file = "abstract_graph_domain.p"
problem_file_name = "v5_abstract_graph_problem_file.pddl"

with open(pickle_source_file,"rb") as src:
    state_graph = pickle.load(src)
    edge_propositions = pickle.load(src)
    all_possible_propositions = pickle.load(src)
    operators = pickle.load(src)
    ordered_all_random_prop_names = pickle.load(src)
    dict_prop_to_value_range = pickle.load(src)


# generate problem file, choose any "x_" state as starting state, and set goal to any x value
problem_file_string = \
    "(define (problem base-abstract_graph) \n\
    (:domain abstract-graph) \n\
    (:objects "

all_values = set()
for prop in edge_propositions:
    all_values.update(set(prop.split("_end_")[1].split("_")))

problem_file_string += " ".join(list(all_values))

problem_file_string += ")\n "
problem_file_string += "(:init \n "

#now setup the initial state. For each property set a value. The value is set by the property range of that property
#todo make this randomly choose a value rather than determinisitically
for single_item in dict_prop_to_value_range.items():
    problem_file_string += "(" + single_item[0] + " v" +str(single_item[1][0]) + ")\n"


string_edge_props = set()
for single_edge_proposition in edge_propositions:
    string_edge_props.add("(" + single_edge_proposition.split("_end_")[0] + " " + \
                           " ".join(single_edge_proposition.split("_end_")[1].split("_")) + ") \n")
for single_string_edge_prop in string_edge_props:
    problem_file_string += single_string_edge_prop


problem_file_string += ")\n" #close the init block


#set the goal
problem_file_string += "(:goal \n "
problem_file_string += "(and \n "
#todo make this randomized
problem_file_string += "(propx v9) \n"
problem_file_string += ")\n" #end "and"
problem_file_string += ")" #end "goal:

problem_file_string += "\n)" #close the domain file

with open(problem_file_name, "w") as problem_dest:
    problem_dest.write(problem_file_string)






