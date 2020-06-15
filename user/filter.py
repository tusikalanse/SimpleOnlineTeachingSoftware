# -*- coding: UTF-8 -*-
def filter(s):
    lines = s.split('\n')
    audio = []
    video = []
    flag = 0
    for line in lines:
        if line[0:6] == "[dshow":
            if line.find("video devices") != -1:
                flag = 1
            elif line.find("audio devices") != -1:
                flag = 2
            elif line.find("Alternative name") != -1:
                pass
            else:
                if flag == 1:
                    video.append(line.split("\"")[1])
                elif flag == 2:
                    audio.append(line.split("\"")[1])
    return (video, audio)
