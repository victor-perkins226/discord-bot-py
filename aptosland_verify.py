import discord, asyncio
from discord.ext import commands,tasks
from discord.commands import slash_command, permissions, Option
from discord.ui import InputText, Modal
from dotenv import load_dotenv

import pymongo
from pymongo import MongoClient
from pymongo import ReturnDocument

import datetime
from datetime import datetime
import requests
import re
import os
import pandas as pd
import numpy as np
import time
import io
import csv
import json

import discord, asyncio
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands
import datetime
import time
import discord
import logging
import discord
import pandas as pd
import pymongo
from pymongo import MongoClient
import datetime
from datetime import datetime
import io
import csv
import json
from discord.ext.commands import CommandNotFound

intents = discord.Intents.all()
intents.members = True

c = pymongo.MongoClient(" ")
db = c["ordiz-verify"]


async def reverify(bot):
    
    print("entering")
    try:

        while True:
            
          
            for guild in bot.guilds: 
                gid = str(guild.id)
                coll = db[gid]
                cursor = coll.find()
                list_cur = list(cursor)
                dff = pd.DataFrame(list_cur)
                
                try:
                    vmemid = dff['_id'].values

                    for member in guild.members:

                        memid = str(member.id)

                                                
                        if memid in vmemid:
                        
                            data=dff.loc[dff['_id'] == str(memid)]
                            r = data['roles'].values[0]
                            df_r = pd.DataFrame(r)
                            df_r=df_r.ffill(axis = 0)
                            df_r=df_r.dropna()
                            role_id =df_r.columns.values
                            status = df_r.values
                            status=status[0]
     
                            
                            
                            for i in range(len(role_id)):
                            
                                role = discord.utils.get(member.guild.roles, id= int(role_id[i]))
                                if(status[i] == True):
                                                                     
                                    await member.add_roles(role, atomic=True)
                                    await asyncio.sleep(5)
                                    print("auto role assigned :",member,role)                           

                                else: 
                                  
                                    await member.remove_roles(role, atomic=True)
                                    await asyncio.sleep(5)
                                    print("auto role removed :",member,role)
                                        
                except Exception as ex:
                    print(ex)
                    print("error in " , gid)

                    
                await asyncio.sleep(50)    

            await asyncio.sleep(15000)

    except Exception as ex:
        print(ex)
        print("error in auto role")
        await asyncio.sleep(50)  
        pass
        
        

async def check_status(interaction):

    try:
  
        gid=str(interaction.guild.id)  
        col = db[gid]     
        cursor = col.find({ "_id": str(interaction.user.id)})   
        data=cursor[0]         
        r = data['roles']
        df_r = pd.DataFrame(r)
        df_r=df_r.ffill(axis = 0)
        df_r=df_r.dropna()
        role_id =df_r.columns.values
        status = df_r.values
        status=status[0]

        for i in range(len(role_id)):
        
            role = discord.utils.get(interaction.guild.roles,id= int(role_id[i]))
            try:
                if(status[i] == True):
                    await interaction.user.add_roles(role, atomic=True) 
                else:
                    await interaction.user.remove_roles(role, atomic=True) 
                sts = "Roles updated"                       
            except:           
                sts ="Missing permissions"
    except:    
        sts ="Wallet not connected"
                 
    return sts
        
                
class PersistentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Connect wallet", style=discord.ButtonStyle.green,custom_id="verify")
    async def button_callback(self, button, interaction):
    
        await interaction.response.defer(ephemeral = True)
    
        #url ="https://discord.com/api/oauth2/authorize?client_id=103336293490630667&redirect_uri=https%3A%2F%2Fconnect.aptosland.io&response_type=token&scope=identify&state="+str(interaction.guild.id)
        url ="https://discord.com/api/oauth2/authorize?client_id=103336293490630667&redirect_uri=https%3A%2F%2Faptosland-3eff6.web.app&response_type=token&scope=identify&state="+str(interaction.guild.id)
        await interaction.followup.send(url,ephemeral = True)

    @discord.ui.button(label="Check status", style=discord.ButtonStyle.blurple,custom_id="check status")
    async def second_button_callback(self, button, interaction):
        await interaction.response.defer(ephemeral = True)
        status = await check_status(interaction)
        embed = discord.Embed( color= 0x2ecc71,description=status) 
        await interaction.followup.send(embed=embed,ephemeral = True)

     
        
class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">",intents=intents,sync_commands = True)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:

            self.add_view(PersistentView())
            self.persistent_views_added = True
            
        

        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        await bot.change_presence(activity=discord.Game(name="https://aptosland.io"))
        await reverify(bot)


bot = PersistentViewBot()


@bot.slash_command(description="Set verification channel")
@discord.default_permissions(administrator=True)
async def setup_verification(ctx : commands.Context,channel : Option(discord.TextChannel, "Choose verification channel")):


    await ctx.defer(ephemeral=True)
    
    embed=discord.Embed(title="Verify your assets",description="Click on `Connect wallet` below to verify your NFT holdings in "+str(ctx.guild.name)+" server"+"\n\n*This is a read - only connection. Do not share your private keys. We will never ask for your seed phrase.* \n\nPowered by https://twitter.com/AptoslandNFT",color= 0xeeffee )
    embed.set_author(name="ORDIZ Verification", icon_url=bot.user.avatar.url)
    embed.set_thumbnail(url=ctx.guild.icon.url)    
    await channel.send(embed=embed,view = PersistentView() )  
    embed = discord.Embed(description="verification pannel sent", color=discord.Color.random())     
    await ctx.send_followup(embed=embed,ephemeral = True) 
    
    
      
@bot.event
async def on_raw_reaction_add(payload):
    
    try:
         
        guild = bot.get_guild(payload.guild_id) # Get guild    
        gid=str(payload.guild_id)    
        col = db[gid]
        
        #bot_config
        config= db["bot_config"]
        cursor = config.find({"guild_id": gid})   
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        cid = df['channel_id'].values [0]
        emj = df['emoji'].values [0]
        

        
        member = get(guild.members, id=payload.user_id) 
      
        if payload.channel_id == int(cid): 
            if str(payload.emoji) == emj: 
                
                     
                try:        
                

                    cursor = col.find({ "_id": str(payload.member.id)})   
                    
                    data=cursor[0]         
                    r = data['roles']
                    df_r = pd.DataFrame(r)
                    df_r=df_r.ffill(axis = 0)
                    df_r=df_r.dropna()
                    role_id =df_r.columns.values
                    status = df_r.values
                    status=status[0]

                    
                    
                    for i in range(len(role_id)):
                    
                        if(status[i] == True):
                        
                            role = get(payload.member.guild.roles, id= int(role_id[i])) 
                            await payload.member.add_roles(role)
                            print("react role assigned :",member,role)  
 
                            
                        else:
                        
                            role = get(payload.member.guild.roles, id= int(role_id[i])) 
                            await payload.member.remove_roles(role)
                            print("react role removed :",member,role) 
                         
                except Exception as ex:
                    print(ex)
                                
   
    
    except Exception as ex:
        print(ex)    
    
    
    

    
    
    
    
    
    
    
    
    
    

bot.run("")



        
