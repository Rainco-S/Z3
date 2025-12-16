import argparse
import test_cases
from automerger import define_connector

BOUND = 10 

def get_available_cases():
    cases = {}
    for name in dir(test_cases):
        if name.startswith("test_"):
            val = getattr(test_cases, name)
            if isinstance(val, tuple) and len(val) == 2:
                cases[name] = val
    return cases

def run_single_check(source_conn, target_conn, source_name, target_name):
    """
    Check if source connector is a refinement of target connector: source <= target ?
    """
    print(f"  Checking: {source_name} <= {target_name} ...", end=" ", flush=True)
    
    result, counterexample, smt = source_conn.isRefinementOf(target_conn, BOUND)

    if result:
        print("\033[92m[TRUE]\033[0m") # Green -> TRUE
    else:
        print("\033[91m[FALSE]\033[0m") # Red -> FALSE
        if counterexample:
            print(f"    Counter-example found:\n{counterexample}")
        else:
            print(f"    (Counter-example found by Z3)")

def run_experiment(case_name, case_data):
    """
    Run a single experiment, containing two directions of checks:
    1. Implementation Refines Specification? (Impl <= Spec)
    2. Specification Refines Implementation? (Spec <= Impl)
    """
    spec_list, impl_list = case_data
    
    print(f"\n{'='*60}")
    print(f"Running Experiment: {case_name}")
    print(f"{'='*60}")

    # Model Connectors
    res_spec, _, _ = define_connector(spec_list)
    spec_conn = res_spec
    
    res_impl, _, _ = define_connector(impl_list)
    impl_conn = res_impl

    # Impl <= Spec
    run_single_check(impl_conn, spec_conn, "Impl", "Spec")

    # Spec <= Impl
    run_single_check(spec_conn, impl_conn, "Spec", "Impl")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Reo Connector Refinement Checker")
    parser.add_argument("case_name", nargs="?", help="Name of the test case to run (e.g., test_basic_01)")
    parser.add_argument("--all", action="store_true", help="Run all test cases")
    parser.add_argument("--list", action="store_true", help="List all available test cases")
    
    args = parser.parse_args()
    available_cases = get_available_cases()

    # List all available test cases
    if args.list:
        print("Available test cases:")
        for name in sorted(available_cases.keys()):
            print(f" - {name}")
        return

    # Run all test cases
    if args.all:
        for name in sorted(available_cases.keys()):
            run_experiment(name, available_cases[name])
        return

    # Run a single test case
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

