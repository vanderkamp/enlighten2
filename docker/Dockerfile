FROM ubuntu AS ubuntu-ambertools19-py3.6-run
RUN apt-get update; \
        DEBIAN_FRONTEND=noninteractive; \
        apt-get install -y --no-install-recommends \
                gcc gfortran g++ python3.6 python3-pip \
		python3-setuptools python3-dev; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*
RUN pip3 install wheel
RUN pip3 install \
	numpy matplotlib scipy ipython notebook cython pytest; \
	rm -rf /root/.cache


FROM ubuntu-ambertools19-py3.6-run AS ambertools-builder
RUN apt-get update; \
        DEBIAN_FRONTEND=noninteractive; \
        apt-get install -y --no-install-recommends \
                wget ca-certificates make csh flex bison patch bc; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*
WORKDIR /usr/bin
COPY assets/AmberTools19.tar.bz2 .
RUN tar xjvf AmberTools19.tar.bz2 && rm AmberTools19.tar.bz2
WORKDIR amber18
RUN echo "y\n" | ./configure -noX11 --with-python /usr/bin/python3.6 gnu
RUN . /usr/bin/amber18/amber.sh; make install


FROM ambertools-builder AS cleaned-ambertools
WORKDIR /usr/bin/amber18/cleaned
RUN mkdir lib; \ 
	mv ../lib/python3.6 lib; \
	rm -rf lib/python3.6/site-packages/pytraj-2.0.5-py3.6-linux-x86_64.egg; \
	rm -rf lib/python3.6/site-packages/packmol_memgen; \
	mkdir bin; cd ../bin; \
	mv sqm tleap teLeap to_be_dispatched/* pdb4amber sander ../cleaned/bin; \
	cd ../cleaned; \
	mkdir dat; cd ../dat; \ 
	mv antechamber chamber contrib leap ../cleaned/dat
WORKDIR /usr/bin/
COPY assets/propka-3.1 propka-3.1
RUN pip3 install propka-3.1/


FROM ubuntu-ambertools19-py3.6-run as emptied
WORKDIR /usr/bin/amber18
COPY assets/cleanup.sh .
RUN . ./cleanup.sh
RUN rm cleanup.sh
COPY --from=cleaned-ambertools /usr/local/bin/propka31 /usr/local/bin/propka31
COPY --from=cleaned-ambertools /usr/bin/amber18/amber.sh ./
COPY --from=cleaned-ambertools /usr/bin/amber18/cleaned ./
COPY --from=cleaned-ambertools /usr/local/lib/python3.6/dist-packages/PROPKA-3.1.0.dist-info /usr/local/lib/python3.6/dist-packages/PROPKA-3.1.0.dist-info
COPY --from=cleaned-ambertools /usr/local/lib/python3.6/dist-packages/propka /usr/local/lib/python3.6/dist-packages/propka

FROM ubuntu 
COPY --from=emptied /lib/x86_64-linux-gnu/libexpat.so.1 /lib/x86_64-linux-gnu/
COPY --from=emptied /usr /usr
RUN echo "export PATH=$PATH:/usr/bin/enlighten2" >> /etc/profile; \
	echo "source /usr/bin/amber18/amber.sh" >> /etc/profile
COPY assets/enlighten2 /usr/bin/enlighten2
RUN cd /usr/bin/enlighten2; python3 setup.py install
WORKDIR /tmp
