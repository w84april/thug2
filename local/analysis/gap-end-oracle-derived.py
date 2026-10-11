"""Shared original-instruction fixture runner for script heap operations.

Concrete game functions run unchanged, with pools disabled. Heap operations are
recorded at the same boundaries as script_values_memory.c. This is test support,
not recovered allocator behavior.
"""
import struct
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import load

class ScriptHeapOracle:
    def __init__(self,initial,base,context,manager,globals_,defaults,functions,observe=(),event_limit=1200,instruction_limit=4000000,scope_entries=None):
        self.initial=bytes(initial);self.base=base;self.context=context;self.manager=manager
        self.globals=globals_;self.defaults=defaults;self.functions=functions
        self.cases=[];self.counts=Counter();self.coverage=Counter();self.heap_events=Counter()
        self.event_limit=event_limit;self.instruction_limit=instruction_limit
        self.scope_entries=scope_entries if scope_entries is not None else {manager+0x200:1}
        self.stack=0x3000000;self.stop=0x3f00000
        pe=load();self.cpu=cpu=Uc(UC_ARCH_X86,UC_MODE_32)
        cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
        cpu.mem_write(0x400000,pe.get_memory_mapped_image())
        for at,size in [(0,4096),(base,(len(initial)+4095)&~4095),(self.stack,0x20000),(self.stop,4096)]:cpu.mem_map(at,size)
        cpu.mem_write(self.stop+32,b'\xdd\x1d'+struct.pack('<I',self.stack+0x100)+b'\xe9'+struct.pack('<i',-43))
        for index,table in [(0x6f2338,0x6f2340),(0x6f3644,0x6f364c),(0x6f3654,0x6f365c),(0x6f3614,0x6f361c),(0x6f22b4,0x6f22bc)]:
            cpu.mem_write(index,bytes(4));cpu.mem_write(table,bytes(8))
        self.setword(0x7d1800,manager);cpu.mem_write(0x7cc979,b'\x01')
        for at in [0x5bbae0,0x5bafc0,0x5ba0b0,0x5baba0,0x5bb0e0,0x5bb110]:cpu.hook_add(UC_HOOK_CODE,self.heap,begin=at,end=at)
        for at in observe:cpu.hook_add(UC_HOOK_CODE,self.observe,begin=at,end=at)
    def word(self,at):return int.from_bytes(self.cpu.mem_read(at,4),'little')
    def setword(self,at,value):self.cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
    def record(self,kind,a,b,c):
        index=self.word(self.context+8);assert index<self.event_limit
        log=self.word(self.context+12)+index*48;self.setword(self.context+8,index+1)
        pointer=a if kind==2 else c;valid=int(self.base<=pointer<=self.base+len(self.initial)-16)
        snapshot=list(struct.unpack('<4I',self.cpu.mem_read(pointer,16))) if valid else [0]*4
        watch=self.word(self.context+24)
        self.cpu.mem_write(log,struct.pack('<12I',kind,a,b,c,*snapshot,valid,watch,self.word(watch) if watch else 0,0))
    def heap(self,cpu,address,size,user):
        sp=cpu.reg_read(UC_X86_REG_ESP);cleanup=0;result=0
        if address in [0x5bbae0,0x5bafc0]:
            requested=self.word(sp+4);route=int(address==0x5bafc0)
            if route:assert self.word(sp+8)==1 and self.word(sp+12)==0;cleanup=12
            result=self.word(self.context);assert result+requested+16<=self.word(self.context+4)
            self.setword(self.context,(result+requested+19)&~3)
            if requested:cpu.mem_write(result,b'\xa5'*requested)
            self.record(1,requested,route,result)
        elif address in [0x5ba0b0,0x5baba0]:
            self.record(2,self.word(sp+4),0,0);cleanup=4 if address==0x5baba0 else 0
        else:
            enter=int(address==0x5bb0e0)
            if enter:enter=self.scope_entries[self.word(sp+4)];cleanup=4
            self.setword(self.context+28,enter);self.record(3,enter,0,0)
        self.heap_events[hex(address)]+=1
        cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,self.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
    def observe(self,cpu,address,size,user):self.coverage[hex(address)]+=1
    def global_read(self,entry):return int.from_bytes(self.cpu.mem_read(entry[1],entry[2]),'little')
    def case(self,calls,patches=(),changes=None):
        self.indeterminate.clear();self.compressions.clear();self.end_labels.clear()
        expected=bytearray(self.initial);global_values=list(self.defaults);cpu=self.cpu
        for k,value in (changes or {}).items():global_values[k]=value
        for at,data in patches:
            data=bytes.fromhex(data);expected[at-self.base:at-self.base+len(data)]=data
        cpu.mem_write(self.base,bytes(expected));cpu.mem_write(0,b'\xa5'*4)
        for entry,value in zip(self.globals,global_values):cpu.mem_write(entry[1],value.to_bytes(entry[2],'little'))
        stages=[]
        for fn,this,args in calls:
            f=self.functions[hex(fn)];sp=self.stack+0x18000
            stack_args=[args[i] for i in f['stack_args']] if 'stack_args' in f else args
            cpu.mem_write(sp,struct.pack('<'+'I'*(len(stack_args)+1),self.stop+32 if f['result']=='double' else self.stop,*stack_args))
            cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad)
            for name,index in f.get('register_args',{}).items():
                cpu.reg_write({'eax':UC_X86_REG_EAX,'ebx':UC_X86_REG_EBX,'ecx':UC_X86_REG_ECX,'edx':UC_X86_REG_EDX,'esi':UC_X86_REG_ESI}[name],args[index])
            cpu.reg_write(UC_X86_REG_FPCW,0x7f)
            try:cpu.emu_start(fn,self.stop,count=self.instruction_limit)
            except Exception as error:raise RuntimeError((len(self.cases),hex(fn),hex(cpu.reg_read(UC_X86_REG_EIP)))) from error
            assert cpu.reg_read(UC_X86_REG_EIP)==self.stop and cpu.reg_read(UC_X86_REG_ESP)==sp+4+f['cleanup'],(len(self.cases),hex(fn))
            assert bytes(cpu.mem_read(0,4))==b'\xa5'*4
            after=bytes(cpu.mem_read(self.base,len(expected)));outputs=[]
            for page in range(0,len(expected),4096):
                if after[page:page+4096]!=expected[page:page+4096]:
                    for i in range(page,min(page+4096,len(expected)),4):
                        if after[i:i+4]!=expected[i:i+4]:outputs.append([self.base+i,after[i:i+4].hex()])
            expected=bytearray(after)
            result=None if f['result']=='void' else cpu.reg_read(UC_X86_REG_EAX)
            if f['result']=='byte':result &= 255
            if f['result']=='half':result &= 65535
            if f['result']=='wide':result=str((cpu.reg_read(UC_X86_REG_EDX)<<32)|result)
            if f['result']=='double':
                result=bytes(cpu.mem_read(self.stack+0x100,8)).hex()
            stages.append({'fn':hex(fn),'this':this,'args':args,'result':result,
                'outputs':outputs,'globals':[self.global_read(g) for g in self.globals],'callbacks':0,'indeterminate_bytes':self.indeterminate_ranges(),'compression_records':list(self.compressions),'stack_texts':self.stack_texts(fn)})
            self.counts[f['name']]+=1
        self.cases.append({'patches':list(patches),'globals':global_values,'steps':stages});return stages
