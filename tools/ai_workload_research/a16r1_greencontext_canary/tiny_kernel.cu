extern "C" __global__ void a16r1_integer_canary(unsigned int* output, unsigned int n) {
 const unsigned int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n)output[i]=3u*i+11u;
}
