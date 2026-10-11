for flag,kind in itertools.product([0,1,255,256,257,0xffffffff],[1,3,4,12]):
 g=CommandGraph();s=g.structure([(0x123,kind,g.text('value'))]);out=g.alloc(4);g.put(out,'<I',0x13579bdf)
 run(g,[call(0x476c60,s,[0x123,out,flag]),call(0x476c60,s,[0x124,out,flag])],f'legacy text kind{kind}/flag{flag}')
for mode in ['named','flag','included','absent','zero','missing input']:
 g=CommandGraph();key=0 if mode=='zero' else 0x1234;args=g.structure([] if mode=='absent' else [(0,13,key)] if mode=='flag' else [(key,1,17)])
 if mode=='included':g.symbol(0x8877,10,args);args=g.structure([(0,13,0x8877)])
 g.put(SCRIPTS+20,'<I',args);s=g.structure([] if mode=='missing input' else [(0,13,key)])
 run(g,[call(0x44bd30,args=[s,SCRIPTS])],f'GotParam {mode}')
for a,b in itertools.product([None,0,1,0xffffffff],[None,0,1,0xffffffff]):
 g=CommandGraph();s=g.structure(([] if a is None else [(0x174841bc,13,a)])+([] if b is None else [(0x8e411006,13,b)]))
 run(g,[call(0x44a260,args=[s,SCRIPTS])],f'ChecksumEquals {a}/{b}')
for a,b in [('',''),('none','none'),('None','none'),('different','none'),('a/b','A\\b'),('abcdef','abcdeg'),('\xff','\xff')]:
 for localized in [False,True]:
  g=CommandGraph();s=g.structure([(0x174841bc,4 if localized else 3,g.text(a)),(0x8e411006,3,g.text(b))])
  run(g,[call(0x44a2c0,args=[s,SCRIPTS])],f'StringEquals {a!r}/{b!r}/local{localized}')
