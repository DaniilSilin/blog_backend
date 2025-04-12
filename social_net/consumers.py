# from .models import *
# from .serializers import *
# from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
#
# import json
#
# from channels.generic.websocket import WebsocketConsumer
#
# class WSConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#     def disconnect(self, close_code):
#         pass
#
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         self.send(text_data=json.dumps({
#             'message': f'Hello, you sent -> {message}'
#         }))
#
#
# class BlogSubscribeConsumer(WebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         pass
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         await self.send(text_data=json.dumps({
#             'message': 'Вы подписались!'
#         }))