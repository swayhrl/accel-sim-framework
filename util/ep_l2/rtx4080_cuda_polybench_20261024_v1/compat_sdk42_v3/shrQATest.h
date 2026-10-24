#pragma once
#include <stdio.h>
#include <stdlib.h>
enum QAstatus {QA_FAILED=0,QA_PASSED=1,QA_WAIVED=2};
template<class T> inline void shrQAStart(int,T){printf("SDK42_HOST_ADAPTER_QA_START\n");}
template<class T> inline void shrQAFinishExit(int,T,QAstatus s){printf("SDK42_HOST_ADAPTER_QA_%s\n",s==QA_PASSED?"PASSED":s==QA_WAIVED?"WAIVED":"FAILED");exit(s==QA_PASSED?0:s==QA_WAIVED?2:1);}
