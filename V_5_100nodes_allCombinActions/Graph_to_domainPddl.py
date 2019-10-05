"""

Generates problem and domain file

"""
import pickle
import networkx as nx


pickle_source_file = "abstract_graph_domain.p"
domain_file_name = "v5_abstract_graph_domain_file.pddl"

with open(pickle_source_file,"rb") as src:
    state_graph = pickle.load(src)
    edge_propositions = pickle.load(src)
    all_possible_propositions = pickle.load(src)
    operators = pickle.load(src)
    ordered_all_random_prop_names = pickle.load(src)


# generate problem file, choose any "x_" state as starting state, and set goal to any x value
domain_file_string = \
    "(define (domain abstract-graph) \n\
        (:requirements :strips) \n\
         (:predicates 	\n "

#insert all the proposition types into the predicates requirement
#collect all the propositions by splitting by "_end_" and taking the prefix.
string_addendum = " (propx "
string_addendum += " ?propValue"
string_addendum += ") \n "
domain_file_string += string_addendum
for single_prop_name in ordered_all_random_prop_names:
    string_addendum = " (" + single_prop_name
    string_addendum += " ?propValue"
    string_addendum += ") \n "
    domain_file_string += string_addendum

edge_prop_names = set()
# for prop in edge_propositions:
for prop in all_possible_propositions:
    edge_prop_names.add(prop.split("_end_")[0])
#end for loop

# for single_prop_name in edge_prop_names:
for single_prop_name in all_possible_propositions:
    string_addendum = " (" + single_prop_name
    num_vars = len(single_prop_name.split("_"))-1
    for i in range(num_vars):
        string_addendum += " ?prior_prop" + str(i)
        string_addendum += " ?post_prop" + str(i)
    #end inner for
    string_addendum += ") \n "
    domain_file_string += string_addendum
#end outer for
domain_file_string += ") \n "


#now add the actions
# "op_prop0_prop3" and "op_x"
for single_operator in operators:
    action_string = "\n(:action " + single_operator + " \n"
    action_string += ":parameters ("
    parts = single_operator.split("_")
    num_vars = len(parts) - 1
    vars = parts[1:]
    for single_var in vars:
        action_string += "\n ?prior_"+single_var
        action_string += "\n ?post_"+single_var
    action_string += ")\n"
    action_string += ":precondition \n (and"
    #add the allows transition condition
    action_string += " (Allow" + "".join(["_"+single_var for single_var in vars])
    for single_var in vars:
        action_string += " ?prior_"+single_var
        action_string += " ?post_"+single_var
    action_string += ") "
    #now add the conditions that the prior values are true
    for single_var in vars:
        action_string += " ("+ single_var+ " ?prior_"+single_var + ") "

    action_string += ")\n"
    action_string += ":effect \n (and"
    for single_var in vars:
        action_string += " (not ("+ single_var+ " ?prior_"+single_var + ") ) "
    for single_var in vars:
        action_string += " ("+ single_var+ " ?post_"+single_var + ") "
    action_string += "))\n"

    domain_file_string += action_string
#end for loop through the actions

domain_file_string += "\n)" #close the domain file

with open(domain_file_name,"w") as domain_dest:
    domain_dest.write(domain_file_string)


print("Domain file generated")
