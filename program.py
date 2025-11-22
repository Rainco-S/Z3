from reo import *

def define_connector(connector_name):
    '''
    Define a connector according to the input.
    :param connector_name: used to offer information
    :return: Connector
    '''
    merger_count = 0
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
                merger_count += 1
                int1 = f"{nodes[2]}_{merger_count * 2 - 1}"
                int2 = f"{nodes[3]}_{merger_count * 2}"
                conn.connect(nodes[0], nodes[2], int1)
                conn.connect(nodes[1], nodes[3], int2)
                conn.connect('Merger', int1, int2, nodes[4])
            else:
                conn.connect(channel_type, *nodes)
        except Exception as e:
            print(f"Error {str(e)}")

    return conn

print('Type connectors according to the following rules: (name the nodes like ABC or A1B1C1)\n'
      'Sync A B\n'
      'Fifo1 A B\n'
      'LossySync A B\n'
      'SyncDrain A B\n'
      'Fifo1e(1) A B\n'
      'Merger type1 type2 A B C')
print("Type 'done' to end defining current connector.")

c1 = define_connector("c1")
c2 = define_connector("c2")

result1, counterexample1, smt1 = c2.isRefinementOf(c1, 10)
result2, counterexample2, smt2 = c1.isRefinementOf(c2, 10)

print(result1)
print(result2)
print(counterexample1)
print(counterexample2)

