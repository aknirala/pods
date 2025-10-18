#ffmpeg -i -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" 
ffmpeg -i 'Google DeepMind CEO Demis Hassabis on AI, Creativity, and a Golden Age of Science ｜ All-In Summit [Kr3Sh2PKA8Y].mp4' -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" AllIn_Demis.mp4
ffmpeg -i 'How to Expand Your Consciousness ｜ Dr. Christof Koch [2t4vswC-3mY].mp4' -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" Huber_Cons.mp4
ffmpeg -i 'Eric Schmidt on AI, the Battle with China, and the Future of America [EkuVqdj8O6E].mp4' -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" AllIn_EricAI.mp4
ffmpeg -i 'Biggest LBO Ever, SPAC 2.0, Open Source AI Models, State AI Regulation Frenzy [ddAwgZ6ietc].mp4' -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" AllIn_AIFrenzy.mp4
ffmpeg -i 'No. 1 Sugar Expert： This Diet Kills Your Sugar Cravings Completely! [ZE_H7rijrVk].mp4' -vf "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'" KillSugarCraving.mp4
