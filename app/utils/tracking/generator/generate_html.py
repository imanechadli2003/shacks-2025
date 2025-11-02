import json
import os

def generate_replay_html(input_json_path, output_html_path):
    """
    Génère un fichier HTML autonome avec les données JSON injectées.
    
    CORRIGÉ : 
    1. Syntaxe JavaScript nettoyée (suppression des '{{{{' et '}}}}' superflus).
    2. Utilisation de la syntaxe f-string correcte ${{variable}} pour les variables JavaScript.
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            json_data_string = f.read()
        
        # Le template HTML (basé sur votre fichier)
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Replay d'Activité d'Intrusion</title>
    <!-- Chargement de Tailwind CSS pour le style -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Utilisation d'une police de caractères propre */
        body {{
            font-family: 'Inter', sans-serif;
        }}
        /* Style pour le mode sombre */
        html.dark {{
            color-scheme: dark;
        }}
        /* Correction pour la prévisualisation des images en mode sombre */
        img {{
            filter: invert(0);
        }}
    </style>
    <!-- Importation de la police Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-900 text-gray-100 p-4 md:p-8">

    <div class="max-w-7xl mx-auto">
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-center text-blue-400">Replay d'Activité</h1>
            <p class="text-center text-gray-400 mt-2">Rapport d'activité généré automatiquement.</p>
        </header>

        <!-- Section pour les messages d'état -->
        <div id="statusMessage" class="bg-gray-800 border-l-4 border-blue-500 text-blue-100 p-4 rounded-md shadow-lg mb-8 max-w-2xl mx-auto" role="alert">
            <p class="font-bold">Chargement du rapport...</p>
        </div>

        <!-- Conteneur principal du Replay (caché par défaut) -->
        <div id="replayContainer" class="hidden">
            <!-- Contrôles de navigation -->
            <div class="bg-gray-800 p-4 rounded-lg shadow-lg mb-6 flex justify-between items-center">
                <button id="prevButton" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed">
                    &lt; Précédent
                </button>
                <div class="text-center">
                    <div class="text-lg font-semibold" id="stepIndicator">Étape 0 / 0</div>
                    <div class="text-sm text-gray-400" id="stepTimestamp">--:--:--</div>
                </div>
                <button id="nextButton" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed">
                    Suivant &gt;
                </button>
            </div>

            <!-- Grille pour l'image et les événements -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Colonne de la capture d'écran -->
                <div class="lg:col-span-2 bg-gray-800 p-4 rounded-lg shadow-lg">
                    <h2 class="text-xl font-semibold mb-3" id="screenshotWindowTitle">Titre de la fenêtre</h2>
                    <div class="bg-black rounded-md overflow-hidden border border-gray-700">
                        <img id="screenshotImage" src="https://placehold.co/1920x1080/000000/333333?text=Chargement..." alt="Capture d'écran" class="w-full h-auto object-contain" 
                             onerror="this.src='https://placehold.co/1920x1080/000000/FF0000?text=Image+introuvable'; this.alt='Impossible de charger l\'image. Vérifiez que le dossier tracking est accessible.'">
                    </div>
                </div>

                <!-- Colonne des événements liés -->
                <div class="lg:col-span-1 bg-gray-800 p-4 rounded-lg shadow-lg h-fit lg:max-h-[70vh] overflow-y-auto">
                    <h2 class="text-xl font-semibold mb-3">Événements pour cette étape :</h2>
                    <div id="relatedEventsContainer" class="space-y-4">
                        <!-- Les événements seront insérés ici -->
                        <p class="text-gray-400">Aucun événement associé à cette étape.</p>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        // *** DONNÉES INJECTÉES PAR PYTHON ***
        // La chaîne JSON est insérée ici directement.
        const embeddedJsonData = {json_data_string};
        // *** FIN DES DONNÉES INJECTÉES ***

        // Attente que le DOM soit chargé
        document.addEventListener('DOMContentLoaded', () => {{ 
            const statusMessage = document.getElementById('statusMessage');
            const replayContainer = document.getElementById('replayContainer');
            const prevButton = document.getElementById('prevButton');
            const nextButton = document.getElementById('nextButton');
            const stepIndicator = document.getElementById('stepIndicator');
            const stepTimestamp = document.getElementById('stepTimestamp');
            const screenshotWindowTitle = document.getElementById('screenshotWindowTitle');
            const screenshotImage = document.getElementById('screenshotImage');
            const relatedEventsContainer = document.getElementById('relatedEventsContainer');

            let allEvents = [];
            let screenshotSteps = [];
            let currentStepIndex = 0;

            prevButton.addEventListener('click', showPrevStep);
            nextButton.addEventListener('click', showNextStep);

            /**
             * Nouvelle fonction pour charger les données injectées
             */
            function loadEmbeddedData() {{ 
                statusMessage.innerHTML = `<p class="font-bold text-yellow-300">Traitement des données...</p>`;
                try {{ 
                    // CORRIGÉ: Pas besoin de JSON.parse, les données sont déjà un objet JavaScript
                    allEvents = embeddedJsonData; 
                    if (!Array.isArray(allEvents)) throw new Error('Les données injectées ne sont pas un tableau.');
                    
                    allEvents.sort((a, b) => a.timestamp - b.timestamp);
                    processEvents();
                    
                    if (screenshotSteps.length > 0) {{ 
                        currentStepIndex = 0;
                        renderCurrentStep();
                        replayContainer.classList.remove('hidden');
                        statusMessage.innerHTML = `<p class="font-bold text-green-400">Rapport chargé.</p><p>${{allEvents.length}} événements trouvés, regroupés en ${{screenshotSteps.length}} étapes.</p>`;
                    }} else {{
                        throw new Error('Aucun événement de type "screenshot" trouvé pour créer les étapes.');
                    }}

                }} catch (error) {{ 
                    console.error('Erreur lors du chargement des données injectées:', error);
                    statusMessage.innerHTML = `<p class="font-bold text-red-500">Erreur de chargement.</p><p>${{error.message}}</p>`;
                    console.log("Données brutes injectées:", embeddedJsonData);
                }}
            }} 

            /**
             * Traite les événements triés pour créer les étapes basées sur les screenshots.
             */
            function processEvents() {{ 
                screenshotSteps = [];
                let relatedEventsBuffer = [];
                
                for (const event of allEvents) {{ 
                    if (event.type === 'screenshot') {{ 
                        screenshotSteps.push({{ 
                            screenshotEvent: event,
                            relatedEvents: [...relatedEventsBuffer]
                        }}); 
                        relatedEventsBuffer = []; // Vide le buffer pour la prochaine étape
                    }} else {{
                        relatedEventsBuffer.push(event);
                    }}
                }} 
            }} 

            /**
             * Affiche l'étape actuelle (image + événements liés).
             */
            function renderCurrentStep() {{ 
                if (screenshotSteps.length === 0) return;

                const step = screenshotSteps[currentStepIndex];
                
                stepIndicator.textContent = `Étape ${{currentStepIndex + 1}} / ${{screenshotSteps.length}}`;
                stepTimestamp.textContent = new Date(step.screenshotEvent.timestamp * 1000).toLocaleString('fr-FR', {{
                    hour: '2-digit', minute: '2-digit', second: '2-digit'
                }}); 

                screenshotImage.src = escapeHTML(step.screenshotEvent.file_path);
                screenshotImage.alt = `Capture d'écran - ${{escapeHTML(step.screenshotEvent.file_path)}}`;
                screenshotWindowTitle.textContent = escapeHTML(step.screenshotEvent.window_title || 'Fenêtre inconnue');

                relatedEventsContainer.innerHTML = '';
                if (step.relatedEvents.length > 0) {{ 
                    step.relatedEvents.forEach(event => {{ 
                        const {{ cardHtml }} = getEventCardDetails(event);
                        if (cardHtml) {{
                            relatedEventsContainer.innerHTML += cardHtml;
                        }}
                    }}); 
                }} else {{
                    relatedEventsContainer.innerHTML = '<p class="text-gray-400 p-4 text-center">Aucun autre événement enregistré pour cette étape.</p>';
                }}

                prevButton.disabled = (currentStepIndex === 0);
                nextButton.disabled = (currentStepIndex === screenshotSteps.length - 1);
            }} 

            /**
             * Fonctions de navigation
             */
            function showPrevStep() {{ 
                if (currentStepIndex > 0) {{
                    currentStepIndex--;
                    renderCurrentStep();
                }}
            }} 

            function showNextStep() {{ 
                if (currentStepIndex < screenshotSteps.length - 1) {{
                    currentStepIndex++;
                    renderCurrentStep();
                }}
            }} 

            /**
             * Génère le HTML pour la carte d'un événement (version compacte pour la barre latérale).
             */
            function getEventCardDetails(event) {{ 
                const timestamp = new Date(event.timestamp * 1000).toLocaleString('fr-FR', {{
                    hour: '2-digit', minute: '2-digit', second: '2-digit'
                }}); 
                
                let icon = '';
                let title = 'Événement inconnu';
                let details = `<pre class="bg-gray-900 p-2 rounded text-xs">${{escapeHTML(JSON.stringify(event, null, 2))}}</pre>`;
                let cardColor = 'gray';

                switch (event.type) {{ 
                    case 'keystroke':
                        icon = getIcon('keyboard');
                        title = 'Frappe clavier';
                        let keyDisplay = escapeHTML(event.key).replace(/'/g, '');
                        if (keyDisplay.startsWith('Key.')) keyDisplay = `[${{keyDisplay.split('.')[1]}}]`;
                        details = `<span class="font-mono bg-gray-700 px-2 py-1 rounded text-yellow-300">${{keyDisplay}}</span>`;
                        cardColor = 'yellow';
                        break;
                    case 'mouse_click':
                        icon = getIcon('mouse');
                        title = 'Clic de souris';
                        details = `<p><strong>${{escapeHTML(event.button)}}</strong> sur (${{event.x}}, ${{event.y}})</p>`;
                        cardColor = 'blue';
                        break;
                    case 'window_change':
                        icon = getIcon('window');
                        title = 'Fenêtre active';
                        details = `<p class="font-semibold text-blue-300">${{escapeHTML(event.title)}}</p>`;
                        cardColor = 'cyan';
                        break;
                    case 'clipboard_copy':
                        icon = getIcon('clipboard');
                        title = 'Presse-papiers';
                        details = `<pre class="bg-gray-700 p-2 rounded text-xs whitespace-pre-wrap max-h-20 overflow-auto">${{escapeHTML(event.content)}}</pre>`;
                        cardColor = 'green';
                        break;
                    case 'process_start':
                        icon = getIcon('process');
                        title = 'Nouveau processus';
                        details = `<p><strong>${{escapeHTML(event.name)}}</strong> (PID: ${{event.pid}})</p>`;
                        cardColor = 'red';
                        break;
                    default:
                        icon = '';
                        title = event.type;
                        break;
                }} 

                const colors = {{ 
                    gray: 'border-gray-600',
                    yellow: 'border-yellow-500',
                    blue: 'border-blue-500',
                    cyan: 'border-cyan-500',
                    purple: 'border-purple-500',
                    green: 'border-green-500',
                    red: 'border-red-500'
                }}; 

                const cardHtml = `
                    <div class="flex items-start p-3 bg-gray-700 rounded-lg shadow-md border-l-4 ${{colors[cardColor]}}">
                        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center mr-3">
                            ${{icon}}
                        </div>
                        <div class="flex-grow min-w-0">
                            <div class="flex justify-between items-center">
                                <h3 class="text-sm font-semibold truncate">${{title}}</h3>
                                <span class="text-xs text-gray-400 font-mono flex-shrink-0 ml-2">${{timestamp}}</span>
                            </div>
                            <div class="mt-1 text-gray-300 text-xs break-words">
                                ${{details}}
                            </div>
                        </div>
                    </div>
                `;

                return {{ cardHtml }}; 
            }} 

            /**
             * Renvoie une chaîne SVG pour une icône donnée (taille réduite).
             */
            function getIcon(type) {{ 
                const icons = {{ 
                    keyboard: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v1.5a1.5 1.5 0 001.5 1.5h3a1.5 1.5 0 001.5-1.5v-1.5A2.25 2.25 0 0015.75 4h-1.5A2.25 2.25 0 0012 6.253zM15 9.75a1.5 1.5 0 011.5 1.5v1.5a1.5 1.5 0 01-1.5 1.5h-3a1.5 1.5 0 01-1.5-1.5v-1.5a1.5 1.5 0 011.5-1.5h3zM13.5 15.75a1.5 1.5 0 00-1.5-1.5h-3a1.5 1.5 0 00-1.5 1.5v1.5a1.5 1.5 0 001.5 1.5h3a1.5 1.5 0 001.5-1.5v-1.5zM9 9.75a1.5 1.5 0 011.5 1.5v1.5a1.5 1.5 0 01-1.5 1.5h-3a1.5 1.5 0 01-1.5-1.5v-1.5a1.5 1.5 0 011.5-1.5h3z" /><path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25c.621 0 1.125-.504 1.125-1.125V5.625c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v12.75c0 .621.504 1.125 1.125 1.125z" /></svg>',
                    mouse: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.042 21.672L13.684 16.6m0 0l-2.51-2.223M13.684 16.6l4.997-2.651M13.684 16.6L9.316 19.991m3.27-3.39l-4.032.911M11.22 13.2l-2.51 2.223m0-2.223l-3.27 3.39M3 3l3.59 3.59m0 0l-3.27 3.39m3.27-3.39l2.51 2.223M3 3l3.59 3.59m0 0l2.51 2.223M3 3l3.59 3.59m0 0l3.27 3.39m0 0l-2.51-2.223m0 0l-4.032.911m0 0l-2.51 2.223m0 0l3.27-3.39M3 3l3.59 3.59" /></svg>',
                    window: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17.25v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM9.75 9.75v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM9.75 17.25v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM15 17.25v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM15 9.75v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM15 17.25v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75zM9.75 9.75v-1.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75v1.5a.75.75 0 00.75.75h3a.75.75 0 00.75-.75z" /><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h19.5M2.25 7.5h19.5" /></svg>',
                    camera: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.174C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.174 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.04l-.821 1.316z" /><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" /></svg>',
                    clipboard: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>',
                    process: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3v-6a3 3 0 013-3h13.5a3 3 0 013 3v6a3 3 0 01-3 3m-13.5 0v-3.375c0-.621.504-1.125 1.125-1.125h11.25c.621 0 1.125.504 1.125 1.125V14.25" /><path stroke-linecap="round" stroke-linejoin="round" d="M9 13.5l3 3m0 0l3-3m-3 3v-6" /></svg>'
                }}; 
                return icons[type] || '<svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 13a3 3 0 100-6 3 3 0 000 6z" /><path stroke-linecap="round" stroke-linejoin="round" d="M10 3v1m0 16v1m-6-8h-1m18 0h-1M5.636 5.636l-.707-.707m12.728 12.728l-.707-.707M5.636 18.364l-.707.707m12.728-12.728l-.707.707" /></svg>';
            }} 

            /**
             * Échappe les caractères HTML pour un affichage sécurisé.
             */
            function escapeHTML(str) {{ 
                if (typeof str !== 'string') {{
                    str = String(str);
                }}
                return str.replace(/&/g, '&amp;')
                          .replace(/</g, '&lt;')
                          .replace(/>/g, '&gt;')
                          .replace(/"/g, '&quot;')
                          .replace(/'/g, '&#039;');
            }} 

            // Démarrer le chargement des données injectées
            loadEmbeddedData();

        }}); 
    </script>
</body>
</html>
        """
        
        # Écrire le contenu HTML dans le fichier de sortie
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    except Exception as e:
        print(f"Erreur fatale lors de la génération du HTML : {e}")

