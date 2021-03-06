from isan.tagging.inc_segger import *
import sys
import pre
import thulac
import thulac_cws
import math
class DiffToHTML:
    """
    用于生成HTML的diff文件的插件
    """
    def __init__(self,filename):
        self.html=open(filename,'w')
        self.line_no=0
    def __del__(self):
        self.html.close()
    def to_set(self,seq):
        offset=0
        s=set()
        for w in seq:
            s.add((offset,w))
            offset+=len(w)
        return s
    def __call__(self,std,rst):
        self.line_no+=1
        std=self.to_set(std)
        rst=self.to_set(rst)
        #for b,w,t in std:
        #print(std)
        cor=std&rst
        seg_std={(b,w)for b,w in std}
        seg_rst={(b,w)for b,w in rst}
        if len(cor)==len(std):return
        html=[]
        for b,w in sorted(rst):
            if (b,w) in seg_std:
                html.append(w)
                continue
            html.append("<font color=red>"+w+"</font>")
        print(' '.join(html),"<br/>",file=self.html)
        html=[]
        for b,w in sorted(std):
            if (b,w) in rst:
                html.append(w)
                continue
            html.append("<font color=blue>"+w+"</font>")
        print(' '.join(html),"<br/><br/>",file=self.html)
        
class Default_Features :
    def __init__(self):
        #self.thulac=thulac.Predict_C()
        self.thulac=thulac.Predict_C()
        #self.sanku=thulac.Predict_C('thulac/models/sanku/')
        self.thulac_weibo=thulac_cws.Predict_C('stack/weibo1')
        self.chinese_characters=set(chr(i) for i in range(ord('一'),ord('鿋')+1))
        self.numbers=set()
        for c in '0123456789':
            self.numbers.add(c)
            self.numbers.add(chr(ord(c)+65248))
        self.latin=set()
        for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.latin.add(c)
            self.latin.add(chr(ord(c)+65248))
        #print(self.numbers)
        self.punks=set('…。，？：；！/.')
        self.idioms=set()
        for ln,line in enumerate(open("res/idiom.txt")):
            ol=line
            line=line.split()
            if line:
                self.idioms.add(line[0])

        self.baidu=dict()
        for line in open('res/baidu_count.txt'):
            word,freq=line.split()
            freq=int(freq)
            self.baidu[word]=freq

        self.SogouW=dict()
        for line in open('res/SogouW.txt'):
            word,freq,*tags=line.split()
            freq=int(freq)
            self.SogouW[word]=[freq,set(tags)]

        self.sogou_input=dict()
        for line in open('res/sogou_input.txt'):
            word,f1,f2=line.split()
            f1=int(f1)
            f2=int(f2)
            self.sogou_input[word]=[f1,f2]


        self.sms_person=set()
        for line in open("res/sms_person.txt"):
            line=line.strip()
            self.sms_person.add(line)


        self.sww=set()
        for line in open("res/sww_idiom.txt"):
            line=line.strip()
            self.sww.add(line)
            
        self.sms=set()
        for line in open("res/sms.txt"):
            line=line.strip()
            self.sms.add(line)

        self.sms_dict=dict()
        for line in open("res/sms_dict.txt"):
            word,freq,*dicts=line.split()
            dicts=[int(x)for x in dicts]
            freq=int(freq)

            self.sms_dict[word]=[freq,dicts]


    def set_raw(self,raw):
        """
        对需要处理的句子做必要的预处理（如缓存特征）
        """
        self.raw=raw
        self.raw_type=['##','##','##']
        for ch in self.raw:
            if ch in self.chinese_characters:
                self.raw_type.append('CC')
            elif ch in self.punks:
                self.raw_type.append('PU')
            elif ch in self.latin:
                self.raw_type.append('LT')
            elif ch in self.numbers:
                self.raw_type.append('NM')
            else:
                #self.raw_type.append('Other')
                self.raw_type.append(ch)
        self.raw_type+=['##','##']
        self.uni_chars=list('###'+raw+'##')
        self.bi_chars=[(self.uni_chars[i],self.uni_chars[i+1]) 
                for i in range(len(self.uni_chars)-1)]

        #'''#set thulac related features'''
        #print(raw)
        thulac_result=self.thulac(raw,self.candidates)
        #sanku_result=self.sanku(raw,self.candidates)
        weibo_result=self.thulac_weibo(raw,self.candidates)
        self.weibo_seq=['s']
        for w in weibo_result:
            for i in range(len(w)-1):
                self.weibo_seq.append('c')
            self.weibo_seq.append('s')



        #print(weibo_result)
        #print(thulac_result)
        
        for w,t in thulac_result :
            pass
            #print(w,t)

        for wt in thulac_result :
            w,t=wt
            if all(c not in self.chinese_characters and c not in self.punks and
                    c not in self.latin and c not in self.numbers for c in w):
                #print(w,t)
                wt[1]='ww'

        self.lac_seq=[['s',None,thulac_result[0][1],None]]
        for i,wt in enumerate(thulac_result):
            w,t=wt
            if i-1>=0:
                lw,lt=thulac_result[i-1]
                if len(lw)==1 and lt=='np' and t=='np':
                    self.lac_seq[-1][3]="name"
                    if(lw in self.chinese_characters
                            and all(c in self.chinese_characters for c in w)):
                        #print("name",lw,w)
                        if lw+w in self.sms_person:
                            pass
                            #self.lac_seq[-1][3]="namesms"
                            #print("name sms",lw,w)

            self.lac_seq[-1][2]=t
            for i in range(len(w)-1):
                self.lac_seq.append(['c',t,t,None])
            self.lac_seq.append(['s',t,None,None])

        #self.sanku_seq=[['s',None,sanku_result[0][1],None]]
        #for i,wt in enumerate(sanku_result):
        #    w,t=wt
        #    if i-1>=0:
        #        lw,lt=sanku_result[i-1]
        #        if len(lw)==1 and lt=='np' and t=='np':
        #            #print(lw,w)
        #            self.sanku_seq[-1][3]=True
        #    self.sanku_seq[-1][2]=t
        #    for i in range(len(w)-1):
        #        self.sanku_seq.append(['c',t,t,None])
        #    self.sanku_seq.append(['s',t,None,None])


    def __call__(self,span):
        raw=self.raw
        uni_chars=self.uni_chars
        bi_chars=self.bi_chars
        c_ind=span[0]+2
        ws_current=span[1]
        ws_left=span[2]
        pos=span[0]
        fv=[
                ("ws",ws_left,ws_current),
                ("c",uni_chars[c_ind],ws_current),
                ("r",uni_chars[c_ind+1],ws_current),
                ('l',uni_chars[c_ind-1],ws_current),
                ("cr",bi_chars[c_ind],ws_current),
                ("lc",bi_chars[c_ind-1],ws_current),
                
                ("rr2",bi_chars[c_ind+1],ws_current),
                ("l2l",bi_chars[c_ind-2],ws_current),
            ]
        #fv+=[
        #        ("c'",uni_chars[c_ind],ws_left,ws_current),
        #        ("r'",uni_chars[c_ind+1],ws_left,ws_current),
        #        ("l'",uni_chars[c_ind-1],ws_left,ws_current),
        #        ("cr'",bi_chars[c_ind],ws_left,ws_current),
        #        ("lc'",bi_chars[c_ind-1],ws_left,ws_current),
        #        
        #        ("rr2'",bi_chars[c_ind+1],ws_left,ws_current),
        #        ("l2l'",bi_chars[c_ind-2],ws_left,ws_current),
        #    ]
        fv+=[   ('L','c' if self.lac_seq[pos][0]=='c' else self.lac_seq[pos][3]),
                ('Ll',self.lac_seq[pos][0],self.lac_seq[pos][1]),
                ('Lr',self.lac_seq[pos][0],self.lac_seq[pos][2]),
                ]
        #fv+=[   ('weibo',self.weibo_seq[pos]),
        #        ]
        #fv+=[   ('skL','c' if self.sanku_seq[pos][0]=='c' else self.sanku_seq[pos][3]),
        #        ('skLl',self.sanku_seq[pos][0],self.sanku_seq[pos][1]),
        #        ('skLr',self.sanku_seq[pos][0],self.sanku_seq[pos][2]),
        #        ]
        fv+=[   
                ('Tc',self.raw_type[c_ind]),
                ('Tl',self.raw_type[c_ind-1]),
                ('Tr',self.raw_type[c_ind+1]),
                ('Tlc',self.raw_type[c_ind-1],self.raw_type[c_ind]),
                ('Tcr',self.raw_type[c_ind],self.raw_type[c_ind+1]),
                #('Tlcr',self.raw_type[c_ind-1],self.raw_type[c_ind],self.raw_type[c_ind+1]),
                #('Tl2lc',self.raw_type[c_ind-2],self.raw_type[c_ind-1],self.raw_type[c_ind]),
                #('Tcrr2',self.raw_type[c_ind],self.raw_type[c_ind+1],self.raw_type[c_ind+2]),
                ]
            

        if len(span)>=4:
            w_current=raw[span[0]-span[3]:span[0]]
            wl=span[0]-span[3]
            fv.append(("w",w_current))
            
            #fv.append("")
            #if w_current:
            #    fv.append(("w1",wl,w_current[-1]))

            fv.append(("wi",w_current in self.idioms))
            fv.append(("wsww",w_current in self.sww))

            if span[3]>1 and wl+4<len(raw):
                if raw[wl:wl+4] in self.idioms:
                    fv.append(("idioms,pre",len(w_current)))
                else:
                    fv.append(("idioms,not",len(w_current)))
                if raw[wl:wl+4] in self.sww:
                    fv.append(("sww,pre",len(w_current)))
                else:
                    fv.append(("sww,not",len(w_current)))
            

            fv.append(("wsms",w_current in self.sms,self.lac_seq[pos][1]))

            dict_info=self.sms_dict.get(w_current,[0,[0,0,0,0,0,0,0,0]])
            #fv.append(('d-',len(w_current),w_current in self.sms_dict))
            fv.append(('d-f',len(w_current),math.floor(math.log(dict_info[0]+1))))
            fv.append(('d-0',len(w_current),dict_info[1][0]))
            fv.append(('d-1',len(w_current),dict_info[1][1]))
            fv.append(('d-2',len(w_current),dict_info[1][2]))
            fv.append(('d-3',len(w_current),dict_info[1][3]))
            fv.append(('d-4',len(w_current),dict_info[1][4]))
            fv.append(('d-5',len(w_current),dict_info[1][5]))
            fv.append(('d-6',len(w_current),dict_info[1][6]))
            #fv.append(('d-7',len(w_current),dict_info[1][7]))

            sgW_info=self.SogouW.get(w_current,[0,set()])
            #fv.append(('sgW',len(w_current),sgW_info[0]>0))
            fv.append(('sgW.t',len(w_current),1 if sgW_info[1] else 0))
            #fv.append(('sgW.t.n',len(w_current),1 if 'N' in sgW_info[1] else 0))
            #fv.append(('sgW.t.v',len(w_current),1 if 'V' in sgW_info[1] else 0))
            #fv.append(('sgW.t.adj',len(w_current),1 if 'ADJ' in sgW_info[1] else 0))
            #fv.append(('sgW.t.pron',len(w_current),1 if 'PRON' in sgW_info[1] else 0))
            #fv.append(('sgW.t.adv',len(w_current),1 if 'ADV' in sgW_info[1] else 0))
            #fv.append(('sgW.t.conj',len(w_current),1 if 'CONJ' in sgW_info[1] else 0))
            #fv.append(('sgW.t.prep',len(w_current),1 if 'PREP' in sgW_info[1] else 0))
            fv.append(('baidu',len(w_current),math.floor(math.log(self.baidu.get(w_current,0)+1))))

            si_info=self.sogou_input.get(w_current,[0,0])
            si_info=[math.floor(math.log(si_info[0]+1)),
                    math.floor(math.log(si_info[1]+1))]
            fv.append(('si',len(w_current),si_info[0],si_info[1]))
            #print('si',w_current,si_info[0],si_info[1])

            
        if len(span)>=5:
            w_left=raw[span[0]-span[3]-span[4]:span[0]-span[3]]
            fv.append(("wl:w",w_left,w_current))
            #fv.append(("wl.l:w",len(w_left),w_current))
            #fv.append(("wl:w.l",w_left,len(w_current)))
            #fv.append(("wl.l:w.l",len(w_left),len(w_current)))
            #w_two=w_left+w_current
            #dict_info_two=self.sms_dict.get(w_two,[0,[0,0,0,0,0,0,0,0]])
            #fv.append(('d2-f',len(w_two),math.floor(math.log(dict_info_two[0]+1))))
            #fv.append(('d2-0',len(w_two),dict_info_two[1][0]))
            #fv.append(('d2-1',len(w_two),dict_info_two[1][1]))
            #fv.append(('d2-2',len(w_two),dict_info_two[1][2]))
            #fv.append(('d2-3',len(w_two),dict_info_two[1][3]))
            #fv.append(('d2-4',len(w_two),dict_info_two[1][4]))
            #fv.append(('d2-5',len(w_two),dict_info_two[1][5]))
            #fv.append(('d2-6',len(w_two),dict_info_two[1][6]))
            
        return fv
