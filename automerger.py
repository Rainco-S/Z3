from reo import *

# input connectors' format:
# test5_1 = ['LossySync A B', 'LossySync A D', 'SyncDrain A C', 'Sync B C', 'Sync D C', 'Merger B D C', 'Sync B E', 'Sync D F']

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

    return conn, basic_channels, mergers

test5_1 = ['LossySync A B', 'LossySync A D', 'SyncDrain A C', 'Sync B C', 'Sync D C', 'Merger B D C', 'Sync B E', 'Sync D F']
test5_2 = ['Sync A B', 'LossySync A D', 'SyncDrain A C', 'Sync B C', 'Sync D C', 'Merger B D C', 'Merger D E F', 'Sync B E', 'Sync D F']

test6_1 = ['Sync A D', 'Sync D C', 'Sync B E', 'Sync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F']
test6_2 = ['Sync A D', 'LossySync D C', 'Sync B E', 'LossySync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F']

test7_1 = ['Sync A D', 'Sync D C', 'Sync B E', 'Sync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F']
test7_2 = ['SyncDrain A B', 'Fifo1 A C', 'Sync B C', 'Merger A B C']

c1 = define_connector("c1", test7_2)
for item in c1[1]:
    print(item)
print(c1[2])

# 如果basic里没有，需要补上Sync