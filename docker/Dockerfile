FROM ubuntu:18.04 AS ubuntu-ambertools19-py3.6-run
RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive; \
    apt-get install -y --no-install-recommends \
            gcc=4:7.4.0-1ubuntu2.3 gfortran=4:7.4.0-1ubuntu2.3 \
            g++=4:7.4.0-1ubuntu2.3 python3.6=3.6.9-1~18.04ubuntu1 \
            python3-pip=9.0.1-2.3~ubuntu1.18.04.1 \
            python3-setuptools=39.0.1-2 python3-dev=3.6.7-1~18.04; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*
RUN pip3 install wheel==0.34.2
RUN pip3 install \
	numpy==1.18.5 matplotlib==3.2.1 scipy==1.4.1 ipython==7.15.0 \
	notebook==6.0.3 cython==0.29.19 pytest==5.4.3; \
	rm -rf /root/.cache


FROM ubuntu-ambertools19-py3.6-run AS ambertools-builder
RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive; \
    apt-get install -y --no-install-recommends \
            wget=1.19.4-1ubuntu2.2 ca-certificates=20190110~18.04.1 \
            make=4.1-9.1ubuntu1 csh=20110502-3ubuntu0.18.04.1 flex=2.6.4-6 \
            bison=2:3.0.4.dfsg-1build1 patch=2.7.6-2ubuntu1.1 bc=1.07.1-2; \
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

FROM ubuntu:18.04
COPY --from=emptied /lib/x86_64-linux-gnu/libexpat.so.1 /lib/x86_64-linux-gnu/
COPY --from=emptied /usr /usr
RUN echo "export PATH=$PATH:/usr/bin/enlighten2" >> /etc/profile; \
	echo "source /usr/bin/amber18/amber.sh" >> /etc/profile
COPY assets/enlighten2 /usr/bin/enlighten2
RUN cd /usr/bin/enlighten2; python3 setup.py install
WORKDIR /tmp
