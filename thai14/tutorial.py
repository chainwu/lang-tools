#!/usr/bin/python
#-*- encoding: UTF-8 -*-

## -------------------------
## EHowNet API 2.0 Tutorial
## -------------------------

## 1. 載入 ehownet library 及 EHowNet ontology 資料庫

# 在執行 python 之後，就可以直接 載入 ehownet library 了，
# 然後，我們接著載入 EHowNet ontology。

from ehownet import *
tree=EHowNetTree("db/ehownet_ontology.sqlite")
#tree=EHowNetTree("db/ehownet_ontology_sim.sqlite")

# 其中，ehownet_ontology.sqlite 是存放 EHowNet 的樹狀結構
# 資料庫。這是一個 sqlite 資料庫檔案，有興趣可以使用 sqlite
# 的應用程式 (如:SQLite Expert) 打開來看看。

## 2. 查詢 EHowNet Ontology

# 我們以「開心」一詞為例，呼叫 searchWord 函數。
# 函數會傳回一組 ontology nodes。

list=tree.searchWord(u"開心")
print list

# 輸出結果：[word('開心.Nv,VH.1')]

# 在這個例子中，因為「開心」只有一組語義，所以 list 中只包含
# 一個 word node。

# 另外，在 2.0 版中，我們可以發現，word 的表達式改為：
#     word('開心.Nv,VH.1')
# 這個表達式代表一個 sense，類似於 WordNet synset 的表達式。
# 這個表達式在整個 ontology tree 中是唯一，所以我們也可以用
# 表達式來取得資料：

node=tree.word('開心.Nv,VH.1')
print node

## 3. word 節點的資料結構

# 一個 word 節點主要有下列的幾個欄位：

# node.name    : 節點的名稱，在 word 類的節點中，就是表達式
# node.word    : 詞彙本身
# node.ehownet : EHowNet 定義式
# node.pos     : 詞類
# node.pos_long: 長詞類
# node.meaning : word sense 的意義，也可以看做是英文翻譯。

# 另外還有其他的一些欄位：
# node.sid     : sense ID， sense 的流水號，對應到ckip 詞典
#		 的資料庫，沒有特別用處
# node.node_type: 在 ontology 中的類別，可以分為 word 及 semanticType 兩類。
# node.node_id  : 在 ontology 中的流水號，供 API 內部使用。
# node.type    : 
#   在 ontology 中的類別可以再細分， semanticType 可分為 
#
#     primitive -- 該節點為「義原」
#     category -- 該節點為「非義原」類別，在 EHowNet 中，是比較
#                 細的分類節點
#
#   而 word 節點也可以再分為：
#
#     attachWord -- 語義和他的 semanticType 完全一致
#     word -- 語義和他的 semanticType 不完全一致
#
#   這個區分在 EHowNet API 的使用上不是很重要的訊息。目前是使用在 
#   EHowNet ontology online 中， attachWord 是直接附加在 semanticType 
#   的下的詞，例如在 ontology online 中我們可以看到 object|物件的節點，
#   後面接了三個 words: 
#     object|物件 [ 事物, 客體, 對象 ]       
#   這三個詞的定義式都是 {object|物件} ，和 semsnticType 一致，所以稱為
#   attachWord。 其餘和 object|物件 不完全一致的詞，例如：
#      一體 : {object|物體:qualification={complete|整}}
#   不會直接放在中括號中的，類別就是 word

print node.name.encode("UTF-8")
print node.word.encode("UTF-8")
print node.ehownet.encode("UTF-8")
print node.pos.encode("UTF-8")
print node.pos_long.encode("UTF-8")
print node.meaning.encode("UTF-8")

print node.dump().encode("UTF-8")

## 4. category 節點的資料結構

# 一個 category 節點主要有下列的幾個欄位：

# node.name    : 節點的名稱，也是 category 的唯一表達式
# node.label   : EHowNet 定義式
# node.type    : 詞類

categoryList=node.getSemanticTypeList()
category=categoryList[0]
print category
print category.dump().encode("UTF-8")

## 5. 上下位查詢

