import discord
from discord.ext import commands
import json
import modules.utils

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="!")

mu = modules.utils.MealUtils()
emojis: list = json.load(open("emojis.json", "r", encoding="utf-8"))
cancel_emoji = "❌"


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
                    mu.member_add(int(args[1]), args[2], args[3])
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
                    mu.member_remove(int(args[1]))
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
                await ctx.send(f"{mu.member_list()}")
            else:
                await ctx.send("Usage: `!member list`")


@bot.command()
async def meal(ctx: commands.context.Context, *args: str):
    if len(args) == 0:
        await ctx.send("Usage: `!meal <create | discount | store | add | delete | query | list | notify> [args]`")
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
                try:
                    items = mu.meal_query(args[1])
                    for i in range(len(items)):
                        items[i].insert(0, emojis[i])
                    items.append([cancel_emoji, "取消", "-"])
                    await ctx.send(
                        f"@everyone\n`{args[1]}` `{mu.meal_store(args[1])}` `本日補助：{mu.meal_discount(args[1])}`")
                    msgs: list[discord.message.Message] = []
                    for i in range(len(items) // 20 + 1):
                        msgs.append(await ctx.send(
                            "```\n" + "\n".join(map(lambda x: f"{x[0]} {x[2]:3s} {x[1]}", items[i * 20: i * 20 + 20])) + "\n```"))
                    msg_ids = list(map(lambda x: x.id, msgs))
                    mu.lastest_msg_id(msg_ids)
                    mu.lastest_meal_title(args[1])
                    for i in range(len(items) - 1):
                        await msgs[i // 20].add_reaction(emojis[i])
                    i += 1
                    await msgs[i // 20].add_reaction(cancel_emoji)
                except Exception as e:
                    await ctx.send(e)
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal order <title>`")
        elif args[0] == "notify":
            if len(args) == 2:
                try:
                    to_notify = []
                    records = mu.meal_state(args[1])
                    for record in records:
                        if record[1] == "":
                            to_notify.append(
                                f"<@{mu.member_search(record[0])[0]}>")
                    await ctx.send(f"{' '.join(to_notify)} 還沒點餐喔！")
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal notify <title>`")
        elif args[0] == "state":
            if len(args) == 2:
                try:
                    await ctx.send(str(mu.meal_state(args[1])))
                except:
                    await ctx.send(f"Meal title `{args[1]}` is not exist.")
            else:
                await ctx.send("Usage: `!meal state <title>`")


@bot.event
async def on_reaction_add(reaction: discord.reaction.Reaction, user: discord.member.Member):
    msg = reaction.message
    if user.bot or (msg.id not in mu.lastest_msg_id()):
        return
    if user.bot:
        return
    try:
        title = mu.lastest_meal_title()
        if reaction.emoji == cancel_emoji:
            mu.order_update(title, user.id, "")
            await msg.channel.send(f"<@{user.id}>'s order has been canceled.")
        else:
            items = mu.meal_query(title)
            index = emojis.index(reaction.emoji)
            mu.order_update(title, user.id, items[index][0])
            await msg.channel.send(f"<@{user.id}> has ordered `{items[index][0]}`.")
    except:
        await msg.channel.send(f"<@{user.id}> has added the reaction '{reaction.emoji}'. However '{reaction.emoji}' isn't the order option.")


@bot.command()
async def test(ctx: commands.context.Context, *args: str):
    await ctx.message.add_reaction("❤️")


with open("token", "r") as token_file:
    token = token_file.readline()

bot.run(token)
