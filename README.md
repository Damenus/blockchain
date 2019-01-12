## Blockchain simple implementation

The program is based on a [document][1] write by Satoshi Nakamoto 
and [tutorial Hackernoon][2]. 

### Run

The program is prepared to deploy with docker composer.

Run command:

````
docker-compose up --scale blockchian_server=3 --force-recreate --build
````

### Requariments

````
Docker > 18.06.1-ce
docker-compose > 1.23.2,
````

### Build

````
docker-compose build --no-cache
docker rmi $(docker images -f "dangling=true" -q); docker-compose build
````


### Local development


````

````


[1]: https://bitcoin.org/bitcoin.pdf
[2]: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
