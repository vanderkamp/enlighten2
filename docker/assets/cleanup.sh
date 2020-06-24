rm -rf /usr/include
rm -rf /usr/sbin
rm -rf /usr/share
rm -rf /usr/lib/gcc
rm -rf /usr/bin/amber18/lib/python3.6/site-packages/pytraj-2.0.5-py3.6-linux-x86_64.egg
rm -rf /usr/bin/amber18/lib/python3.6/site-packages/packmol_memgen
rm -rf /usr/local/lib/python3.6/dist-packages/matplotlib
rm -rf /usr/local/lib/python3.6/dist-packages/matplotlib-3.1.1-py3.6-nspkg.pth
rm -rf /usr/local/lib/python3.6/dist-packages/notebook
rm -rf /usr/local/lib/python3.6/dist-packages/scipy
rm -rf /usr/lib/python3.6/__pycache__
rm -rf /usr/lib/python3.6/libpython3.6m.a
rm -rf /usr/lib/python3.6/libpython3.6m-pic.a

cd /usr/lib/x86_64-linux-gnu
mv * /tmp/
mv /tmp/libc.so .
mv /tmp/libdl.so .
mv /tmp/libffi.so.6 .
mv /tmp/libffi.so.6.0.4 .
mv /tmp/libgfortran.so.4.0.0 .
mv /tmp/libgfortran.so.4 .
mv /tmp/libm.so .
mv /tmp/libquadmath.so.0.0.0 .
mv /tmp/libquadmath.so.0 .
mv /tmp/libstdc++.so.6 .

cd /usr/local/lib/python3.6/dist-packages
mv * /tmp/
mv /tmp/numpy /tmp/numpy.libs .
