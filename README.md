# Test Case Generation using Z3
This repository provides connectors modeling in Z3 and refinement checking scripts, as well as some examples. Additionally, we finished visualizing the connectors in LaTeX using TikZ.
## Dependencies
- python
- LaTeX
## Modeling and Refinement Checking
The modeling of connectors (basic, probabilistic, timer) and refinement checking scripts are in folder `\Models`.
- `channel.py`: we defined basic channels, probabilistic channels, and timer channels by adding constraints using Z3.
- `refinement.py`: using the function `isRefinementOf(abstraction, bound)` to check if the connector is a refinement of the abstraction.
- `automerger.py`: in previous works, we need to specially add a `merge *nodes` to model connectors, which may be inconvenient and easy to make mistakes. Therefore, we implemented an automerger to automatically merge the nodes in the connector.\
Note that you can merge arbitrary many nodes to one sink end rather than simply merging two nodes.
## Implementation
The corresponding scripts for the examples are also in folder `\Models`. We listed several test cases in `test_cases.py`, you can add your own cases into this script following this format:
```Python
test_case = (
    ['Sync A E', 'Fifo1 E F', 'Fifo1 E G', 'Sync F B', 'Sync G C', 'SyncDrain F G'],
    ['Fifo1 A D', 'Sync D B', 'Sync D C']
)
```
Running a single experiment, the refinement checking will contain two directions of checks:
- Implementation Refines Specification? (Impl <= Spec)
- Specification Refines Implementation? (Spec <= Impl)

To be clear, if both directions are `True`, then the connectors are equivalent.\
To check all the test cases in `test_cases.py`, you can run the following command:
```bash
python main.py --list
python main.py --all
```
If you only want to check a specific test case in `test_cases.py`, you can run the following command:
```bash
python main.py test_basic_01
```
Terminal will return dictionary(s) as the result in the form of
```bash
{'test_basic_01': (spec_list, impl_list), ...}
```
## Visualizing Connectors in LaTeX
We finished visualizing the connectors in LaTeX using TikZ. The corresponding scripts are in folder `\Visualization`.\
`tikz_template.tex`: we provide a template for all the connectors defined in `channel.py` in this LaTeX file.
There are also three examples in this folder, which are showed in the paper.
