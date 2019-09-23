#!/usr/bin/env python3

import os
import random
import time


for i in range(10):
    time.sleep(0.2)
    os.write(random.randint(1, 2), bytes(str(i) + '\n', 'utf8'))