# --- FIN DE LA FONCTION ---

# Section de test pour exécuter ce script directement
if __name__ == "__main__":
    import os
    print("Test de generate_replay_html...")
    
    # Créer un faux fichier JSON pour le test
    fake_json_path = "test_log.json"
    fake_html_path = "test_report.html"
    
    # CORRECTION: Utilisation de simples accolades {} pour les dictionnaires Python
    fake_data = [
        {
            "type": "window_change", 
            "title": "Fenêtre de Test", 
            "timestamp": 1678886400
        },
        {
            "type": "keystroke", 
            "key": "'t'", 
            "timestamp": 1678886401
        },
        {
            "type": "keystroke", 
            "key": "'e'", 
            "timestamp": 1678886401.5
        },
        {
            "type": "keystroke", 
            "key": "'s'", 
            "timestamp": 1678886401.7
        },
        {
            "type": "keystroke", 
            "key": "'t'", 
            "timestamp": 1678886401.9
        },
        {
            "type": "screenshot", 
            "file_path": "https://placehold.co/600x400/333333/999999?text=Test+Image+1", 
            "window_title": "Fenêtre de Test", 
            "timestamp": 1678886402
        },
        {
            "type": "process_start", 
            "name": "cmd.exe", 
            "pid": 1234, 
            "timestamp": 1678886403
        },
        {
            "type": "clipboard_copy", 
            "content": "motdepasse123", 
            "timestamp": 1678886404
        },
        {
            "type": "screenshot", 
            "file_path": "https://placehold.co/600x400/555555/EEEEEE?text=Test+Image+2", 
            "window_title": "C:\\WINDOWS\\system32\\cmd.exe", 
            "timestamp": 1678886405
        }
    ]
    with open(fake_json_path, 'w', encoding='utf-8') as f:
        json.dump(fake_data, f)
        
    try:
        # Assurer que le nom de la fonction est correct (sans underscore)
        generate_replay_html(fake_json_path, fake_html_path)
        print(f"Test réussi : {fake_html_path} créé.")
        print(f"Ouvrez {os.path.abspath(fake_html_path)} dans votre navigateur pour tester.")
        os.remove(fake_json_path) # Nettoyer le JSON
    except Exception as e:
        print(f"Échec du test : {e}")