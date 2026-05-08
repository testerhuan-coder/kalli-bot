import os
import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput

TOKEN = os.getenv("TOKEN")
keys_validas = {
    "KALI-2020": None,
    "KALI-1234": None,
    "KALI-5689": None,
}

usuarios_ativos = {}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# MODAL RESGATAR KEY
class ResgatarKeyModal(Modal, title="Resgatar Key"):

    key = TextInput(
        label="Sua Key",
        placeholder="KALI-XXXX",
        required=True
    )

    ipv4 = TextInput(
        label="Seu IPv4",
        placeholder="Ex: 177.45.162.44",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        from datetime import datetime, timedelta

        key_digitada = self.key.value
        ip_digitado = self.ipv4.value

        usuario_id = str(interaction.user.id)

        # key existe?
        if key_digitada not in keys_validas:
            await interaction.response.send_message(
                "❌ Key inválida.",
                ephemeral=True
            )
            return

        dados_key = keys_validas[key_digitada]

        # se já foi usada por outra pessoa
        if dados_key is not None:
            dono = dados_key["usuario"]

            if dono != usuario_id:
                await interaction.response.send_message(
                    "❌ Esta key já foi resgatada por outro usuário.",
                    ephemeral=True
                )
                return

            # verifica expiração
            agora = datetime.now()

            if agora < dados_key["expira"]:
                tempo = dados_key["expira"] - agora
                horas = tempo.seconds // 3600
                minutos = (tempo.seconds % 3600) // 60

                await interaction.response.send_message(
                    f"⚠️ Sua key ainda está ativa.\n"
                    f"⏳ Tempo restante: {horas}h {minutos}m",
                    ephemeral=True
                )
                return

        # ativa por 24h
        agora = datetime.now()
        nova_expiracao = agora + timedelta(hours=24)

        # salva dono da key
        keys_validas[key_digitada] = {
            "usuario": usuario_id,
            "expira": nova_expiracao
        }

        # salva plano do usuário
        usuarios_ativos[usuario_id] = {
            "key": key_digitada,
            "ip": ip_digitado,
            "expira": nova_expiracao
        }

        await interaction.response.send_message(
            f"✅ Key ativada com sucesso!\n\n"
            f"🔑 Key: {key_digitada}\n"
            f"🌐 IPv4: {ip_digitado}\n"
            f"⏰ Expira em: {nova_expiracao}",
            ephemeral=True
        )

# PAINEL
class Painel(View):

    @discord.ui.button(
        label="Resgatar Key",
        style=discord.ButtonStyle.success
    )
    async def resgatar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            ResgatarKeyModal()
        )

    @discord.ui.button(
        label="Trocar IP",
        style=discord.ButtonStyle.primary
    )
    async def ip_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        class TrocarIPModal(Modal, title="Trocar IPv4"):

            novo_ip = TextInput(
                label="Novo IPv4",
                placeholder="Ex: 177.45.162.44",
                required=True
            )

            async def on_submit(
                self,
                interaction: discord.Interaction
            ):

                usuario_id = str(interaction.user.id)

                if usuario_id not in usuarios_ativos:

                    await interaction.response.send_message(
                        "❌ Você não possui plano ativo.",
                        ephemeral=True
                    )
                    return

                usuarios_ativos[usuario_id]["ip"] = self.novo_ip.value

                await interaction.response.send_message(
                    f"✅ IPv4 atualizado com sucesso!\n\n"
                    f"🌐 Novo IP: {self.novo_ip.value}",
                    ephemeral=True
                )

        await interaction.response.send_modal(
            TrocarIPModal()
        )

    @discord.ui.button(
        label="Meu Plano",
        style=discord.ButtonStyle.secondary
    )
    async def plano_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        from datetime import datetime

        usuario_id = str(interaction.user.id)

        if usuario_id not in usuarios_ativos:
            await interaction.response.send_message(
                "❌ Você não possui plano ativo.",
                ephemeral=True
            )
            return

        dados = usuarios_ativos[usuario_id]
        agora = datetime.now()
        expiracao = dados["expira"]

        # expirou
        if agora >= expiracao:
            del usuarios_ativos[usuario_id]
            await interaction.response.send_message(
                "❌ Seu plano expirou.",
                ephemeral=True
            )
            return

        tempo_restante = expiracao - agora
        horas = tempo_restante.seconds // 3600
        minutos = (tempo_restante.seconds % 3600) // 60

        await interaction.response.send_message(
            f"👑 Plano: PREMIUM\n\n"
            f"🔑 Key: {dados['key']}\n"
            f"🌐 IP: {dados['ip']}\n"
            f"⏳ Tempo restante: {horas}h {minutos}m",
            ephemeral=True
        )

# BOT ONLINE
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# COMANDO
@bot.command()
async def painel(ctx):

    embed = discord.Embed(
        title="KALLI",
        description=(
            "Bem-vindo ao painel de controle.\n\n"
            "• **Resgatar Key** — Ative ou renove seu plano\n"
            "• **Trocar IP** — Atualize seu IPv4\n"
            "• **Meu Plano** — Veja o status do seu acesso"
        ),
        color=0x8a2be2
    )

    embed.set_footer(text="Sistema Proxy Android")

    await ctx.send(
        embed=embed,
        view=Painel()
    )
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot online!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

keep_alive()

bot.run(TOKEN)