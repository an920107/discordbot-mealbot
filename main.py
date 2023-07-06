import discord
from discord.ext import commands
import json
import modules.utils

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="!")

mu = modules.utils.MealUtils()
emojis: list = json.load(open("emojis.json", "r", encoding="utf-8"))

@bot.event
async def on_ready():
    print("On ready.")


@bot.command()
async def ping(ctx: commands.context.Context, *args: str):
    if (len(args) > 0):
        await ctx.send("Usage: `!ping`")
    else:
        await ctx.send(f"{bot.latency * 1000:.0f} (ms)")


@bot.command()
async def member(ctx: commands.context.Context, *args: str):
    if len(args) == 0:
        await ctx.send("Usage: `!member <add | remove | query | list> [args]`")
    else:
        if args[0] == "add":
            if len(args) == 4:
                try:
                    mu.members_add(int(args[1]), args[2], args[3])
                    await ctx.send(f"<@{args[1]}> has been added to {args[3]} as {args[2]}.")
                except ValueError:
                    await ctx.send("`<id>` should be an integer.")
                except:
                    await ctx.send(f"<@{args[1]}> is already exist.")
            else:
                await ctx.send("Usage: `!member add <id> <name> <group>`")
        elif args[0] == "remove":
            if len(args) == 2:
                try:
                    mu.members_remove(int(args[1]))
                    await ctx.send(f"<@{args[1]}> has been removed.")
                except ValueError:
                    await ctx.send("`<id>` should be an integer.")
                except:
                    await ctx.send(f"<@{args[1]}> is not exist.")
            else:
                await ctx.send("Usage: `!member remove <id>`")
        elif args[0] == "query":
            if len(args) == 2:
                try:
                    await ctx.send(f"{mu.member_query(int(args[1]))}")
                except ValueError:
                    await ctx.send("`<id>` should be an integer.")
                except:
                    await ctx.send(f"<@{args[1]}> is not exist.")
            else:
                await ctx.send("Usage: `!member query <id>`")
        elif args[0] == "list":
            if len(args) == 1:
                await ctx.send(f"{mu.members_list()}")
            else:
                await ctx.send("Usage: `!member list`")


@bot.command()
async def meal(ctx: commands.context.Context, *args: str):
    if len(args) == 0:
        await ctx.send("Usage: `!meal <create | discount | store | add | delete | query | list> [args]`")
    else:
        if args[0] == "create":
            if len(args) == 2:
                try:
                    mu.meal_create(args[1])
                    await ctx.send(f"Meal `{args[1]}` has been created.")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is already exist.")
            else:
                await ctx.send("Usage: `!meal create <title>`")
        elif args[0] == "list":
            if len(args) == 1:
                await ctx.send(f"{mu.meal_list()}")
            else:
                await ctx.send("Usage: `!meal list`")
        elif args[0] == "store":
            if len(args) == 2:
                try:
                    await ctx.send(f"{mu.meal_store(args[1])}")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            elif len(args) == 3:
                try:
                    mu.meal_store(args[1], args[2])
                    await ctx.send(f"Store of `{args[1]}` has been changed to `{args[2]}`.")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal store <title> [name]`")

        elif args[0] == "discount":
            if len(args) == 2:
                try:
                    await ctx.send(f"{mu.meal_discount(args[1])}")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            elif len(args) == 3:
                try:
                    mu.meal_discount(args[1], int(args[2]))
                    await ctx.send(f"Discount of `{args[1]}` has been changed to `{args[2]}`.")
                except ValueError:
                    await ctx.send("`<value>` should be an integer.")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal discount <title> [value]`")
        elif args[0] == "add":
            if len(args) == 4:
                try:
                    mu.meal_add(args[1], args[2], int(args[3]))
                    await ctx.send(f"Item `{args[2]}` with price `{args[3]}` has been added to `{args[1]}`.")
                except ValueError:
                    await ctx.send("`<price>` should be an integer.")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not found or item `{args[2]}` is already exist.")
            else:
                await ctx.send("Usage: `!meal add <title> <item> <price>`")
        elif args[0] == "query":
            if len(args) == 2:
                try:
                    await ctx.send(f"{mu.meal_query(args[1])}")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal query <title>`")
        elif args[0] == "delete":
            if len(args) == 3:
                try:
                    mu.meal_delete(args[1], args[2])
                    await ctx.send(f"`{args[2]}` has been deleted from `{args[1]}`.")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not found or item `{args[2]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal delete <title> <item>`")
        elif args[0] == "order":
            if len(args) == 2:
                items = mu.meal_query(args[1])
                for i in range(len(items)):
                    items[i].insert(0, emojis[i])
                msg = await ctx.send(
                    f"`{args[1]}` `{mu.meal_store(args[1])}` `本日補助：{mu.meal_discount(args[1])}`\n```\n" +
                    "\n".join(map(lambda x: f"{x[0]} {x[2]:3s} {x[1]}", items)) + "\n```")
                mu.lastest_msg_id(msg.id)
                mu.lastest_meal_title(args[1])
                for i in range(len(items)):
                    await msg.add_reaction(emojis[i])
            else:
                await ctx.send("Usage: `!meal order <title>`")


@bot.event
async def on_reaction_add(reaction: discord.reaction.Reaction, user: discord.member.Member):
    msg = reaction.message
    if user.bot or (msg.id != mu.lastest_msg_id()):
        return
    try:
        title = mu.lastest_meal_title()
        items = mu.meal_query(title)
        index = emojis.index(reaction.emoji)
        mu.order_update(title, user.id, items[index][0])
        await msg.channel.send(f"<@{user.id}> has ordered `{items[index][0]}`.")
    except Exception as e:
        print(e.with_traceback())
    

@bot.command()
async def test(ctx: commands.context.Context, *args: str):
    await ctx.message.add_reaction("❤️")


with open("token", "r") as token_file:
    token = token_file.readline()

bot.run(token)
