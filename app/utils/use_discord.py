import discord
import asyncio
from typing import List

async def envoyer_message_et_obtenir_reponse(token: str, guild_id: int, user_id: int, message_a_envoyer: str) -> str:
    """
    Crée un canal privé avec l'utilisateur si nécessaire, envoie un message, 
    puis attend la réponse de l'utilisateur et la retourne.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    reponse_utilisateur = {"message": None}

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await channel.send(f"<@{user_id}> {message_a_envoyer}")

    @client.event
    async def on_message(message):
        if message.channel.name != channel_name:
            return
        if message.author.id != user_id:
            return
        
        reponse_utilisateur["message"] = message.content
        await client.close()

    await client.start(token)
    return reponse_utilisateur["message"]


async def envoyer_message(token: str, guild_id: int, user_id: int, message_a_envoyer: str):
    """
    Crée un canal privé avec l'utilisateur si nécessaire et envoie un message.
    Ne lit pas les réponses.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await channel.send(f"<@{user_id}> {message_a_envoyer}")
        await client.close()

    await client.start(token)


async def envoyer_photo(token: str, guild_id: int, user_id: int, chemin_image: str):
    """
    Envoie une photo sans attendre de réponse.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        try:
            guild = client.get_guild(guild_id)
            if guild:
                channel = discord.utils.get(guild.channels, name=channel_name)
                if channel is None:
                    channel = await guild.create_text_channel(channel_name)
                await channel.send(file=discord.File(chemin_image))
        finally:
            await client.close()

    try:
        await client.start(token)
    except Exception as e:
        print(f"Erreur lors de l'envoi de la photo: {e}")


async def recuperer_usernames(token: str, guild_id: int) -> List[dict]:
    """
    Récupère la liste des utilisateurs HUMANS d'un serveur Discord, en excluant les bots.

    Remarques:
    - Nécessite l'intent Members activé côté bot (Developer Portal) et dans le code.
    - Utilise la route HTTP fetch_members pour balayer tous les membres.
    - Retourne une liste de dicts: {"id": int, "name": str} où name = member.name (username)
    """
    intents = discord.Intents.default()
    intents.members = True  # Intent privilégié requis
    client = discord.Client(intents=intents)

    result = {"users": []}

    @client.event
    async def on_ready():
        try:
            guild = client.get_guild(guild_id)
            if guild is None:
                # Guild introuvable: fermer proprement
                await client.close()
                return

            users: List[dict] = []
            try:
                # Méthode exhaustive via HTTP (asynchrone)
                async for member in guild.fetch_members(limit=None):
                    # member.name = username, member.display_name = pseudo/nickname
                    if not getattr(member, "bot", False):
                        users.append({"id": member.id, "name": member.name})
            except Exception:
                # Fallback: membres déjà en cache (peut être incomplet selon intents)
                users = [
                    {"id": m.id, "name": m.name}
                    for m in guild.members
                    if not getattr(m, "bot", False)
                ]

            result["users"] = users
        finally:
            await client.close()

    await client.start(token)
    return result["users"]