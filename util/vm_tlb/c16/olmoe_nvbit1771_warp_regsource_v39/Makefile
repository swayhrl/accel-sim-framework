NVCC=nvcc -ccbin=$(CXX) -D_FORCE_INLINES
PTXAS=ptxas
BIN2C=bin2c
NVBIT_PATH=/data/c16/env/nvbit-1.7.7.1/core
INCLUDES=-I$(NVBIT_PATH) -I.
LIBS=-L$(NVBIT_PATH) -lnvbit
NVCC_PATH=-L /usr/local/cuda-12.8/lib64
ARCH?=all
TOOL=nvbit1771_warp_regsource_v39.so

all: $(TOOL)

tool_func/flush_channel.fatbin: tool_func/flush_channel.cu
	$(NVCC) -arch=$(ARCH) $(INCLUDES) -O3 -fatbin $< -o $@

tool_func/flush_channel.c: tool_func/flush_channel.fatbin
	$(BIN2C) -c --name flush_channel_bin $< > $@

c16warp1_v39_inject.o: c16warp1_v39_inject.cu c16warp1_v39_common.h
	$(NVCC) $(INCLUDES) -Xptxas -astoolspatch --keep-device-functions -arch=$(ARCH) -Xcompiler -fPIC -c $< -o $@

c16warp1_v39_tool_impl.o: c16warp1_v39_tool_impl.cu c16warp1_v39_common.h tool_func/flush_channel.c
	$(NVCC) -dc -c -std=c++11 $(INCLUDES) -Xptxas -cloning=no -Xcompiler -Wall -arch=$(ARCH) -O3 -Xcompiler -fPIC $< -o $@

$(TOOL): c16warp1_v39_inject.o c16warp1_v39_tool_impl.o $(NVBIT_PATH)/libnvbit.a
	$(NVCC) -arch=$(ARCH) -O3 c16warp1_v39_inject.o c16warp1_v39_tool_impl.o $(LIBS) $(NVCC_PATH) -lcuda -lcudart_static -shared -o $@

clean:
	rm -f $(TOOL) *.o tool_func/flush_channel.fatbin tool_func/flush_channel.c
