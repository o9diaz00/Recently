# The purpose of this script is to update the GUI and remove hosts that are no longer active.  It doesn't seem as if CrowdStrike automatically removes hosts that no longer exist, so in an ephemeral environment, the GUI will still list hosts that have long been cycled #

import requests;
import json;
import sys;
import time;

## #####################
##  Global Variables  ##
########################
# start_time  => time at which the script began 
# BASE_URL    => just the base crowdstrike api url 
# AUTH_CREDS  => the credentials needed to authenticate w/ crowdstrike api 
# INSTANCE_ID => the ID(s) of the instances in AWS
# DEVICE_ID   => the ID(s) of the instances in Crowdstrike

start_time = time.time();
BASE_URL = "https://api.crowdstrike.com/";
AUTH_CREDS = {};
AUTH_CREDS['client_id'] = "[REMOVED]";
AUTH_CREDS['client_secret'] = "[REMOVED]";
AUTH_TOKEN = "";
INSTANCE_ID = "";
DEVICE_ID = "";

## #####################
##      Functions     ##
########################
# def getToken()           => retrieves token from Crowdstrike api and stores its value into globalvar AUTH_TOKEN
# def checkAuth()          => checks to see if the current value stored into globalvar AUTH_TOKEN is valid by attempting an API call.  If not, then call getToken()
# def getInstanceId()      => stores instance id(s) into globalvar INSTANCE_ID (this may eventually become retrieving the instance_ids from AWS Cloudtrail
# def getDeviceId()        => retrieves and stores the device id(s) of host(s) from Crowdstrike based upon the provided AWS instance id(s) into globalvar DEVICE_ID
# def getDeviceIdByLast()  => retrieves and stores the device id(s) of host(s) from Crowdstrike whose 'Last Seen' filter was over an hour from now into globalvar DEVICE_ID
# def deregister()         => remove hosts stored in globalvar DEVICE_ID from Crowdstrike GUI 'host management' section

def getToken():
        url = BASE_URL+"oauth2/token";
        headers = { 'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' };
        auth_response = requests.post(url,data=AUTH_CREDS, headers=headers);
        if auth_response.status_code != 201:
                print("\nReturn code: "+str(auth_response.status_code)+" "+auth_response.reason);
        else:
                return auth_response.json()['access_token'];

def checkAuth():
        url = BASE_URL+"devices/queries/devices/v1";
        global AUTH_TOKEN;
        headers = { 'accept': 'application/json', 'Authorization': 'bearer '+str(AUTH_TOKEN) };
        auth_response = requests.get(url, headers=headers);
        if auth_response.status_code != 200:
#               print("\nReturn code: "+str(auth_response.status_code)+" "+auth_response.reason);
                AUTH_TOKEN = getToken();
#               print("\nAUTH_TOKEN=\""+str(AUTH_TOKEN)+"\"");
        #else:
#               print("\nCurrent token is valid");

def getInstanceId():
        return "";

def getDeviceId(instance_id):
        url = BASE_URL+"devices/queries/devices/v1?filter=instance_id:'"+str(instance_id)+"'";
        headers = { 'accept': 'application/json', 'Authorization': 'bearer '+str(AUTH_TOKEN) };
        auth_response = requests.get(url, headers=headers);
        return auth_response.json()['resources'];

def getDeviceIdByLast():
        global DEVICE_ID;
        url = BASE_URL+"devices/queries/devices/v1?filter=last_seen:<'now-1h'";
        headers = { 'accept': 'application/json', 'Authorization': 'bearer '+str(AUTH_TOKEN) };
        auth_response = requests.get(url, headers=headers);
        if auth_response.json()['meta']['pagination']['total'] <= 0:
                print("There are no more hosts to be found");
                DEVICE_ID = 0;
        else:
                DEVICE_ID = auth_response.json()['resources'];
                deregister(DEVICE_ID);

def deregister(device_id):
        print("\n----------\nAttempting to remove devices:\n----------\n"+str(device_id));
        url = BASE_URL+"devices/entities/devices-actions/v2?action_name=hide_host";
        headers = { 'Content-Type': 'application/json', 'Authorization': 'bearer '+str(AUTH_TOKEN) };
        auth_response = requests.post(url,json={'ids': device_id}, headers=headers);

## #####################
##        Main        ##
########################
#checkAuth();
AUTH_TOKEN = getToken();
while DEVICE_ID != 0:
        getDeviceIdByLast();

print("\n---- Completed in "+str(time.time() - start_time)+" seconds ----\n");
