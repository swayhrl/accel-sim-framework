#include <cassert>
#include <cstdio>
struct packet {};
struct subpart { unsigned calls=0; bool set_done(packet*) { ++calls; return true; } };
struct tvd_directory { enum result { OK }; unsigned calls=0; result set_done(unsigned,unsigned) { ++calls; return OK; } };
int main() {
 subpart sub;subpart *m_sub_partition[]={&sub};unsigned dest_spid=0;packet p;packet*mf_return=&p;
const bool done = m_sub_partition[dest_spid]->set_done(mf_return);
          assert(done);
          (void)done;
 tvd_directory directory;auto*m_tvd=&directory;unsigned t=0,cycle=1;
const auto completion_status = m_tvd->set_done(t,cycle);
    assert(completion_status==tvd_directory::OK);
    (void)completion_status;
 if(sub.calls!=1||directory.calls!=1) return 99;
 puts("PASS both production completion callbacks executed once");return 0;
}
