"""
Presenter pour l'onglet de capture en temps réel
Gère la logique de capture, d'analyse et de mise à jour de la vue
"""
from PySide6.QtCore import QObject, Signal, QTimer
from datetime import datetime

class CapturePresenter(QObject):
    """
    Presenter pour la capture
    Fait le lien entre LiveCaptureTab (View) et CaptureService/AnalysisService (Model)
    """
    
    # Signaux pour la communication thread-safe
    pokemon_single_detected = Signal(str, float, dict)
    pokemon_multi_detected = Signal(dict)

    def __init__(self, view, capture_service, analysis_service, pokeapi_service, type_calculator):
        super().__init__()
        self.view = view
        self.capture_service = capture_service
        self.analysis_service = analysis_service
        self.pokeapi_service = pokeapi_service
        self.type_calculator = type_calculator
        
        self.is_capturing = False
        self.capture_timer = None
        self.last_detected_pokemon = None
        self.current_pokemons_data = []
        self.manual_selection = False
        
        self._connect_signals()
        
    def _connect_signals(self):
        """Connecte les signaux de la vue et internes"""
        # Commandes utilisateur
        self.view.btn_select_region.clicked.connect(self.select_region)
        self.view.btn_save_region.clicked.connect(self.save_region)
        self.view.btn_load_region.clicked.connect(self.load_region)
        self.view.btn_toggle.clicked.connect(self.toggle_capture)
        
        # Changement de sélection dans le dropdown (mode multi)
        self.view.combo_pokemon_selector.currentIndexChanged.connect(self.on_pokemon_selection_changed)
        
        # Changement de forme
        self.view.form_selected.connect(self.on_form_selected)

        # Simple clic sur l'historique
        self.view.list_history.itemClicked.connect(self._on_history_item_clicked)

        # Connexion des signaux internes pour le threading
        self.pokemon_single_detected.connect(self.handle_single_pokemon_detection)
        self.pokemon_multi_detected.connect(self.handle_multiple_pokemon_detection)

    def on_form_selected(self, form_name, types, api_name, widget_number=1):
        """Gère le changement de forme"""
        
        # Récupère les données de la forme
        pokemon_data = self.pokeapi_service.get_pokemon_form_data(api_name)
        
        if not pokemon_data:
            self.view.show_error("Erreur", f"Impossible de charger la forme {form_name}")
            return
            
        # Utilise le helper pour la mise à jour
        self._update_pokemon_slot(widget_number - 1, pokemon_data, form_name)
        
        self.view.set_status(f"Forme changée: {form_name}", "success")
        
    def select_region(self):
        """Gère la sélection de région"""
        # Cache la fenêtre principale via la vue
        self._parent_window = self.view.window()
        if self._parent_window:
            self._parent_window.showMinimized()

        # Lance le sélecteur de région (PySide6)
        from ui.widgets.region_selector import RegionSelector
        self._region_selector = RegionSelector()
        self._region_selector.selection_confirmed.connect(self._on_region_selected)
        self._region_selector.selection_cancelled.connect(self._on_region_cancelled)
        self._region_selector.show()
        
        # Active la fenêtre et donne le focus pour capturer les événements clavier (Echap)
        self._region_selector.raise_()
        self._region_selector.activateWindow()
        self._region_selector.setFocus()

    def _on_region_selected(self, region_dict):
        """Callback quand une région est sélectionnée"""
        from core.entities import CaptureRegion
        
        # Met à jour le service
        region = CaptureRegion(
            left=region_dict['left'],
            top=region_dict['top'],
            width=region_dict['width'],
            height=region_dict['height']
        )
        self.capture_service.set_region(region)
        
        # Restaure la fenêtre
        if hasattr(self, '_parent_window') and self._parent_window:
            self._parent_window.showNormal()
            self._parent_window.raise_()
            self._parent_window.activateWindow()
            self._parent_window = None

        # Mise à jour UI
        self.view.update_region_info(region.width, region.height)
        self.view.set_status("Zone sélectionnée")
        self.view.enable_capture_controls(True)
        
        # Démarre automatiquement la capture
        self.view.show_info("Succès", "Zone sélectionnée ! Capture automatique démarrée.")
        if hasattr(self, '_parent_window') and self._parent_window:
            self._parent_window.showNormal()
            self._parent_window.raise_()
        
        # Démarre automatiquement la capture
        self.start_capture()
        
        # Nettoyage
        self._region_selector = None

    def update_language(self, lang_code):
        """Met à jour la configuration OCR selon la langue"""
        # Mise à jour des noms de Pokémon pour l'OCR
        pokemon_names = self.pokeapi_service.get_all_pokemon_names()
        self.capture_service.ocr.update_pokemon_names(pokemon_names)
        
        # Mise à jour de la config Tesseract
        if lang_code == 'ja':
            if not self.capture_service.ocr.check_language_availability('ja'):
                self.view.show_warning(
                    "Pack de langue manquant", 
                    "Le pack de langue 'Japanese' (jpn) n'est pas installé pour Tesseract.\n"
                    "L'OCR ne pourra pas lire les caractères japonais.\n\n"
                    "Veuillez installer le pack 'jpn.traineddata' dans le dossier tessdata."
                )
            
            self.capture_service.ocr.tesseract_config = self.capture_service.ocr.tesseract_config['japanese']
            print(f"[OCR] Changement langue: Japonais (mode: {self.capture_service.ocr.tesseract_config})")
        else:
            # Par défaut on utilise 'multi' pour supporter Anglais + Français
            self.capture_service.ocr.tesseract_config = self.capture_service.ocr.tesseract_config['multi']
            print(f"[OCR] Changement langue: Défaut/Multi (mode: {self.capture_service.ocr.tesseract_config})")
            
    def _on_region_cancelled(self):
        """Callback quand la sélection est annulée"""
        # Restaure la fenêtre
        if hasattr(self, '_parent_window') and self._parent_window:
            self._parent_window.showNormal()
            self._parent_window.raise_()
            self._parent_window.activateWindow()
            self._parent_window = None
            
        self.view.set_status("Sélection de région annulée")
        self._region_selector = None
            
    def save_region(self):
        """Sauvegarde la région"""
        if self.capture_service.save_region():
            self.view.show_info("Sauvegarde", "Configuration de région sauvegardée!")
            self.view.set_status("💾 Zone d'écran sauvegardée")
        else:
            self.view.show_warning("Attention", "Aucune région à sauvegarder")
            
    def load_region(self):
        """Charge la région"""
        if self.capture_service.load_region():
            region = self.capture_service.region
            self.view.update_region_info(region.width, region.height)
            self.view.set_status("✅ Zone chargée")
            self.view.enable_capture_controls(True)
            self.view.show_info("Chargement", "Configuration de région chargée!")
        else:
            self.view.show_warning("Attention", "Aucune configuration de région trouvée")
            
    def toggle_capture(self):
        """Bascule la capture"""
        if self.is_capturing:
            self.stop_capture()
        else:
            self.start_capture()
            
    def start_capture(self):
        """Démarre la capture"""
        if not self.capture_service.region:
            self.view.show_warning("Attention", "Sélectionnez d'abord une région d'écran")
            return

        # Récupère les paramètres depuis la vue
        params = self.view.get_capture_params()
        interval = params['interval']
        sensitivity = params['sensitivity']
        confidence = params['confidence']
        max_pokemon = params['max_pokemon']

        # Configure le mode de détection
        if self.capture_service.live_capture_instance:
            self.capture_service.live_capture_instance.set_max_pokemon(max_pokemon)

        # Démarre la capture
        success = self.capture_service.start_live_capture(
            interval=interval,
            callback=self._on_pokemon_detected_callback,
            sensitivity=sensitivity,
            confidence=confidence
        )

        if success:
            self.is_capturing = True
            self.view.update_capture_state(True)
            from core.translations import t

            # Avertissement si OCR non disponible
            if not self.capture_service.ocr:
                self.view.show_warning(
                    "OCR non disponible",
                    "Tesseract n'est pas installé sur cette machine.\n"
                    "La capture d'écran fonctionne mais l'analyse automatique OCR est désactivée.\n\n"
                    "Pour activer l'OCR, installez Tesseract depuis:\n"
                    "https://github.com/UB-Mannheim/tesseract/wiki"
                )
                self.view.set_status(f"🔄 {t('status_capturing')} (OCR désactivé)", "running")
            else:
                self.view.set_status(f"🔄 {t('status_capturing')}", "running")

            # Timer pour vérifier le statut
            self.capture_timer = QTimer()
            self.capture_timer.timeout.connect(self._check_capture_status)
            self.capture_timer.start(1000)
        else:
            self.view.show_error("Erreur", "Impossible de démarrer la capture")
            
    def stop_capture(self):
        """Arrête la capture"""
        self.capture_service.stop_live_capture()

        if self.capture_timer:
            self.capture_timer.stop()
            self.capture_timer = None

        self.is_capturing = False
        self.view.update_capture_state(False)
        from core.translations import t
        self.view.set_status(f"⏸️ {t('status_stopped')}")
        
    def single_capture(self):
        """Capture unique"""
        if not self.capture_service.region:
            self.view.show_warning("Attention", "Sélectionnez d'abord une région d'écran")
            return

        # Capture
        image = self.capture_service.capture_single()
        if not image:
            self.view.show_error("Erreur", "Impossible de capturer l'écran")
            return

        # Affiche l'aperçu
        self.view.display_preview(image)

        # Récupère les paramètres de capture pour savoir si on est en mode multi
        params = self.view.get_capture_params()
        max_pokemon = params['max_pokemon']

        # Analyse
        if self.capture_service.live_capture_instance:
            result = self.capture_service.live_capture_instance.analyze_capture(
                image,
                multi_pokemon=True,
                max_pokemon=max_pokemon
            )
            if result['success']:
                # Vérifie si c'est un résultat multi-Pokémon
                if 'pokemon_count' in result and result['pokemon_count'] > 1:
                    # Mode multi
                    self._on_pokemon_detected_callback(None, 0, result)
                elif 'pokemon_name' in result:
                    # Mode simple
                    self._on_pokemon_detected_callback(
                        result['pokemon_name'],
                        result['confidence'],
                        result
                    )
                else:
                    self.view.show_error("Erreur", "Aucun Pokémon détecté")
                
    def _check_capture_status(self):
        """Vérifie si la capture tourne toujours"""
        if not self.capture_service.is_capturing():
            self.stop_capture()
            
    def _on_pokemon_detected_callback(self, pokemon_name, confidence, result):
        """Callback appelé par le service de capture (thread séparé)"""
        # On émet un signal pour passer au thread principal
        
        # Gère le cas multi-pokémon
        if 'pokemon_count' in result and result['pokemon_count'] > 1:
            self.pokemon_multi_detected.emit(result)
            return

        # Cas simple
        if not pokemon_name:
            return

        self.pokemon_single_detected.emit(pokemon_name, confidence, result)

    def handle_single_pokemon_detection(self, pokemon_name, confidence, result):
        """Gère la détection d'un seul Pokémon"""
        pokemon_data = self.pokeapi_service.get_pokemon_by_name(pokemon_name)
        if not pokemon_data:
            self.view.set_status(f"Pokémon '{pokemon_name}' non trouvé dans la base", "error")
            return
        
        # Crée l'entité Pokemon
        pokemon = self._create_pokemon_from_data(pokemon_data)

        # Évite le spam
        if self.last_detected_pokemon == pokemon.name:
            return

        self.last_detected_pokemon = pokemon.name
        self.manual_selection = False

        # Utilise le helper pour la mise à jour (index 0 car single detection)
        # Reset les données courantes pour le mode single
        self.current_pokemons_data = []
        
        self.view.set_single_view()
        self._update_pokemon_slot(0, pokemon_data, image=result.get('image'))

        # Ajoute à l'historique (le timestamp sera ajouté par la vue)
        history_text = f"#{pokemon.number:03d} {pokemon.name.title()} ({confidence:.1%})"
        self.view.add_to_history(history_text)

        from core.translations import t
        self.view.set_status(f"✅ {pokemon.name.title()} {t('word_detected')} ({confidence:.1%})", "success")
        
        # Gestion des formes (logique métier)
        forms_info = self.pokeapi_service.get_pokemon_forms(pokemon.number)
        if forms_info and forms_info.get('has_forms'):
            # Force la forme actuelle comme défaut pour qu'elle soit sélectionnée
            forms_info['default_form'] = pokemon.api_name
            
            # Use species_name for correct form formatting
            species_name = forms_info.get('species_name', pokemon.api_name.split('-')[0])
            
            # Also fetch the localized species name
            species_localized_name = self.pokeapi_service._get_localized_name(pokemon.pokedex_number)

            self.view.show_form_selector(
                species_name, 
                forms_info, 
                pokemon_api_name=pokemon.api_name,
                translated_species_name=species_localized_name
            )
        else:
            self.view.hide_form_selector()

    def handle_multiple_pokemon_detection(self, result):
        """Gère la détection multiple"""
        pokemons_data = []
        
        for pkmn_info in result['pokemons']:
            pokemon_name = pkmn_info['pokemon_name']
            confidence = pkmn_info['confidence']
            
            pokemon_data = self.pokeapi_service.get_pokemon_by_name(pokemon_name)
            if not pokemon_data:
                continue
                
            pokemon = self._create_pokemon_from_data(pokemon_data)
            
            pokemons_data.append({
                'pokemon': pokemon,
                'confidence': confidence,
                'sprite_url': pokemon_data.get('sprite'),
                'pokemon_data': pokemon_data  # Store the API data
            })
            
        if not pokemons_data:
            return

        # Vérifie si changement
        new_names = set(p['pokemon'].name for p in pokemons_data)
        current_names = set()
        if self.last_detected_pokemon:
            current_names = set(self.last_detected_pokemon.split("_"))

        if new_names == current_names and self.manual_selection:
            return

        self.last_detected_pokemon = "_".join([p['pokemon'].name for p in pokemons_data])
        self.current_pokemons_data = pokemons_data
        self.manual_selection = False

        # Récupère les formes pour chaque Pokémon
        forms_per_pokemon = {}
        for pkmn_data in pokemons_data:
            pokemon = pkmn_data['pokemon']
            forms_info = self.pokeapi_service.get_pokemon_forms(pokemon.number)
            if forms_info:
                forms_per_pokemon[pokemon.number] = forms_info

        # Met à jour la vue
        image = result.get('image')
        
        self.view.set_multi_view(pokemons_data)
        
        for i, pkmn_data in enumerate(pokemons_data):
            # Update slot - pass the API data format
            self._update_pokemon_slot(i, pkmn_data['pokemon_data'], image=image if i==0 else None)
            
            # Show form selector if needed
            pokemon = pkmn_data['pokemon']
            if pokemon.number in forms_per_pokemon:
                forms_info = forms_per_pokemon[pokemon.number]
                if forms_info and forms_info.get('has_forms'):
                    # Force la forme actuelle comme défaut
                    forms_info['default_form'] = pokemon.api_name
                    
                    # Use species_name
                    species_name = forms_info.get('species_name', pokemon.api_name.split('-')[0])
                    
                    # Also fetch the localized species name
                    species_localized_name = self.pokeapi_service._get_localized_name(pokemon.pokedex_number)
                    
                    self.view.show_form_selector(
                        species_name, 
                        forms_info, 
                        widget_number=i+1, 
                        pokemon_api_name=pokemon.api_name,
                        translated_species_name=species_localized_name
                    )

        names_str = " + ".join([p['pokemon'].name.title() for p in pokemons_data])
        mode_label = f"MULTI ({len(pokemons_data)})"

        # Ajoute à l'historique avec les numéros (le timestamp sera ajouté par la vue)
        numbers_str = ", ".join([f"#{p['pokemon'].number:03d}" for p in pokemons_data])
        history_text = f"{numbers_str}: {names_str}"
        self.view.add_to_history(history_text)

        from core.translations import t
        self.view.set_status(f"✅ {t('word_battle')} {mode_label}: {names_str}", "success")

        # Affiche l'analyse du premier par défaut
        self.display_analysis_for_index(0)

    def on_pokemon_selection_changed(self, index):
        """Changement de sélection manuelle"""
        if index >= 0:
            self.manual_selection = True
            self.display_analysis_for_index(index)

    def display_analysis_for_index(self, index):
        """Affiche l'analyse pour un index donné"""
        if index >= len(self.current_pokemons_data):
            return

        pkmn_data = self.current_pokemons_data[index]
        pokemon = pkmn_data['pokemon']
        analysis = self.analysis_service.analyze_pokemon_types(pokemon)

        self.view.update_analysis_table(pokemon, analysis, self.type_calculator)

    def _on_history_item_clicked(self, item):
        """Gère le clic sur un élément de l'historique"""
        import re

        item_text = item.text()

        # Extrait les numéros de Pokémon du texte (format: [HH:MM:SS] #001 Name ou #001, #002: Name1 + Name2)
        # Pattern pour extraire tous les numéros
        numbers = re.findall(r'#(\d+)', item_text)

        if not numbers:
            self.view.set_status("Impossible d'extraire le numéro du Pokémon", "warning")
            return

        # Convertit en entiers
        pokemon_numbers = [int(num) for num in numbers]

        # Cas simple: un seul Pokémon
        if len(pokemon_numbers) == 1:
            pokemon_number = pokemon_numbers[0]

            # Récupère les données via l'API
            pokemon_data = self.pokeapi_service.get_pokemon_by_number(pokemon_number)
            if not pokemon_data:
                self.view.set_status(f"Pokémon #{pokemon_number} non trouvé", "error")
                return

            pokemon = self._create_pokemon_from_data(pokemon_data)

            # Analyse
            analysis = self.analysis_service.analyze_pokemon_types(pokemon)
            sprite_url = pokemon_data.get('sprite')

            # Met à jour les données courantes
            self.current_pokemons_data = [{
                'pokemon': pokemon,
                'confidence': 1.0,
                'sprite_url': sprite_url
            }]

            # Affiche
            self.view.set_single_view()
            self._update_pokemon_slot(0, pokemon_data)

            # Gestion des formes
            forms_info = self.pokeapi_service.get_pokemon_forms(pokemon.number)
            if forms_info and forms_info.get('has_forms'):
                # Use species_name for correct form formatting
                species_name = forms_info.get('species_name', pokemon.api_name.split('-')[0])
                species_localized_name = self.pokeapi_service._get_localized_name(pokemon.pokedex_number)
                self.view.show_form_selector(species_name, forms_info, pokemon_api_name=pokemon.api_name, translated_species_name=species_localized_name)
            else:
                self.view.hide_form_selector()

            from core.translations import t
            self.view.set_status(f"📜 {t('word_history')}: {pokemon.name.title()}", "info")

        # Cas multi: plusieurs Pokémon
        else:
            pokemons_data = []
            forms_per_pokemon = {}

            for pokemon_number in pokemon_numbers:
                pokemon_data = self.pokeapi_service.get_pokemon_by_number(pokemon_number)
                if not pokemon_data:
                    continue

                pokemon = self._create_pokemon_from_data(pokemon_data)

                pokemons_data.append({
                    'pokemon': pokemon,
                    'confidence': 1.0,
                    'sprite_url': pokemon_data.get('sprite'),
                    'pokemon_data': pokemon_data  # Store API data
                })

                # Récupère les formes
                forms_info = self.pokeapi_service.get_pokemon_forms(pokemon.number)
                if forms_info:
                    forms_per_pokemon[pokemon.number] = forms_info

            if not pokemons_data:
                self.view.set_status("Aucun Pokémon trouvé", "error")
                return

            # Affiche
            self.view.set_multi_view(pokemons_data)
            
            for i, pkmn_data in enumerate(pokemons_data):
                self._update_pokemon_slot(i, pkmn_data['pokemon_data'])
                
                # Forms
                pokemon = pkmn_data['pokemon']
                if pokemon.number in forms_per_pokemon:
                    forms_info = forms_per_pokemon[pokemon.number]
                    if forms_info and forms_info.get('has_forms'):
                         # Use species_name from forms_info as the base name for the selector
                         # This ensures "charizard-mega-x" is correctly identified as a form of "charizard"
                         species_name = forms_info.get('species_name', pokemon.api_name.split('-')[0])
                         
                         # Get localized species name
                         species_localized_name = self.pokeapi_service._get_localized_name(pokemon.pokedex_number)
                         
                         self.view.show_form_selector(species_name, forms_info, widget_number=i+1, pokemon_api_name=pokemon.api_name, translated_species_name=species_localized_name)

            # Met à jour les données courantes
            self.current_pokemons_data = pokemons_data

            # Affiche l'analyse du premier
            self.display_analysis_for_index(0)

            names_str = " + ".join([p['pokemon'].name.title() for p in pokemons_data])
            from core.translations import t
            self.view.set_status(f"📜 {t('word_history')}: {names_str}", "info")

    def _format_pokemon_info(self, pokemon, form_name=None):
        """
        Formate les informations du Pokémon pour l'affichage
        Standardise l'affichage entre la vue par défaut et la vue forme
        """
        from core.translations import translate_type
        from ui.styles import get_type_badge_html

        # En-tête avec types à côté de la génération
        types_html = []
        for t in pokemon.types:
            type_translated = translate_type(t)
            types_html.append(get_type_badge_html(t, type_translated))
        types_str = "&nbsp;".join(types_html)
        
        info_text = f"<h3>{pokemon.name.upper()} #{pokemon.number:03d} | Gen {pokemon.generation}&nbsp;&nbsp;{types_str}</h3>"

        # Forme (si spécifiée)
        if form_name:
            info_text += f"<b>Forme :</b> {form_name}<br>"

        # Taille et Poids
        if pokemon.height is not None and pokemon.weight is not None:
            # Conversion: height est en dm -> m, weight est en hg -> kg
            height_m = pokemon.height / 10.0
            weight_kg = pokemon.weight / 10.0
            # Formatage avec virgule comme séparateur décimal
            info_text += f"<b>Taille :</b> {height_m:.1f}m | <b>Poids :</b> {weight_kg:.1f}kg<br>".replace('.', ',')

        # Talents (Abilities)
        if pokemon.abilities:
            # TODO: Traduire les talents si possible via PokeAPI service
            # Pour l'instant on affiche les noms bruts (souvent en anglais ou slug)
            # On essaie de les rendre plus lisibles
            abilities_list = []
            for ability in pokemon.abilities:
                name = ability['name'].replace('-', ' ').title()
                if ability.get('is_hidden'):
                    name += " (caché)"
                abilities_list.append(name)
            
            abilities_str = ", ".join(abilities_list)
            info_text += f"<b>Talents :</b> {abilities_str}<br>"

        # Description (seulement si présente)
        if pokemon.description:
            info_text += f"<br><i>{pokemon.description}</i>"

        return info_text

    def _create_pokemon_from_data(self, pokemon_data):
        """Crée une entité Pokemon à partir des données API"""
        from core.entities import Pokemon
        return Pokemon(
            number=pokemon_data['number'],
            pokedex_number=pokemon_data.get('pokedex_number', pokemon_data['number']),
            name=pokemon_data['name'],
            api_name=pokemon_data.get('api_name', pokemon_data['name']), # Fallback safe
            types=pokemon_data['types'],
            generation=pokemon_data['generation'],
            description=pokemon_data.get('description'),
            height=pokemon_data.get('height'),
            weight=pokemon_data.get('weight'),
            abilities=pokemon_data.get('abilities', [])
        )

    def _update_pokemon_slot(self, index, pokemon_data, form_name=None, image=None):
        """
        Met à jour un slot de Pokémon (données + affichage)
        Gère la persistance des données pour le changement de langue
        """
        # 1. Création de l'entité
        pokemon = self._create_pokemon_from_data(pokemon_data)
        sprite_url = pokemon_data.get('sprite')
        
        # 2. Mise à jour des données courantes (Persistence)
        # Si l'index est hors limites (nouveau slot), on l'ajoute
        # Sinon on le met à jour
        entry = {
            'pokemon': pokemon,
            'confidence': 1.0, # Défaut, sera écrasé si existant et pertinent
            'sprite_url': sprite_url
        }
        
        if index < len(self.current_pokemons_data):
            # Garde la confiance existante si on met juste à jour (ex: forme)
            entry['confidence'] = self.current_pokemons_data[index].get('confidence', 1.0)
            self.current_pokemons_data[index] = entry
        else:
            # Cas où on ajoute (ne devrait pas arriver souvent ici, mais pour robustesse)
            # En général on reset current_pokemons_data avant pour les détections
            if index == 0 and len(self.current_pokemons_data) == 0:
                 self.current_pokemons_data.append(entry)
        
        # 3. Analyse
        analysis = self.analysis_service.analyze_pokemon_types(pokemon)
        
        # 4. Mise à jour Vue - Sélectionne le bon widget
        if index == 0:
            widget = self.view.pokemon1_widget
        elif index == 1:
            widget = self.view.pokemon2_widget
        elif index == 2:
            widget = self.view.pokemon3_widget
        else:
            return
        
        # Update sprite
        if image:
            self.view.display_preview(image)
            
        if sprite_url:
            self.view._display_sprite(sprite_url, index + 1)
        
        # Update info widget (replaces HTML)
        widget.set_pokemon(pokemon, form_name)
        
        # Image capture (si fournie)
        if image and index == 0:
             self.view.display_preview(image)

        # Tableau d'analyse
        current_combo_idx = self.view.combo_pokemon_selector.currentIndex()
        if len(self.current_pokemons_data) == 1 or current_combo_idx == index:
             self.view.update_analysis_table(pokemon, analysis, self.type_calculator)

    def refresh_current_display(self):
        """Rafraîchit l'affichage des Pokémon actuels (ex: après changement de langue)"""
        # Copie pour itérer
        current_data_copy = list(self.current_pokemons_data)
        
        for i, entry in enumerate(current_data_copy):
            if not entry or 'pokemon' not in entry:
                continue

            current_pokemon = entry['pokemon']
            api_name = current_pokemon.api_name
            
            # Re-fetch complet pour avoir les nouvelles traductions
            new_pokemon_data = self.pokeapi_service.get_pokemon_by_name(api_name)
            
            if new_pokemon_data:
                # Met à jour le slot (crée entité + UI)
                self._update_pokemon_slot(i, new_pokemon_data)

                # Crée l'objet pour avoir les propriétés accessibles facilement
                new_pokemon = self._create_pokemon_from_data(new_pokemon_data)

                # Gestion des formes (Récupère les nouvelles traductions de formes)
                forms_info = self.pokeapi_service.get_pokemon_forms(new_pokemon.number)
                if forms_info and forms_info.get('has_forms'):
                    # Force la forme actuelle comme défaut pour qu'elle soit sélectionnée
                    forms_info['default_form'] = new_pokemon.api_name
                    
                    # Use species_name for correct form formatting
                    species_name = forms_info.get('species_name', new_pokemon.api_name.split('-')[0])
                    
                    # Also fetch the localized species name (e.g. "Dracaufeu" instead of "Mega Dracaufeu X")
                    # This is crucial for the FormSelector to format names correctly
                    species_localized_name = self.pokeapi_service._get_localized_name(new_pokemon.pokedex_number)
                    
                    self.view.show_form_selector(
                        species_name, 
                        forms_info, 
                        widget_number=i+1, 
                        pokemon_api_name=new_pokemon.api_name,
                        translated_species_name=species_localized_name
                    )

        # Rafraîchit le dropdown du sélecteur de Pokémon avec les noms traduits
        if len(self.current_pokemons_data) > 1:
            self.view.refresh_pokemon_selector(self.current_pokemons_data)

        # Force la mise à jour de l'analyse (tableau de types) avec le premier Pokémon
        if self.current_pokemons_data:
             self.display_analysis_for_index(0)

        # Rafraîchit le message de statut avec les nouvelles traductions
        if self.current_pokemons_data:
            from core.translations import t
            if len(self.current_pokemons_data) == 1:
                # Cas simple : un seul Pokémon
                pokemon = self.current_pokemons_data[0]['pokemon']
                confidence = self.current_pokemons_data[0].get('confidence', 1.0)
                self.view.set_status(f"✅ {pokemon.name.title()} {t('word_detected')} ({confidence:.1%})", "success")
            else:
                # Cas multi : plusieurs Pokémon
                names_str = " + ".join([p['pokemon'].name.title() for p in self.current_pokemons_data])
                mode_label = f"MULTI ({len(self.current_pokemons_data)})"
                self.view.set_status(f"✅ {t('word_battle')} {mode_label}: {names_str}", "success")

