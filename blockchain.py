import hashlib
import json
from textwrap import dedent
from time import time, sleep
from uuid import uuid4
import requests
from subprocess import check_output
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from urllib.parse import urlparse

from flask import Flask, jsonify, request, render_template


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.current_transactions.append({
            'sender': 0,
            'recipient': node_identifier,
            'amount': 100,
        })
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            url = 'http://%s:5000/chain' % node
            response = requests.get(url)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def get_my_amount(self):
        """
        Sum node currency
        :return: <int> Actual state of account
        """

        money = 0
        current_index = 0

        while current_index < len(self.chain):
            block = self.chain[current_index]
            for transaction in block['transactions']:
                if transaction['recipient'] == node_identifier:
                    money += int(transaction['amount'])
                if transaction['sender'] == node_identifier:
                    money -= int(transaction['amount'])

            current_index += 1

        if self.current_transactions != '':
            for transaction in self.current_transactions:
                if transaction['sender'] == node_identifier:
                    money -= int(transaction['amount'])

        return money


# Instantiate our Node
app = Flask(__name__, template_folder='./templates')

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

node_ip = check_output(['awk', 'END{print $1}', '/etc/hosts']).decode('utf-8').replace('\n','')

key = rsa.generate_private_key(
    backend=crypto_default_backend(),
    public_exponent=65537,
    key_size=2048
)
private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption())
public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH)

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/')
def index():
    return render_template('index.html', node_identifier=node_identifier, node_money=blockchain.get_my_amount()), 200

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=10,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    # return jsonify(response), 200
    return render_template('mine.html', node_identifier=node_identifier, node_money=blockchain.get_my_amount(), mine=response), 200


@app.route('/transactions/receive_new', methods=['POST'])
def new_transaction_form_node():
    values = request.get_json()

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    sender = values.get('sender')
    recipient = values.get('recipient')
    amount = values.get('amount')

    index = blockchain.new_transaction(sender, recipient, amount)


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    #values = request.get_json()
    values = request.form

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    # Distribute the new Transaction in network
    for node in blockchain.nodes:
        url = "http://%s:5000/transactions/receive_new" % node
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        data = '{"sender": "%s", "recipient": "%s","amount": "%s"}' % (values['sender'], values['recipient'], values['amount'])
        requests.post(url, data=data, json=data, headers=headers)

    response = {'message': f'Transaction will be added to Block {index}'}
    #return jsonify(response), 201
    return render_template('index.html', node_identifier=node_identifier, node_money=blockchain.get_my_amount(), response=response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/chain/template', methods=['GET'])
def full_chain_template():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return render_template('chain.html', node_identifier=node_identifier, node_money=blockchain.get_my_amount(), chain=response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        #blockchain.nodes.add(node['node'])
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/node/register', methods=['POST'])
def register_node():
    values = request.get_json()

    node_ip = values.get('node')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    blockchain.nodes.add(node_ip)

    response = {
        'message': 'New nodes have been added'
    }

    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def list_all_nodes():
    list_nodes = list(blockchain.nodes)
    response = {
        'total_nodes': list_nodes,
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    #return jsonify(response), 200
    return render_template('index.html', node_identifier=node_identifier, node_money=blockchain.get_my_amount(), response=response), 200

app.jinja_env.filters['hash'] = blockchain.hash

if __name__ == '__main__':
    print(node_ip)
    url = "http://ip_register_server:5000/node/register"
    data = '{"node": "%s", "identifier": "%s","public_key": "%s"}' % (node_ip, node_identifier, "dd")
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    nodes = []

    try:
        response = requests.post(url, data=data, json=data, headers=headers)
    except Exception:
        sleep(10)
        response = requests.post(url, data=data, json=data, headers=headers)

    if response.status_code == 200:
        messege = response.json()['message']
        nodes = response.json()['total_nodes']

    for node in nodes:
        blockchain.nodes.add(node['node'])

    app.run(host='0.0.0.0', port=5000)
