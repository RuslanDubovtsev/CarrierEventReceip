## Локальный бэкенд для сохранения событий перевозчика и его обработки отдельным worker.

## Схема данных  
   <img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/6e9a6b1b-aa5c-41a4-8326-68e302e5fa70" />  
   
## Состояния  
### Shipment
created — отправление создано;  
in_transit — отправление находится в пути;  
delivered — отправление доставлено.  

**Допустимые переходы:**  
created → in_transit
created → delivered
in_transit → delivered

### Event  
**Поле state определяет состояние события:**  

pending → done  

pending — событие принято webhook и ожидает обработки worker;  
done — событие обработано worker.  

**Результат обработки хранится в поле outcome:**

applied — событие применило допустимый переход статуса Shipment;  
ignored — событие было обработано, но изменение статуса не потребовалось.  

## Запуск 
1. Нужно задать значения переменным в env.example внутри папки project  
2. В консоле `docker compose --env-file ./project/.env up --build`  

## Ручные запросы  
1. Я создал Shipment в админ-панеле Django  
2. Отправка событий:  
``` 
from django.conf import settings
def forming_data():
    url = 'http://localhost:8000/webhooks/delivery'

    headers = {'content-type': 'application/json', 'X-Webhook-Secret': settings.SECRET_WEBHOOK}
    data_1 = [{"event_id": 'e1', "shipment_id": 1, "status": 'delivered'},
            {"event_id": 'e1', "shipment_id": 1, "status": 'in_transit'},
            {"event_id": 'e2', "shipment_id": 3, "status": 'delivered'},
            {"event_id": 'e3', "shipment_id": 3, "status": 'in_transit'},
            {"event_id": 'e3', "shipment_id": 3, "status": 'delivered'}]
    data_2 = [{"event_id": 'e4', "shipment_id": 1, "status": 'in_transit'},
              {"event_id": 'e5', "shipment_id": 1, "status": 'delivered'}]
    data_3 = [{"event_id": 'e6', "shipment_id": 1, "status": 'in_transit'}]


    for elem in data_3:
        res = requests.post(url, json=elem, headers=headers)
        print(res.text)
```  
Отправка производится сторонним программным кодом, отправляющий JSON-запросы.  
data-1 тестирует штатную работу валидации в вебхуке и проверяет обработку ошибки в воркере: e2 является одноразовым триггером для выброса ошибки  
data-2 тестирует обработку двух одновременных запросов двумя воркерами  
data-3 тестирует воркер на недопуск изменения существующей отправки  
3. `python manage.py worker --start` - запускает воркер. Сообщения выходят прямо в терминал.  
При запуске докера воркер открывается автоматически, при желании можно запустить еще одни отдельно командой: `docker-compose exec web python manage.py worker --start`  
## Демонстрация сбоя
<img width="657" height="137" alt="image" src="https://github.com/user-attachments/assets/c488ffa1-94c4-4650-8bce-96b909da00c8" />    

Сначала произошел сбой, но через 5 секунд воркер повторно и успешно обработал событие  

## Workflow

Работает, доступен в Actions