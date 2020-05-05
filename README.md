# KHUKIE Air

2020년 1학기 클라우드컴퓨팅 G조입니다.
Dropbox와 유사한 기능 개발이 목표입니다.

## 팀원 
- 2017103964 컴퓨터공학과 김명현
- 2016104131 컴퓨터공학과 안영민
- 2018102223 컴퓨터공학과 임주현
- 2016104170 컴퓨터공학과 최원영
- 2015104235 컴퓨터공학과 황지원

## KHUHub
[KHUHub Repository](http://khuhub.khu.ac.kr/2020-1-CloudComputing/G_Team_KHUKIE_Air)

## How to Start
Python 3.6 이상이 설치된 Windows 환경 기준으로 작성했습니다.

```
$ git clone https://github.com/khukie-air/khukie-air
$ cd khukie-air

$ pip install virtualenv
$ virtualenv venv
$ venv/scripts/activate

(venv) $ pip install -r requirements.txt

(venv) $ python manage.py migrate
(venv) $ python manage.py runserver
```