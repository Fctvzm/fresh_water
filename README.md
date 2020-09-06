# Automated water ordering using object detection (Yolo) and Telegram bot

### Collected own dataset of empty and full water containers, labeled and used [Yolo](https://pjreddie.com/darknet/yolo/) for training

Client (ip camera) sends video frames to server which detects bottles in picture and cound empty and full bottles, and if all containers are empty sends notification by Telegram bot to order water bottles.

Tech Stack: Python, Django, Twisted, Opencv

![Image notification telegram bot example](https://i.postimg.cc/L6Yqn92P/photo-2020-09-07-00-58-20.jpg)
![](https://i.postimg.cc/yxJNgj4K/photo-2020-09-07-00-58-16.jpg)
