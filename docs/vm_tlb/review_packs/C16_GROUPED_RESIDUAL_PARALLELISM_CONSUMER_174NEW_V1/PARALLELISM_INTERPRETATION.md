# 并行度解释

split8在M1/M16/M32仍有优势，g1分别为-126.7%/-87.4%/-27.3%，但随split1 CTA从96到192增加而衰减；M64时split1反超约4.93%，bootstrap区间为[4.50%, 5.13%]。split1 TEX read-side L2 hit全程保持高位。残余split8价值集中在低CTA供给/partial-tile与reduction权衡，属于已有parallel decomposition问题；当前Split-K支线可以关闭。
