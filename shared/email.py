# # -*- coding: utf-8 -*-
# from mailjet_rest import Client
# import os
#
# class Email(object):
#     def __init__(self, subject, html, destinations, text=None):
#         self.subject = subject
#         self.html = html
#         if text is None:
#             self.text = html
#         self.destinations = []
#         for destination in destinations:
#             email = {'Email': destination}
#             self.destinations.append(email)
#         self.client = Client(auth=(os.environ["MJ_USER"], os.environ["MJ_P"]), version='v3')
#
#     def send(self):
#         email = {
#             'FromName': 'A3UAV Pilot Training (no reply)',
#             'FromEmail': 'no.reply@uavpilottraining.a3uav.com',
#             'Subject': self.subject,
#             'Text-Part': self.text,
#             'Html-Part': self.html,
#             'Recipients': self.destinations
#         }
#         self.client.send.create(email)