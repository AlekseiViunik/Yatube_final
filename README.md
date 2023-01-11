# Yatube_final
![Python version](https://img.shields.io/badge/python-3.7-yellow) ![Django version](https://img.shields.io/badge/django-2.2-red)

```sh
It is a small social network, where users can create/edit/delete posts with picture. 
The other users can comment posts. You can also choose a group for your post.
Everybody who is authenticated can see all the posts of group, all the posts of author.

Небольшая социальная сеть, где пользователи могут добавлять/редактировать и удалять свои посты с картинками.
Другие пользователи могут оставлять комментарии под ними. Так же для каждого поста можно выбрать группу.
Любой, у кого есть доступ, может просматривать все посты группы и все посты автора.
```

## Running project in dev-mode/Запуск проекта в dev-режиме

Clone repository. Install and activate virtual environment./
Клонировать репозиторий. Установить и активировать виртуальное окружение.

```
- For Mac or Linux:
$ python3 -m venv venv
$ source venv/bin/activate

- For Windows
$ python3 -m venv venv
$ source venv/Scripts/activate 
``` 

Install dependencies  from requirements.txt./
Установить зависимости из файла requirements.txt.

```
pip install -r requirements.txt
``` 

Run migrations and run the project./
Выполнить миграции и запустить проект.

```
python3 manage.py migrate
python3 manage.py runserver
``` 
