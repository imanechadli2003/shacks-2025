from app.utils.settings import settings
from app.utils.reports import reports_manager
from app.utils.tracking.generator.generate_html import generate_replay_html
from app.utils.use_discord import envoyer_message_et_obtenir_reponse, envoyer_message, envoyer_photo
from app.utils.close_computer import close_computer
from app.utils.const import TOKEN_DISCORD, GUILD_ID, PATH_PHOTO_INTRUS
from app.utils.tracking.generator.generator import generate_intrusion_report

import asyncio
import threading


async def trigger_intrusion_alert(action_type: str):
    """
    Gère l'alerte en cas d'intrusion détectée.
    """
    user_id = int(settings.get("discord_user_id", 0))
    if action_type == "Fermeture automatique":
        MESSAGE = "Un intrus est détecté. Nous avons procedé à la fermeture de l'ordinateur pour votre sécurité. VOICI UNE PHOTO DE L'INTRUS : "
        await envoyer_message(TOKEN_DISCORD, GUILD_ID, user_id, MESSAGE)
        await envoyer_photo(TOKEN_DISCORD, GUILD_ID, user_id, PATH_PHOTO_INTRUS)  # TODO
        close_computer()
        print("Ordinateur fermé.")  # Pour test uniquement, # TODO


    elif action_type == "Contre-espionnage":
        from app.utils.tracking.tracking_activity import stop_tracking, tracking

        MESSAGE = "Un intrus est détecté. Le mode espionnage est activé. Si vous souhaitez fermer l'ordinateur, répondez '1'."

        json_content = {}
        temps_espionnage = settings.get("espionnage_duration", 15)
        tracking_thread = threading.Thread(target=tracking, args=(temps_espionnage, json_content), daemon=True)
        tracking_thread.start()

        # Envoyer le message et la photo immédiatement
        await envoyer_message(TOKEN_DISCORD, GUILD_ID, user_id, MESSAGE)
        await envoyer_photo(TOKEN_DISCORD, GUILD_ID, user_id, PATH_PHOTO_INTRUS)

        try:
            reponse = await asyncio.wait_for(
                envoyer_message_et_obtenir_reponse(TOKEN_DISCORD, GUILD_ID, user_id, "En attente de votre réponse..."),
                timeout=temps_espionnage
            )
            if reponse == "1":
                stop_tracking()
                await envoyer_message(TOKEN_DISCORD, GUILD_ID, user_id, "Ordinateur en cours de fermeture...")
            elif reponse is not None:
                await envoyer_message(TOKEN_DISCORD, GUILD_ID, user_id, f"Réponse reçue mais invalide : '{reponse}'. L'ordinateur reste en espionnage.")
        except asyncio.TimeoutError:
            print("Temps d'espionnage écoulé sans réponse Discord")

        # Wait for tracking to finish
        tracking_thread.join()

        # Generate report
        pdf_path, summary_json_path = generate_intrusion_report(json_content["json_path"])
        generate_replay_html(json_content["json_path"], "rapport.html")
        
        reports_manager.add_report(pdf_path, summary_json_path)


#asyncio.run(trigger_intrusion_alert("Contre-espionnage"))