from flask import Flask, jsonify, request

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

    node = values.get('node')
    identifier = values.get('identifier')
    public_key = values.get('public_key')

    list_nodes = list(nodes)

    nodes.append({
        'node': node,
        'identifier': identifier,
        'public_key': public_key
    })

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list_nodes,
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
