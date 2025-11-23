from reo import *

def define_connector(connector_name):
    merger_count = 1
    conn = Connector()
    print(f'Start defining connector {connector_name}')

    while True:
        user_input = input(f"{connector_name}> ").strip()
        if user_input.lower() == 'done':
            break

        parts = user_input.split()
        channel_type = parts[0]
        nodes = parts[1:]

        try:
            if channel_type == 'Merger':
                new_node = []
                src_num = len(nodes) // 2
                for i in range(src_num):
                    temp = f"{nodes[src_num + i]}_{merger_count}"
                    conn.connect(nodes[i], nodes[src_num + i], temp)
                    new_node.append(temp)
                    merger_count += 1

                new_node.append(nodes[-1])
                conn.connect('Merger', *new_node)
            else:
                conn.connect(channel_type, *nodes)
                
        except Exception as e:
            print(f"Error {str(e)}")

    return conn

print('Type connectors according to the following rules: (name the nodes like ABC or A1B1C1)\n'
      'Sync A B\n'
      'Fifo1e(1) A B\n'
      'Merger type1 type2 ... src_1 src_2 ... snk')
print("Type 'done' to end defining current connector.")

c1 = define_connector("c1")
c2 = define_connector("c2")

result1, counterexample1, smt1 = c2.isRefinementOf(c1, 10)
result2, counterexample2, smt2 = c1.isRefinementOf(c2, 10)

print(result1)
print(result2)
print(counterexample1)
print(counterexample2)

