/*
Extracted portions of gpu-cache.h / gpu-cache.cc retain the following notice:

Copyright (c) 2009-2021, Tor M. Aamodt, Tayler Hetherington,
Vijay Kandiah, Nikos Hardavellas, Mahmoud Khairy, Junrui Pan,
Timothy G. Rogers
The University of British Columbia, Northwestern University, Purdue
University All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer;
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution;
3. Neither the names of The University of British Columbia, Northwestern
University nor the names of their contributors may be used to
endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/
// Exact tag_array::probe body plus a minimal cache/config fixture.
// This is NOT a full cache_cycle()/ft_access() build or an application result.
#include <array>
#include <bitset>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
using new_addr_type = std::uint64_t;
using mem_access_sector_mask_t = std::bitset<4>;
struct mem_fetch {};
enum cache_block_state {INVALID=0,RESERVED,VALID,MODIFIED};
enum cache_request_status {HIT=0,HIT_RESERVED,MISS,RESERVATION_FAIL,SECTOR_MISS};
enum {LRU=0,FIFO,ON_MISS};
struct cache_block_t {
  new_addr_type m_tag=0;
  std::array<cache_block_state,4> m_status{{INVALID,INVALID,INVALID,INVALID}};
  unsigned long long m_line_last_access_time=0,m_line_alloc_time=0,m_line_fill_time=0;
  unsigned get_sector_index(mem_access_sector_mask_t m) const {
    assert(m.count()==1); for(unsigned i=0;i<4;++i)if(m[i])return i; std::abort();
  }
  cache_block_state get_status(mem_access_sector_mask_t m) const {return m_status[get_sector_index(m)];}
  bool is_readable(mem_access_sector_mask_t) const{return true;}
  bool is_invalid_line() const{for(auto s:m_status)if(s!=INVALID)return false;return true;}
  bool is_valid_line() const{return !is_invalid_line();}
  bool is_reserved_line() const{for(auto s:m_status)if(s==RESERVED)return true;return false;}
  bool is_modified_line() const{for(auto s:m_status)if(s==MODIFIED)return true;return false;}
  unsigned long long get_last_access_time() const{return m_line_last_access_time;}
  unsigned long long get_alloc_time() const{return m_line_alloc_time;}
  // Source sector_cache_block::fill makes RESERVED -> VALID (without modified-
  // on-fill) and updates fill time, NOT the line's last-access or allocation time.
  void model_unmodified_sector_fill(unsigned s,unsigned long long time){
    m_status[s]=VALID;m_line_fill_time=time;
  }
};
struct cache_config {
 unsigned m_assoc=16,m_nset=1,m_wr_percent=0,m_replacement_policy=LRU,m_alloc_policy=ON_MISS;
 unsigned set_index(new_addr_type)const{return 0;}
 new_addr_type tag(new_addr_type a)const{return a;}
};
struct tag_array {
 cache_config m_config;
 unsigned m_dirty=1;
 std::vector<cache_block_t*> m_lines;
 cache_request_status probe(new_addr_type,unsigned&,mem_access_sector_mask_t,bool,bool,mem_fetch*)const;
};
enum cache_request_status tag_array::probe(new_addr_type addr, unsigned &idx,
                                           mem_access_sector_mask_t mask,
                                           bool is_write, bool probe_mode,
                                           mem_fetch *mf) const {
  // assert( m_config.m_write_policy == READ_ONLY );
  unsigned set_index = m_config.set_index(addr);
  new_addr_type tag = m_config.tag(addr);

  unsigned invalid_line = (unsigned)-1;
  unsigned valid_line = (unsigned)-1;
  unsigned long long valid_timestamp = (unsigned)-1;
  unsigned dirty_line = (unsigned)-1;
  unsigned long long dirty_timestamp = (unsigned)-1;

  bool all_reserved = true;
  // check for hit or pending hit
  for (unsigned way = 0; way < m_config.m_assoc; way++) {
    unsigned index = set_index * m_config.m_assoc + way;
    cache_block_t *line = m_lines[index];
    if (line->m_tag == tag) {
      if (line->get_status(mask) == RESERVED) {
        idx = index;
        return HIT_RESERVED;
      } else if (line->get_status(mask) == VALID) {
        idx = index;
        return HIT;
      } else if (line->get_status(mask) == MODIFIED) {
        if ((!is_write && line->is_readable(mask)) || is_write) {
          idx = index;
          return HIT;
        } else {
          idx = index;
          return SECTOR_MISS;
        }

      } else if (line->is_valid_line() && line->get_status(mask) == INVALID) {
        idx = index;
        return SECTOR_MISS;
      } else {
        assert(line->get_status(mask) == INVALID);
      }
    }
    if (!line->is_reserved_line()) {
      all_reserved = false;
      // percentage of dirty lines in the cache
      // number of dirty lines / total lines in the cache
      float dirty_line_percentage =
          ((float)m_dirty / (m_config.m_nset * m_config.m_assoc)) * 100;
      // If the cacheline is from a load op (not modified),
      // or the total dirty cacheline is above a specific value,
      // Then this cacheline is eligible to be considered for replacement
      // candidate i.e. Only evict clean cachelines until total dirty cachelines
      // reach the limit.
      if (!line->is_modified_line() ||
          dirty_line_percentage >= m_config.m_wr_percent) {
        if (line->is_invalid_line()) {
          invalid_line = index;
        } else {
          // valid line : keep track of most appropriate replacement candidate
          if (m_config.m_replacement_policy == LRU) {
            if (line->get_last_access_time() < valid_timestamp) {
              valid_timestamp = line->get_last_access_time();
              valid_line = index;
            }
          } else if (m_config.m_replacement_policy == FIFO) {
            if (line->get_alloc_time() < valid_timestamp) {
              valid_timestamp = line->get_alloc_time();
              valid_line = index;
            }
          }
        }
      } else if ((m_config.m_replacement_policy == LRU &&
                  line->get_last_access_time() < dirty_timestamp) ||
                 (m_config.m_replacement_policy == FIFO &&
                  line->get_alloc_time() < dirty_timestamp)) {
        // Dirty-ratio selection is a preference, never an availability rule.
        // If this set has no clean candidate, retain its oldest dirty line as
        // the conventional replacement fallback.
        dirty_timestamp = (m_config.m_replacement_policy == LRU)
                              ? line->get_last_access_time()
                              : line->get_alloc_time();
        dirty_line = index;
      }
    }
  }
  if (all_reserved) {
    assert(m_config.m_alloc_policy == ON_MISS);
    return RESERVATION_FAIL;  // miss and not enough space in cache to allocate
                              // on miss
  }

  if (invalid_line != (unsigned)-1) {
    idx = invalid_line;
  } else if (valid_line != (unsigned)-1) {
    idx = valid_line;
  } else if (dirty_line != (unsigned)-1) {
    idx = dirty_line;
  } else
    abort();  // if an unreserved block exists, it is either invalid or
              // replaceable

  return MISS;
}

int main(int argc,char**argv){
 std::array<cache_block_t,16> blocks;
 tag_array tags;
 for(unsigned i=0;i<16;++i){
  blocks[i].m_tag=(i+1)*128;
  blocks[i].m_status[0]=RESERVED;
  blocks[i].m_line_last_access_time=100+i;
  blocks[i].m_line_alloc_time=100+i;
  tags.m_lines.push_back(&blocks[i]);
 }
 blocks[0].m_status[0]=RESERVED;
 blocks[0].m_line_last_access_time=1;blocks[0].m_line_alloc_time=1;
 blocks[1].m_status[0]=MODIFIED;
 blocks[1].m_line_last_access_time=2;blocks[1].m_line_alloc_time=2;
 unsigned index=~0U;
 const new_addr_type incoming=0x10000;
 assert(tags.probe(incoming,index,mem_access_sector_mask_t(1),false,true,nullptr)==MISS);
 assert(index==1);
 const unsigned pending_tag_index=index;
 // In B16 ft_access: p.tag_index=1, copy phase0 reads dirty victim then returns
 // RESERVATION_FAIL. No tag reservation is installed on that path.
 // All other ways are pending; the dirty fallback is the only eligible victim.
 // Next cache cycle's DRAM-fill phase precedes the retry of the frontend head.
 blocks[0].model_unmodified_sector_fill(0,200);
 const auto probe=tags.probe(incoming,index,mem_access_sector_mask_t(1),false,true,nullptr);
 assert(probe==MISS);
 assert(index==0&&index!=pending_tag_index);
 std::cout<<"REPRO B16 replacement target: pending tag="<<pending_tag_index
          <<", reprobe after unrelated fill="<<index
          <<"; original ft_access invariant is false"<<std::endl;
 if(argc>1&&std::string(argv[1])=="--invoke-original-assert") {
   assert(pending_tag_index==index && probe==MISS);
 }
}
