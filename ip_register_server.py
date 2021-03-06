from flask import Flask, jsonify, request
import requests

# Instantiate our Node
app = Flask(__name__, template_folder='./templates')

# Registered nodes in network
nodes = []


@app.route('/nodes', methods=['GET'])
def list_all_nodes():
    list_nodes = list(nodes)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list_nodes,
    }
    return jsonify(response), 201


@app.route('/node/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    ip_node = values.get('node')
    identifier_node = values.get('identifier')
    public_key = values.get('public_key')

    list_nodes = list(nodes)
    new_node = {
        'node': ip_node,
        'identifier': identifier_node,
        'public_key': public_key
    }

    for node in list_nodes:
        url = "http://%s:5000/node/register" % node['node']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        data = '{"node": "%s", "identifier": "%s","public_key": "%s"}' % (ip_node, identifier_node, public_key)
        requests.post(url, data=data, json=data, headers=headers)

    nodes.append(new_node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list_nodes,
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
