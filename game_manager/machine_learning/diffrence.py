#!/usr/bin/env python3
# coding: UTF-8

import difflib as diff

with open('block_controller_train.py','r') as f:
    str1 = f.readlines()
    
with open('block_controller_train_sample3.py','r') as f:
    str2 = f.readlines()

print(str1)
print(str2)

for i in diff.unified_diff(str1, str2, fromfile='block_controller_train.py', tofile='block_controller_train_sample3.py'):
    print(i, end='')