from reo import *

def define_connector(connector_name, input_connectors):
    conn = Connector()
    merger_count = 0

    basic_channels = []
    mergers = []

    for con in input_connectors:
        con = con.split()
        if con[0] != 'Merger':
            basic_channels.append((con[0], con[1:]))
        elif con[0] == 'Merger':
            mergers.append(con[1:])
        else:
            print(f"Error: Unknown channel type in {con}")

    for i in range(len(mergers)):
        src_num = len(mergers[i]) - 1
        for j in range(src_num):
            hidden_node = f"{mergers[i][j]}_{merger_count}"
            merger_count += 1
            
            for k in range(len(basic_channels)):
                if basic_channels[k][1][0] == mergers[i][j] and basic_channels[k][1][1] == mergers[i][-1]:
                    basic_channels[k][1][1] = hidden_node
                    mergers[i][j] = hidden_node
                    break
            
    for con in basic_channels:
        conn.connect(con[0], *con[1])
    for con in mergers:
        conn.connect('Merger', *con[1])

    return conn