class Segmentation_Stats(perceptrons.Base_Stats):
    def __init__(self,actions,features):
        self.actions=actions
        self.features=features
        #初始状态 (解析位置，上一个位置结果，上上个位置结果，当前词长)
        self.init=(0,'|','|',0,0)
    def gen_next_stats(self,stat):
        """
        由现有状态产生合法新状态
        """
        ind,last,_,wordl,lwordl=stat
        yield 's',(ind+1,'s',last,1,wordl)
        yield 'c',(ind+1,'c',last,wordl+1,lwordl)

    def _actions_to_stats(self,actions):
        stat=self.init
        for action in actions:
            yield stat
            ind,last,_,wordl,lwordl=stat
            if action=='s':
                stat=(ind+1,'s',last,1,wordl)
            else:
                stat=(ind+1,'c',last,wordl+1,lwordl)
        yield stat

class Segmentation_Space(perceptrons.Base_Decoder):
    """
    线性搜索
    value = [alphas,betas]
    alpha = [score, delta, action, link]
    """
    def debug(self):
        """
        used to generate lattice
        """
        self.searcher.backward()
        sequence=self.searcher.sequence
        for i,d in enumerate(sequence):
            for stat,alpha_beta in d.items():
                if alpha_beta[1]:
                    for beta,db,action,n_stat in alpha_beta[1]:
                        if beta==None:continue
                        delta=alpha_beta[0][0][0]+beta-self.searcher.best_score
                        if action=='s':
                            pass
    
    def __init__(self,beam_width=8):
        super(Segmentation_Space,self).__init__(beam_width)
        self.init_data={'alphas':[(0,None,None,None)],'betas':[]}
        self.features=Default_Features()
        self.actions=Segmentation_Actions()
        self.stats=Segmentation_Stats(self.actions,self.features)

    def search(self,raw):
        self.raw=raw
        #print(raw)
        #print(self.candidates)
        self.stats.candidates=self.candidates
        self.features.set_raw(raw)
        self.sequence=[{}for x in range(len(raw)+2)]
        self.forward()
        res=self.make_result()
        return res

    def gen_next(self,ind,stat):
        """
        根据第ind步的状态stat，产生新状态，并计算data
        """
        fv=self.features(stat)
        alpha_beta=self.sequence[ind][stat]
        beam=self.sequence[ind+1]
        for action,key in self.stats.gen_next_stats(stat):
            #print(ind,self.candidates[ind],action)
            if self.candidates:
                if self.candidates[ind]!=None and action!=self.candidates[ind]:
                    continue
            #print("pass",ind,self.candidates[ind],action)
            if key not in beam:
                beam[key]={'alphas':[],'betas':[]}
            value=self.actions[action](fv)
            beam[key]['alphas'].append((alpha_beta['alphas'][0][0]+value,value,action,stat))

    def make_result(self):
        """
        由alphas中间的记录计算actions
        """
        sequence=self.sequence
        result=[]
        item=sequence[-1][self.thrink(len(sequence)-1)[0]]['alphas'][0]
        self.best_score=item[0]
        ind=len(sequence)-2
        while True :
            if item[3]==None: break
            result.append(item[2])
            item=sequence[ind][item[3]]['alphas'][0]
            ind-=1
        result.reverse()
        return result
