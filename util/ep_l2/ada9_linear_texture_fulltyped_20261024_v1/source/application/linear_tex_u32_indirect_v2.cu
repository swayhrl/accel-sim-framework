#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#define CK(x) do { cudaError_t e=(x); if(e!=cudaSuccess){fprintf(stderr,"CUDA_FAIL %s %s\n",#x,cudaGetErrorString(e));return 2;} }while(0)
__global__ void linear_tex_u32(const cudaTextureObject_t* handles,const int* indices,unsigned* output){
 cudaTextureObject_t tex=handles[0];
 int tid=threadIdx.x;
 int index=indices[tid];
 output[tid]=tex1Dfetch<unsigned int>(tex,index);
}
int main(){
 const int N=128,T=37; std::vector<unsigned> input(N),output(T);std::vector<int> index(T);
 for(int i=0;i<N;++i)input[i]=0x12340000u+i*19u;
 for(int i=0;i<T;++i)index[i]=(i*13+7)%N;
 unsigned *backing=nullptr,*out=nullptr;int* coords=nullptr;
 CK(cudaMalloc(&backing,N*sizeof(unsigned)));CK(cudaMalloc(&out,T*sizeof(unsigned)));CK(cudaMalloc(&coords,T*sizeof(int)));
 CK(cudaMemcpy(backing,input.data(),N*sizeof(unsigned),cudaMemcpyHostToDevice));
 CK(cudaMemcpy(coords,index.data(),T*sizeof(int),cudaMemcpyHostToDevice));
 cudaResourceDesc rd={};rd.resType=cudaResourceTypeLinear;rd.res.linear.devPtr=backing;rd.res.linear.desc=cudaCreateChannelDesc<unsigned int>();rd.res.linear.sizeInBytes=N*sizeof(unsigned);
 cudaTextureDesc td={};td.addressMode[0]=cudaAddressModeClamp;td.filterMode=cudaFilterModePoint;td.readMode=cudaReadModeElementType;td.normalizedCoords=0;
 cudaTextureObject_t tex=0;CK(cudaCreateTextureObject(&tex,&rd,&td,nullptr));
 cudaTextureObject_t* handleBuffer=nullptr;CK(cudaMalloc(&handleBuffer,sizeof(tex)));CK(cudaMemcpy(handleBuffer,&tex,sizeof(tex),cudaMemcpyHostToDevice));
 FILE* hf=fopen("HOST_HANDLE_U64.bin","wx");if(!hf)return 2;fwrite(&tex,sizeof(tex),1,hf);fclose(hf);
 cudaResourceDesc qr={};cudaTextureDesc qt={};CK(cudaGetTextureObjectResourceDesc(&qr,tex));CK(cudaGetTextureObjectTextureDesc(&qt,tex));
 cudaPointerAttributes pa={};CK(cudaPointerGetAttributes(&pa,backing));
 FILE* f=fopen("APP_RESOURCE.json","wx");if(!f)return 2;
 fprintf(f,"{\"texture_object\":\"0x%llx\",\"actual_backing_pointer\":\"0x%llx\",\"queried_backing_pointer\":\"0x%llx\",\"pointer_attributes_device_pointer\":\"0x%llx\",\"resource_type\":%d,\"size_bytes\":%zu,\"channel_bits\":[%d,%d,%d,%d],\"channel_kind\":%d,\"filter_mode\":%d,\"read_mode\":%d,\"normalized_coords\":%d,\"N\":%d,\"threads\":%d}\n",(unsigned long long)tex,(unsigned long long)backing,(unsigned long long)qr.res.linear.devPtr,(unsigned long long)pa.devicePointer,(int)qr.resType,qr.res.linear.sizeInBytes,qr.res.linear.desc.x,qr.res.linear.desc.y,qr.res.linear.desc.z,qr.res.linear.desc.w,(int)qr.res.linear.desc.f,(int)qt.filterMode,(int)qt.readMode,qt.normalizedCoords,N,T);fclose(f);
 f=fopen("HOST_INPUT_U32.bin","wx");if(!f)return 2;fwrite(input.data(),4,N,f);fclose(f);
 f=fopen("HOST_INDICES_I32.bin","wx");if(!f)return 2;fwrite(index.data(),4,T,f);fclose(f);
 linear_tex_u32<<<1,T>>>(handleBuffer,coords,out);CK(cudaGetLastError());CK(cudaDeviceSynchronize());
 CK(cudaMemcpy(output.data(),out,T*sizeof(unsigned),cudaMemcpyDeviceToHost));
 for(int i=0;i<T;++i)if(index[i]<0||index[i]>=N||output[i]!=input[index[i]]){fprintf(stderr,"FULL_REFERENCE_FAIL %d\n",i);return 2;}
 f=fopen("HOST_OUTPUT_U32.bin","wx");if(!f)return 2;fwrite(output.data(),4,T,f);fclose(f);
 CK(cudaFree(handleBuffer));CK(cudaDestroyTextureObject(tex));CK(cudaFree(coords));CK(cudaFree(out));CK(cudaFree(backing));puts("FULL_CPU_REFERENCE_PASS 37 of 37; LINEAR_U32_INBOUNDS; one launch grid1 block37");return 0;
}
