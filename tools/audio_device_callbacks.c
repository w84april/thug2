/* Test-only OS audio interface. Record semantic arguments and configured
 * results/writes. This is not a browser playback implementation. */
#include <stdint.h>
#ifndef AUDIO_CONTEXT
#define AUDIO_CONTEXT 0x1808000
#endif
#define C ((uint32_t *)(uintptr_t)AUDIO_CONTEXT)
#define W(a) (*(uint32_t *)(uintptr_t)(a))
static uint32_t record(uint32_t kind, uint32_t self, const uint32_t *args, uint32_t count) {
    uint32_t *r=C+32+C[0]++*20;
    r[0]=kind;r[1]=self;
    for(unsigned i=0;i<7;++i)r[2+i]=i<count?args[i]:0;
    for(unsigned i=0;i<6;++i)r[9+i]=W(C[16]+i*4);
    r[15]=W(C[18]);r[16]=W(C[17]);r[17]=W(C[17]+4);r[18]=W(C[19]);r[19]=*(uint8_t *)(uintptr_t)C[20];
    if(C[10]==kind){if(C[13]==1)*(uint8_t *)(uintptr_t)C[11]=(uint8_t)C[12];else W(C[11])=C[12];}
    return C[1]==kind?C[2]:0;
}
uint32_t fixture_audio_orientation(uint32_t self,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t flags){uint32_t v[]={a,b,c,d,e,f,flags};return record(0,self,v,7);}
uint32_t fixture_audio_commit(uint32_t self){return record(1,self,0,0);}
uint32_t fixture_audio_min(uint32_t self,uint32_t a,uint32_t flags){uint32_t v[]={a,flags};return record(2,self,v,2);}
uint32_t fixture_audio_max(uint32_t self,uint32_t a,uint32_t flags){uint32_t v[]={a,flags};return record(3,self,v,2);}
uint32_t fixture_audio_position(uint32_t self,uint32_t a,uint32_t b,uint32_t c,uint32_t flags){uint32_t v[]={a,b,c,flags};return record(4,self,v,4);}
uint32_t fixture_audio_volume(uint32_t self,uint32_t a){return record(5,self,&a,1);}
uint32_t fixture_audio_pan(uint32_t self,uint32_t a){return record(6,self,&a,1);}
uint32_t fixture_audio_frequency(uint32_t self,uint32_t a){return record(7,self,&a,1);}
uint32_t fixture_audio_stop(uint32_t self){return record(8,self,0,0);}
uint32_t fixture_audio_release(uint32_t self){return record(9,self,0,0);}
uint32_t fixture_audio_release_spatial(uint32_t self){return record(10,self,0,0);}
uint32_t fixture_audio_create(uint32_t self,uint32_t description,uint32_t output,uint32_t outer){uint32_t v[]={description,output,outer};uint32_t result=record(11,self,v,3);W(output)=C[4];return result;}
uint32_t fixture_audio_query(uint32_t self,uint32_t iid,uint32_t output){uint32_t v[]={iid,output};uint32_t result=record(12,self,v,2);W(output)=C[5];return result;}
uint32_t fixture_audio_lock(uint32_t self,uint32_t offset,uint32_t size,uint32_t first,uint32_t first_size,uint32_t second,uint32_t second_size,uint32_t flags){
    uint32_t v[]={offset,size,flags,C[6],C[7],C[8],C[9]};uint32_t result=record(13,self,v,7);
    W(first)=C[6];W(first_size)=C[7];W(second)=C[8];W(second_size)=C[9];return result;
}
uint32_t fixture_audio_unlock(uint32_t self,uint32_t first,uint32_t first_size,uint32_t second,uint32_t second_size){uint32_t v[]={first,first_size,second,second_size};return record(14,self,v,4);}
uint32_t fixture_audio_seek(uint32_t self,uint32_t position){return record(15,self,&position,1);}
uint32_t fixture_audio_play(uint32_t self,uint32_t a,uint32_t b,uint32_t loop){uint32_t v[]={a,b,loop};return record(16,self,v,3);}