class Weibo_Model(perceptrons.Base_Model):
    """
    模型
    """
    def __init__(self,model_file,schema=None):
        """
        初始化
        """
        super(Weibo_Model,self).__init__(model_file,schema)
        self.codec=tagging_codec
        self.Eval=tagging_eval.TaggingEval
        self.pre=pre.Pre()
    def test(self,test_raw,test_result):
        """
        测试
        """
        eval=self.Eval([DiffToHTML(test_result+'.html')])
        for line,std in zip(open(test_raw),open(test_result)):#迭代每个句子
            line=line.strip()
            std=std.split()
            y=std
            std=pre.gen_std(std)
            std=[t for _,t in sorted(list(std))]
            raw,s=self.pre(line)
            self.schema.candidates=s
            self.schema.features.candidates=s
            assert(len(s)==len(std))
            hat_y=self(raw)
            eval(y,hat_y)
        eval.print_result()#打印评测结果
        return eval
    def train(self,training_raw,training_result,iteration=5):
        """
        训练
        """
        for it in range(iteration):#迭代整个语料库
            eval=self.Eval()#测试用的对象
            sn=0
            for line,std in zip(open(training_raw),open(training_result)):#迭代每个句子
                sn+=1
                #if sn%10==0:
                #    print('('+str(sn)+')',end='')
                #    sys.stdout.flush()
                line=line.strip()
                std=std.split()
                y=std
                std=pre.gen_std(std)
                std=[t for _,t in sorted(list(std))]
                raw,s=self.pre(line)
                self.schema.candidates=s
                self.schema.features.candidates=s
                
                assert(len(s)==len(std))
                
                _,hat_y=self._learn_sentence(raw,y)
                eval(y,hat_y)
            eval.print_result()#打印评测结果
        self.actions.average(self.step)

