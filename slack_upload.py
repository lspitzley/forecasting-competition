#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 16:43:14 2020

@author: leespitzley
"""
# https://stackoverflow.com/questions/43464873/how-to-upload-files-to-slack-using-file-upload-and-requests

import requests
import yaml
#%% upload file

filepath = "tokens.yaml"
with open(filepath, 'r') as f:
    keys = yaml.safe_load(f)
# post data to Slack
token = keys['token']
print(token)

#%% upload forecast file to Slack
def upload_forecast_file(token):
    my_file = {
      'file' : ('last_ten_alb.csv', open('last_ten_alb.csv', 'rb'), 'csv')
    }
    
    payload={
      "filename":"last_ten_alb.csv", 
      "token":token, 
      "channels":['#forecasting'], 
    }
    
    r = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)
    print(r)
    print(r.text)


#%% read file to bot
payload ={
  "token":token, 
  "channels":'#B01AJRTQJLE',
  "types" : "csv"}
headers = {'Content-Type': 'application/json'}
get = requests.get('https://slack.com/api/files.list', params=payload, headers=headers)
print(get)
print(get.json()["files"][0]["name"])
print(get.text)
# with open()


#%% files to the bot
# U01ARHWDLN6 # bot
# user: U018ZK7MD7D
payload ={
  "token":token, 
 "channels":'U01ARHWDLN6'}
headers = {'Content-Type': 'application/json'}
get = requests.get('https://slack.com/api/conversations.members', params=payload)
print(get)
#print(get.json()["files"][0]["name"])
print(get.text)
for convo in get.json()["channels"]:
    print(convo["name"])


#%% convo list
payload ={
  "token":token,
  "types": "im",
  "channel": "D01AJSEBX38"}
headers = {'Content-Type': 'application/json'}
get = requests.get('https://slack.com/api/conversations.history', params=payload)
print(get)
#print(get.json()["files"][0]["name"])
print(get.text)
for convo in get.json()["channel"]:
    print(convo["user"])



#%% get bot info
payload = {"token":token, 
}
bot= requests.get('https://slack.com/api/auth.test', params=payload)
print(bot.json())
print(bot.text)
