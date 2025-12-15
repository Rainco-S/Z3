import argparse
import test_cases
from automerger import define_connector

'''
在终端输入
python main.py --list
python main.py --all
python main.py test_basic_01
'''


BOUND = 10 

def get_available_cases():
    """
    自动从 test_cases.py 中获取所有以 'test_' 开头的测试用例
    返回字典: {'test_basic_01': (spec_list, impl_list), ...}
    """
    cases = {}
    for name in dir(test_cases):
        if name.startswith("test_"):
            val = getattr(test_cases, name)
            if isinstance(val, tuple) and len(val) == 2:
                cases[name] = val
    return cases

def run_single_check(source_conn, target_conn, source_name, target_name):
    """
    运行单向精化检查: source <= target ?
    """
    print(f"  Checking: {source_name} <= {target_name} ...", end=" ", flush=True)
    
    result, counterexample, smt = source_conn.isRefinementOf(target_conn, BOUND)

    if result:
        print("\033[92m[TRUE]\033[0m") # 绿色 TRUE
    else:
        print("\033[91m[FALSE]\033[0m") # 红色 FALSE
        if counterexample:
            print(f"    Counter-example found:\n{counterexample}")
        else:
            print(f"    (Counter-example found by Z3)")

def run_experiment(case_name, case_data):
    """
    运行单个实验，包含两个方向的检查
    """
    spec_list, impl_list = case_data
    
    print(f"\n{'='*60}")
    print(f"Running Experiment: {case_name}")
    print(f"{'='*60}")

    # 1. 构建 Connector 对象
    res_spec = define_connector("Spec", spec_list)
    spec_conn = res_spec[0] if isinstance(res_spec, tuple) else res_spec
    
    res_impl = define_connector("Impl", impl_list)
    impl_conn = res_impl[0] if isinstance(res_impl, tuple) else res_impl

    # 2. 方向一: Implementation Refines Specification? (标准精化)
    # Impl <= Spec
    run_single_check(impl_conn, spec_conn, "Impl", "Spec")

    # 3. 方向二: Specification Refines Implementation? (反向精化)
    # Spec <= Impl
    # 如果两个方向都为 True，则证明等价
    run_single_check(spec_conn, impl_conn, "Spec", "Impl")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Reo Connector Refinement Checker")
    parser.add_argument("case_name", nargs="?", help="Name of the test case to run (e.g., test_basic_01)")
    parser.add_argument("--all", action="store_true", help="Run all test cases")
    parser.add_argument("--list", action="store_true", help="List all available test cases")
    
    args = parser.parse_args()
    available_cases = get_available_cases()

    # 1. 列出所有用例
    if args.list:
        print("Available test cases:")
        for name in sorted(available_cases.keys()):
            print(f" - {name}")
        return

    # 2. 运行所有用例
    if args.all:
        for name in sorted(available_cases.keys()):
            run_experiment(name, available_cases[name])
        return

    # 3. 运行单个用例
    if args.case_name:
        if args.case_name in available_cases:
            run_experiment(args.case_name, available_cases[args.case_name])
        else:
            print(f"Error: Test case '{args.case_name}' not found.")
            print("Use --list to see available cases.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()





# def define_connector(connector_name):
#     merger_count = 1
#     conn = Connector()
#     print(f'Start defining connector {connector_name}')

#     while True:
#         user_input = input(f"{connector_name}> ").strip()
#         if user_input.lower() == 'done':
#             break

#         parts = user_input.split()
#         channel_type = parts[0]
#         nodes = parts[1:]

#         try:
#             if channel_type == 'Merger':
#                 new_node = []
#                 src_num = len(nodes) // 2
#                 for i in range(src_num):
#                     temp = f"{nodes[src_num + i]}_{merger_count}"
#                     conn.connect(nodes[i], nodes[src_num + i], temp)
#                     new_node.append(temp)
#                     merger_count += 1

#                 new_node.append(nodes[-1])
#                 conn.connect('Merger', *new_node)
#             else:
#                 conn.connect(channel_type, *nodes)
                
#         except Exception as e:
#             print(f"Error {str(e)}")

#     return conn

# print('Type connectors according to the following rules: (name the nodes like ABC or A1B1C1)\n'
#       'Sync A B\n'
#       'Fifo1e(1) A B\n'
#       'Merger type1 type2 ... src_1 src_2 ... snk')
# print("Type 'done' to end defining current connector.")

# c1 = define_connector("c1")
# c2 = define_connector("c2")

# result1, counterexample1, smt1 = c2.isRefinementOf(c1, 10)
# result2, counterexample2, smt2 = c1.isRefinementOf(c2, 10)

# print(result1)
# print(result2)
# print(counterexample1)
# print(counterexample2)

