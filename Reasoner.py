#------------------------#
# Knowledge Reasoner     #
# author:Kazumi Ishiwata #
#------------------------#
import re
from time import sleep

#Messages
inputMessage = '0 : Type in a sentence with three words or \'see you\'.\n' #"コメントを記入してください"的なメッセージ
excMessage   = '0 : I don\'t know.'                                        #"分かりません"的なメッセージ
knowMessage  = '0 : I know it.'                                            #"知っている"的なメッセージ
learnMessage = '0 : I got it.'                                             #"今知った"的なメッセージ
endMessage   = '0 : see you next time!'                                    #"さようなら"的なメッセージ

#事実のリストを読込
factFile = open('facts.txt', 'r')
factText = factFile.readlines();factFile.close()
factList = []
for line in factText:
   if line != '\n' and not line.startswith('#'):
      factList.append(line.split('.')[0])


#名詞の属性一覧の作成
def getMeanList(noun,u_or_d):
  meanList   = [noun]
  searchList = [noun]
  idx = 2 if u_or_d == 'u' else 0
  while len(searchList) > 0:
    searchList1 = searchList;searchList = []
    for noun in searchList1:
      for fact in factList:
        if  (u_or_d == 'u' and re.fullmatch(noun+' are .*',fact)) or (u_or_d == 'd' and re.fullmatch('.* are '+noun,fact)):
          searchList.append(fact.split(' ')[idx])
          meanList.append(fact.split(' ')[idx])
  #print(','.join(meanList))#debug
  return meanList


#回答を追加する
def appendAnswer(q,l,answerList,meanList,id1,id2):
  for noun in meanList:
    l[id1] = noun
    for fact in factList:
      if re.fullmatch(' '.join(l),fact) != None:
        answerList.append('0 : ' + fact.replace(l[id1],q[id2]) + '.')
  return answerList


#推論
def reasoning(input1):
  answerList = []
  Q = input1.replace('?','').replace('.','').split(' ')
  if Q[0] == 'you':
    Q[0] = 'I'
    if Q[1] == 'are':Q[1] = 'am'
    if Q[2] == 'are':Q[2] = 'am'
  elif Q[1] == 'you':
    Q[1] = 'I'
    if Q[2] == 'are':Q[2] = 'am'
    if Q[0] == 'are':Q[0] = 'am'
  elif Q[2] == 'you':
    Q[2] = 'I'
    if Q[0] == 'are':Q[0] = 'am'
    if Q[1] == 'are':Q[1] = 'am'
  L = ['','','']
  #print('    '+' '.join(Q))#debug

  #who am A? -> I am ~~.
  if Q[1] == 'am':
    L[0] = Q[2];L[1] = Q[1];L[2] = '.*'
    meanList = getMeanList(L[0],'u')
    appendAnswer(Q,L,answerList,meanList,0,2)
  elif Q[0] == 'what' or Q[0] == 'who':
    if Q[0] == 'what':
      #what are A? -> A are B.
      if (Q[1] == 'are'):
        L[0] = Q[2];L[1] = Q[1];L[2] = '.*'
        meanList = getMeanList(L[0],'u')
        appendAnswer(Q,L,answerList,meanList,0,2)
      #what S V? -> S V O.
      else:
        L[0] = Q[1];L[1] = Q[2];L[2] = '.*'
        meanList = getMeanList(L[0],'u')
        appendAnswer(Q,L,answerList,meanList,0,1)
    if Q[0] == 'who':
      #who are A? -> ~~ are A.
      if (Q[1] == 'are'):
        L[0] = '.*';L[1] = Q[1];L[2] = Q[2]
        meanList = getMeanList(L[2],'d')
        appendAnswer(Q,L,answerList,meanList,2,2)
      #who V O? -> S V O.
      else:
        L[0] = '.*';L[1] = Q[1];L[2] = Q[2]
        meanList = getMeanList(L[2],'d')
        appendAnswer(Q,L,answerList,meanList,2,2)
  else:
    #S V O. -> S V O. or (none)
    L[0] = Q[0];L[1] = Q[1];L[2] = Q[2]
    meanList = getMeanList(L[0],'u')
    appendAnswer(Q,L,answerList,meanList,0,0)
    meanList = getMeanList(L[2],'d')
    appendAnswer(Q,L,answerList,meanList,2,2)
  return answerList


#学習
def appendFact(s1):
  s1 = s1.replace('you are ','I am ').replace('.','')
  #print(reasoning(s1))#debug
  if '0 : ' + s1 + '.' in reasoning(s1):
    print(knowMessage)
  else:
    factList.append(s1)
    factFile.write('\n' + s1 + '.')
    print(learnMessage)


#main
def main():
  print(inputMessage,end='')
  while True:
    s1 = input('1 : ')
    if   s1.startswith('see you') or s1.startswith('See you')or s1.startswith('seeyou')or s1.startswith('Seeyou') :
      break
    elif s1 == '':                  #改行
      continue
    elif s1.endswith('?'):          #回答
      try:
        answerList = reasoning(s1)
        if answerList == []:print(excMessage)
        else:print('\n'.join(answerList))
      except:
        None
    elif s1.count(' ') == 2:        #学習
      appendFact(s1)
    else:                           #該当なし
      print(excMessage)
  print(endMessage)                 #終了
  sleep(3)


#実行
factFile = open('facts.txt', 'a')
main()
factFile.close()