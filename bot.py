from restart import keep_alive
import discord
from discord.ext import commands
import asyncio
import time

keep_alive()

TOKEN = "MTQ3ODIwNTE5MDczNjcwNzY1Ng.Gu5I2v.mxgsMAxTCP9ZzFLLVdFGxT1NoVtIVqPP-_hkzo"
CATEGORIA_ID = 1479116599398105259

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# AUTO REINICIO
def bot_run():
    while True:
        try:
            bot.run("MTQ3ODIwNTE5MDczNjcwNzY1Ng.Gu5I2v.mxgsMAxTCP9ZzFLLVdFGxT1NoVtIVqPP-_hkzo")
        except Exception as e:
            print("Bot caiu:", e)
            print("Reiniciando em 5 segundos...")
            time.sleep(5)


# BOT ONLINE
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    bot.add_view(PainelTicket())
    bot.add_view(TicketControl())
    bot.add_view(AvaliacaoView())


# MODAL MOTIVO ABERTURA
class MotivoAbertura(discord.ui.Modal, title="Motivo do Ticket"):

    motivo = discord.ui.TextInput(
        label="Explique seu problema",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        categoria = guild.get_channel(1478470052431794338)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        canal = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=categoria,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket Aberto",
            description=f"""
👤 **Usuário:** {interaction.user.mention}

📝 **Motivo**
```{self.motivo}```

Aguarde atendimento da equipe.
""",
            color=discord.Color.red()
        )

        await canal.send(embed=embed, view=TicketControl())

        embed2 = discord.Embed(
            title="✅ Ticket criado",
            description="Clique abaixo para ir até o ticket.",
            color=discord.Color.red()
        )

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Ir para ticket", url=canal.jump_url))

        await interaction.response.send_message(embed=embed2, view=view, ephemeral=True)


# MODAL FECHAR
class MotivoFechar(discord.ui.Modal, title="Fechar Ticket"):

    motivo = discord.ui.TextInput(
        label="Motivo do fechamento",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):

        mensagens = []

        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            mensagens.append(f"{msg.author}: {msg.content}")

        transcript = "\n".join(mensagens)

        embed_transcript = discord.Embed(
            title="📄 Transcript do Ticket",
            description=f"```\n{transcript[:3900]}\n```",
            color=discord.Color.red()
        )

        try:
            await interaction.user.send(embed=embed_transcript, view=AvaliacaoView())
        except:
            pass

        embed = discord.Embed(
            title="🔒 Ticket Fechado",
            description=f"""
👮 **Fechado por:** {interaction.user.mention}

📝 **Motivo**
```{self.motivo}```
""",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(5)
        await interaction.channel.delete()


# MODAL AVALIAÇÃO
class MotivoAvaliacao(discord.ui.Modal, title="Avaliação do Atendimento"):

    motivo = discord.ui.TextInput(
        label="Diga o motivo da sua avaliação",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="⭐ Avaliação Recebida",
            description=f"""
👤 Usuário: {interaction.user.mention}

📝 Motivo:
```{self.motivo}```
""",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)


# BOTÕES DE AVALIAÇÃO
class AvaliacaoView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.gray, custom_id="star1")
    async def star1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MotivoAvaliacao())

    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.gray, custom_id="star2")
    async def star2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MotivoAvaliacao())

    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.gray, custom_id="star3")
    async def star3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MotivoAvaliacao())

    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.gray, custom_id="star4")
    async def star4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MotivoAvaliacao())

    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.gray, custom_id="star5")
    async def star5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MotivoAvaliacao())


# SELECT MENU
class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Suporte", description="Abrir ticket suporte", emoji="🎫"),
            discord.SelectOption(label="Alto Escalão", description="Falar com administração", emoji="👑")
        ]

        super().__init__(
            placeholder="Escolha uma opção",
            options=options,
            custom_id="ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MotivoAbertura())


class PainelTicket(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# CONTROLE DO TICKET
class TicketControl(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Assumir",
        style=discord.ButtonStyle.green,
        emoji="🛠",
        custom_id="assumir_ticket"
    )
    async def assumir(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🛠 Ticket Assumido",
            description=f"{interaction.user.mention} assumiu este ticket.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed)

    @discord.ui.button(
        label="Fechar",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="fechar_ticket"
    )
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(MotivoFechar())


# COMANDO PAINEL
@bot.command()
async def painel(ctx):

    embed = discord.Embed(
        title="🎫 RT Revolução Trabalhista",
        description="""
Nossa equipe está pronta para ajudar você.

Selecione uma opção no menu abaixo para abrir atendimento.

📩 Suporte técnico  
📩 Falar com administração  
📩 Resolver problemas
""",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed, view=PainelTicket())


keep_alive()
bot_run()
