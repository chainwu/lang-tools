#!/usr/bin/env python3
# coding: utf-8

# In[1]:


import pandas as pd
import treelib

def read_databases():
    try:
        #讀入字典
        cdict = pd.read_excel('cdict2.xlsx')

        return cdict
    except Exception as e:
        print(e)
        exit(-1)

cdict = read_databases()


# In[2]:


from treelib import Node, Tree

tree = Tree()
root = tree.create_node("root", "root") # root node

for p in cdict.phone:
    print(p, end=" ")
    tmp=p
    tmp=tmp.replace("ˊ","")
    tmp=tmp.replace("˙","")
    tmp=tmp.replace("ˇ","")
    tmp=tmp.replace("ˋ","")
    tmp=tmp.replace(" ","")
    tmp=tmp.replace(",","")
    print(tmp)
    for j in range(len(tmp)):
        phnode = tree.get_node(tmp[0:j])
        if phnode == None:
            try:
                if j == 0:
                    px = tree.create_node(tmp[0], tmp[0], parent="root")
                else:
                    px = tree.create_node(tmp[j], tmp[0:j], parent=phnode.identifier)
                phnode = px
            except:
                continue

tree.show()


# In[ ]:


from treelib import Node, Tree

tree = Tree()
tree.create_node("Harry", "harry") # root node
tree.create_node("Jane", "jane", parent="harry")
tree.create_node("Bill", "bill", parent="harry")
tree.create_node("Diane", "diane", parent="jane")
tree.create_node("Mary", "mary", parent="diane")
tree.create_node("Mark", "mark", parent="jane")
tree.show()

