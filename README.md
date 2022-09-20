# snap_analyzer
**snap-analyzer.online** - сервис для расшифровки SNAP'а с систем хранения данных на базе IBM Spectrum Virtualize.
После загрузки архива SNAP сервис визуализирует систему хранения данных, с которого был собран SNAP, выводит информацию об аппаратном составе СХД и характеристики компонентов.

Сервис доступен по адресу http://snap-analyzer.online/

Использовался Python 3.10.2, Django 4.0.7, Bootstrap 5.2.0, БД PostgreSQL 12.12, Gunicorn 20.1.0, Nginx 1.18.0.

**Главная страница, на которой отображен список загруженных SNAP'ов**
![Image text](https://github.com/slepzov/snap_analyzer/blob/main/images/home_page.png?raw=true)

**Страница загрузки SNAP в систему**
![Image text](https://github.com/slepzov/snap_analyzer/blob/main/images/upload_page.png?raw=true)

**Страница СХД**
![Image text](https://github.com/slepzov/snap_analyzer/blob/main/images/storagesystem_page.png?raw=true)

**Страница с информацией о выбранном диске**
![Image text](https://github.com/slepzov/snap_analyzer/blob/main/images/drive_page.png?raw=true)

**Страница с информацией о выбранном контроллере**
![Image text](https://github.com/slepzov/snap_analyzer/blob/main/images/drive_page.png?raw=true)
