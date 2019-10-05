
import os
import time

fast_downward_exec_loc = "~/FastDownward/fast-downward.py"
fd_heuristic_config = "--heuristic \"hff=ff()\" --heuristic \"hcea=cea()\" --search \"lazy_greedy([hff, hcea], preferred=[hff, hcea])\""
domain_file_loc = "./v6_abstract_graph_domain_file.pddl"
problem_file_loc = "./v6_abstract_graph_problem_file.pddl"


# problem_file_loc = "./problem_logistics_c4_s3_p1_a1.pddl"
# domain_file_loc = "./logistics_domain.pddl"

solution_file_loc = "./abstract_graph_solution.txt"

# ---NOW we have the problem files ,lets generate the solutions with fast downward
fd_command = fast_downward_exec_loc + " " + domain_file_loc + " " + problem_file_loc + " " +fd_heuristic_config
# print(fd_command)

start_time = time.time()
os.system(fd_command + " > " + solution_file_loc)
print(time.time() - start_time)