# 上下位查詢的 API 提供在 ontology 中走訪的功能。基本的 API 如下：
#
# A. word node 的 member function:
#    * word.getSemanticTypeList(): 取得詞彙的語義類
#    * word.getSynonymWordList(): 取得詞彙的同義詞(定義式完全相同)
#    * word.getSiblingWordList(): 取得同在 semanticType 下的近義詞
#    * word.getDescendantWordList(): 取得在 semanticType 下及其下位的近義詞
# 註： getSiblingWordList() 和 getDescendantWordList() 的差別在於前者所取得
#      的近義詞限於同一層，後者則是將更深層的節點下的近義詞也取出。
#      以「開心」為例，getSiblingWordList() 會取得 joyful|喜悅 下的詞，
#      而 getDescendantWordList() 除了 「joyful|喜悅」 之外，還會取得 
#      「狂喜|exultation」,「不快|be displeased」,「不悅|frown on」... 等
#      下位節點下的詞。

node=tree.word('開心.Nv,VH.1')
print node.getSemanticTypeList()
print node.getSynonymWordList()
print node.getSiblingWordList()
print node.getDescendantWordList()

# B. category node 的 member function
#    * category.getHypernym(): 取得上位義類
#    * category.getHyponymList(): 取得下位義類
#    * category.getWordList(): 取得附在義類下的詞彙
#    * category.getAncestorList(): 取得所有上位義類，包含 TopNode
#    * category.getDescendantList(): 取得所有下位義類
#    * category.getDescendantWordList(): 取得節點內及所有下位義類節點內的
#       近義詞
# 

category=tree.semanticType('joyful|喜悅.1')
print category

parent=category.getHypernym()
print parent

ancestorList=category.getAncestorList()
print ancestorList

childList=parent.getHyponymList()
print childList

wordList=category.getWordList()
print wordList


## 6. 檢查節點間的上下位關係:

# categoryA.isHypernymOf(categoryB): category A 是否為 B 的上位
# categoryA.isHyponymOf(categoryB): category A 是否為 B 的下位
# categoryA.isAncestorOf(categoryB): category A 是否為 B 的祖先節點
# categoryA.isDescendantOf(categoryB): category A 是否為 B 的子孫節點

categoryA=tree.semanticType('joyful|喜悅.1')
categoryB=tree.semanticType('FeelingByGood|好情.1')
categoryC=tree.semanticType('thing|萬物.1')
categoryD=tree.semanticType('event|事件.1')

print categoryA.isHyponymOf(categoryB)  # True
print categoryA.isHypernymOf(categoryB) # False
print categoryB.isHyponymOf(categoryA)  # False
print categoryB.isHypernymOf(categoryA) # True
print categoryD.isHypernymOf(categoryA) # False
print categoryD.isAncestorOf(categoryA) # True

## 7. 節點的查詢功能
#
# tree.searchWord(word): 查詢 tree 中的詞彙
# tree.searchSemanticType(semanticType): 查詢 tree 中的 semantic type
# tree.word(word_name): 直接用 word 表達式取出節點
# tree.semanticType(semantic_type_name): 直接用 semanticType 取出節點

print tree.searchWord("開心")
print tree.searchSemanticType("龍|dragon")
print tree.word('開心.Nv,VH.1')
print tree.semanticType('龍|dragon.1')


## 8. 計算節點間的距離及路徑
# tree.distance(node1, node2): 計算 node1 到 node2 的最短距離
# tree.searchShortestPath(node1, node2): 計算 node1 到 node2 的短路徑

categoryA=tree.semanticType('joyful|喜悅.1')
categoryB=tree.semanticType('FeelingByGood|好情.1')
categoryC=tree.semanticType('thing|萬物.1')
categoryD=tree.semanticType('event|事件.1')
wordE=tree.word('開心.Nv,VH.1')

print tree.distance(categoryA, categoryB)
print tree.distance(categoryD, wordE)
print tree.distance("大快人心","不亦樂乎")
print tree.distance(tree.searchWord("大快人心"),tree.searchWord("不亦樂乎"))
print tree.distance("開心.Nv,VH.1","joyful|喜悅.1")
print tree.distance("打",tree.word("開心.Nv,VH.1"))
print tree.distance("打","開心.Nv,VH.1")

print tree.searchShortestPath(categoryD, categoryA)
print tree.searchShortestPath("打","開心.Nv,VH.1")
print len(tree.searchShortestPath("打","開心.Nv,VH.1"))
