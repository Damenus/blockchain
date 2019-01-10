FROM python:3.6-alpine

ADD /dist/blockchain.pex /usr/bin/

EXPOSE 5000

CMD ["blockchain.pex"]
