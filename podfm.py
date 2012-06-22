#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import urllib
from ghost import Ghost

# Bugfix для работы с Ghost.py в Windows
# https://github.com/jeanphix/Ghost.py/commit/6e826426d55801974eaed443a3260e0ab24761f0

###################### НАСТРОЙКИ ##########################
# Если выдает ошибку Exception: Unable to load requested page
# увеличить параметр таймаута в строке
timeout = 30

# Если не указан файл с картинкой, скачается по этому URL. Можно указать свой.
default_img_url = 'http://www.jessicaadams.com/wp-content/uploads/2009/12/podcast-headphones.jpg'

# Имя пользователя на podfm
user = 'user'

# Пароль на podfm
passwd = 'password'

# Оформление подкаста
podcast = {
            # Дата и время публикации
            'day': '1',
            'month': '1',
            'year': '2013',
            'hour': '0',
            'min': '0',
            # Номер выпуска
            'number': '100',
            # Название
            'name': u'Новый выпуск подкаста',
            # Лид (краткое описание)
            'short_descr': u'Краткое описание нового выпуска',
            # Полное описание (шоуноты)
            'body': u'''Шоуноты к подкасту''',
            # Автоформатирование
            'format': '1',
            # Подпись к картинке
            'image_alt': 'images.google.com',
            # Идентификатор ленты. Указать свой
            'lent_id': '11652',
            # Категория подкаста. Указать (33 - Дневники)
            'cat_id': '33'
          }
add_page = 'http://%s.podfm.ru/add' % user
###########################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=u'Автоматическая публикация подкаста на podfm.ru')
    parser.add_argument(u'-f', u'--file',
                        dest=u'file',
                        help=u'файл подкаста в формате MP3 (указать обязательно)')
    parser.add_argument(u'-i', u'--image',
                        dest=u'image',
                        help=u'файл с рисунком к оформлению выпуска.\
                            \nЕсли не указать, скачается дефолтный.')
    args = parser.parse_args()

    if not args.file or '.mp3' not in args.file:
        print u'Запустите с ключом -h или --help'
        sys.exit(1)

    if not args.image:
        args.image = 'image.jpg'
        urllib.urlretrieve(default_img_url, args.image)
    podcast['image'] = args.image

    ghost = Ghost(wait_timeout=timeout)

    # Получаем страницу с формой логина
    page, resources = ghost.open(add_page)
    assert page.http_status == 200 and 'loginForm' in ghost.content

    # Заполняем форму логина
    ghost.fill('#loginForm',
                {
                    'login': user,
                    'password': passwd
                }
               )
    page, resources = ghost.fire_on('#loginForm',
                                    'submit',
                                    expect_loading=True)
    assert page.http_status == 200 and u'Выход' in ghost.content

    # Получаем страницу с формой добавления файла
    page, resources = ghost.open(add_page)
    assert page.http_status == 200 and 'formulaire' in ghost.content

    # Заполняем форму добавления файла
    ghost.fill('#formulaire', {'file': args.file})
    page, resources = ghost.fire_on('#formulaire',
                                    'submit',
                                    expect_loading=True)
    assert page.http_status == 200 and 'myform' in ghost.content

    # Заполняем данные о подкасте
    ghost.fill('#myform', podcast)
    page, resources = ghost.fire_on('#myform', 'submit', expect_loading=True)
