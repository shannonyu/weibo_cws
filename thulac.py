#!/usr/bin/python3
import subprocess
import sys
import os
import isan.common.Chinese as Chinese


class Predict_C:
    def __init__(self,model_path='./stack/'):# b m e s = 1 2 4 8
        self.poc_map={(None,None):'f',
                (None,'s'):'c',#e s
                (None,'c'):'3',#b m
                ('s',None):'9',# b s
                ('s','s'):'8',#s
                ('s','c'):'1',#b
                ('c',None):'6',#me
                ('c','s'):'4',#e
                ('c','c'):'2',#m
                }
        self.sp=subprocess.Popen(['./thulac/bin/thulac',model_path,'-p']
        #self.sp=subprocess.Popen(['./thulac/bin/predict_c','thulac/models/pku/model_c']
                                        ,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    def __call__(self,raw,cands):
        pocs=[]
        for i in range(len(cands)-1):
            pocs.append(self.poc_map[(cands[i],cands[i+1])])
        pocs=''.join(pocs)
        #raw=Chinese.to_full(raw)
        self.sp.stdin.write((pocs+' '+raw+'\n').encode())
        self.sp.stdin.flush()
        result=self.sp.stdout.readline().decode().strip()
        res=[]
        for item in result.split():
            word,_,tag=item.rpartition('_')
            res.append([word,tag])

        return res


if __name__ == '__main__':
    model=Predict_C('thulac/models/sanku/')
    r=model('鱼上钩了',[None,None,None,None,None])
    print(r)

