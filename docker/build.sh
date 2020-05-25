#!/bin/bash
cd assets
if [[ ! -d enlighten2 ]]; then
	git clone https://github.com/vanderkamp/enlighten2.git
	rm -rf enlighten2/examples enlighten2/.git
fi
if [[ ! -d propka-3.1 ]]; then
	git clone https://github.com/jensengroup/propka-3.1.git
	rm -rf propka-3.1/.git
fi
cd ..
docker build -t kzinovjev/enlighten2 .
