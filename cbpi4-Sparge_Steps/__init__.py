import asyncio
import aiohttp
from aiohttp import web
from cbpi.api import parameters, Property, action
from cbpi.api.step import StepResult, CBPiStep
from cbpi.api.timer import Timer
from datetime import datetime
import time
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.api.dataclasses import Kettle, Props
from cbpi.api import *
import logging
from socket import timeout
from typing import KeysView
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import numpy as np
import requests
import warnings


@parameters([Property.Number(label="Temp", configurable=True),
             Property.Actor(label="Actor"),
             Property.Kettle(label="Kettle")])

class TempStep(CBPiStep):

    @action("Stop heating", [])
    async def stop_heating(self):
        self.kettle=self.get_kettle(self.props.get("Kettle", None))
        self.Actor=self.props.get("Actor", None)
        self.kettle.target_temp = int(0)
        await self.setAutoMode(False)
        await self.actor_off(self.Actor)
        self.cbpi.notify(self.name, 'Sparge Heating stopped', NotificationType.INFO)
        await self.push_update()

    async def on_timer_done(self, timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self, timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(1, on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.timer.start()

        self.port = str(self.cbpi.static_config.get('port',8000))

        self.kettle=self.get_kettle(self.props.get("Kettle", None))
        if self.kettle is not None:
            self.kettle.target_temp = int(self.props.get("Temp", 0))
        else:
            logging.error("Error, no kettle {}".format(e))

        self.Actor=self.props.get("Actor", None)
        if self.Actor is not None and self.kettle.target_temp == int(0):
            await self.actor_off(self.Actor)

        if self.kettle.target_temp == int(0):
            await self.setAutoMode(False)
            await self.actor_off(self.props.Actor)
        else:
            await self.setAutoMode(True)

        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def reset(self):
        self.timer = Timer(1, on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
        return StepResult.DONE

    async def setAutoMode(self, auto_state):
        try:
            if (self.kettle.instance is None or self.kettle.instance.state == False) and (auto_state is True):
                await self.cbpi.kettle.toggle(self.kettle.id)
            elif (self.kettle.instance.state == True) and (auto_state is False):
                await self.cbpi.kettle.stop(self.kettle.id)
            await self.push_update()

        except Exception as e:
            logging.error("Failed to switch on KettleLogic {} {}".format(self.kettle.id, e))





@parameters([Property.Actor(label="Sparge-Heater"),
             Property.Kettle(label="Sparge-Kettle")])

class SpargeStep(CBPiStep):

    async def SpargeStep(self, **kwargs):
        self.summary = "Sparging"
        if self.kettle is not None:
            self.kettle.target_temp = int(0)
            await self.setAutoMode(False)

        if self.actor is not None:
            await self.actor_off(self.actor)

        await self.push_update()

        self.cbpi.notify(self.name, "Sparging in progress. When done, press Next to start boil.", NotificationType.INFO, action=[NotificationAction("Next step", self.NextStep)])
        await self.push_update()

    async def NextStep(self, **kwargs):
        await self.next()

    async def on_timer_done(self,timer):
        self.summary = "Take malt out and click Sparge"

        self.cbpi.notify(self.name, "Mashing done. Take malt out and click Begin Sparging. (System will stop Sparge heater and will ask when you are done)", NotificationType.INFO, action=[NotificationAction("Begin Sparging", self.SpargeStep)])
        await self.push_update()

    async def on_timer_update(self,timer, seconds):
        await self.push_update()

    async def on_start(self):
        self.summary=""

        self.kettle=self.get_kettle(self.props.get("Sparge-Kettle", None))
        self.actor=self.props.get("Sparge-Heater", None)

        if self.timer is None:
            self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            if self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True

        return StepResult.DONE

    async def setAutoMode(self, auto_state):
        try:
            if (self.kettle.instance is None or self.kettle.instance.state == False) and (auto_state is True):
                await self.cbpi.kettle.toggle(self.kettle.id)
            elif (self.kettle.instance.state == True) and (auto_state is False):
                await self.cbpi.kettle.stop(self.kettle.id)
            await self.push_update()

        except Exception as e:
            logging.error("Failed to switch on KettleLogic {} {}".format(self.kettle.id, e))



def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''    
    
    cbpi.plugin.register("TempStep", TempStep)
    cbpi.plugin.register("SpargeStep", SpargeStep)
   
    
    

    
