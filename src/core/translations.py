"""
Module de traduction pour l'interface utilisateur
Gère les traductions pour FR, EN, DE, ES, IT, JP
"""
import json
import os
import sys
from pathlib import Path

# Import de la fonction utilitaire pour les chemins
try:
    from core.utils import get_resource_path
except ImportError:
    # Fallback si l'import échoue
    def get_resource_path(relative_path):
        try:
            base_path = Path(sys._MEIPASS)
        except AttributeError:
            base_path = Path(__file__).parent.parent
        return base_path / relative_path

class TranslationManager:
    """Gestionnaire de traductions pour l'application"""
    
    # Dictionnaire principal de traductions
    TRANSLATIONS = {
        'fr': {
            # Application
            'app_title': 'Analyseur Pokémon',
            
            # Tabs
            'tab_capture': 'Capture Live',
            'tab_search': 'Recherche',
            
            # Live Capture Tab
            'capture_title': 'Capture en Temps Réel',
            'btn_select_region': 'Sélectionner Zone',
            'btn_save_region': 'Sauvegarder Configuration',
            'btn_load_region': 'Charger Configuration',
            'btn_start_capture': 'Démarrer',
            'btn_stop_capture': 'Arrêter',
            'btn_single_capture': 'Capture Unique',
            'label_region': 'Zone d\'écran',
            'label_region_not_selected': 'Aucune zone sélectionnée',
            'label_interval': 'Intervalle (s)',
            'label_sensitivity': 'Sensibilité',
            'label_confidence': 'Confiance Min.',
            'label_max_pokemon': 'Max Pokémon',
            'label_preview': 'Aperçu',
            'label_history': 'Historique',
            'label_form': 'Forme',
            
            # GroupBox titles
            'group_controls': 'Contrôles',
            'group_analysis': 'Analyse des Types',
            'group_preview': 'Aperçu',
            'group_history': 'Historique',
            'group_pokemon': 'Pokémon(s)',
            'group_search': 'Recherche par nom',
            'group_filters': 'Filtres',
            'group_results': 'Résultats',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'Nombre de Pokémon:',
            'label_interval_full': 'Intervalle (s):',
            'label_confidence_full': 'Confiance:',
            'label_consecutive': 'Consécutives:',
            
            # Battle modes
            'battle_solo': 'Solo (1)',
            'battle_duo': 'Duo (2)',
            'battle_trio': 'Trio (3)',
            
            # Analysis table headers
            'header_weaknesses': 'Faiblesses',
            'header_resistances': 'Résistances',
            'header_immunities': 'Immunités',
            'header_vulnerabilities': 'Super efficace',
            'label_analyze': 'Analyser:',
            
            # Preview/Capture
            'no_capture': 'Aucune capture',
            'save_short': 'Sauv.',
            'load_short': 'Charger',
            
            # Search Tab
            'search_title': 'Recherche de Pokémon',
            'search_placeholder': 'Rechercher un Pokémon...',
            'btn_search': 'Rechercher',
            'btn_clear': 'Effacer',
            'label_filters': 'Filtres',
            'label_type': 'Type',
            'label_generation': 'Génération',
            'filter_all_types': 'Tous les types',
            'filter_all_generations': 'Toutes les générations',
            
            # Analysis Table
            'analysis_title': 'Analyse des Types',
            'analysis_type': 'Type',
            'analysis_multiplier': 'Multiplicateur',
            
            # Status Messages
            'status_ready': 'Prêt',
            'status_capturing': 'Capture en cours...',
            'status_stopped': 'Capture arrêtée',
            'status_region_selected': 'Zone sélectionnée',
            'status_pokemon_detected': 'Pokémon détecté',
            'status_error': 'Erreur',
            'status_language_changed': 'Langue changée',
            'word_detected': 'détecté',
            'word_battle': 'Combat',
            'word_history': 'Historique',
            
            # Messages
            'msg_no_region': 'Sélectionnez d\'abord une région d\'écran',
            'msg_region_saved': 'Configuration de région sauvegardée!',
            'msg_region_loaded': 'Configuration de région chargée!',
            'msg_no_config': 'Aucune configuration de région trouvée',
            'msg_capture_started': 'Capture automatique démarrée',
            'msg_no_pokemon': 'Aucun Pokémon détecté',
            'msg_pokemon_not_found': 'Pokémon non trouvé dans la base',
            
            # Pokemon Info
            'info_number': 'N°',
            'info_generation': 'Génération',
            'info_type': 'Type',
            'info_form': 'Forme',

            # Pokemon Details Dialog
            'label_talents': 'Talents',
            'label_description': 'Description',
            'label_hidden': '(Caché)',
            'label_height': 'Taille',
            'label_weight': 'Poids',
            'btn_close': 'Fermer',
            'tooltip_click_details': 'Cliquer pour voir les détails',
        },
        
        'en': {
            # Application
            'app_title': 'Pokémon Analyzer',
            
            # Tabs
            'tab_capture': 'Live Capture',
            'tab_search': 'Search',
            
            # Live Capture Tab
            'capture_title': 'Real-Time Capture',
            'btn_select_region': 'Select Region',
            'btn_save_region': 'Save Configuration',
            'btn_load_region': 'Load Configuration',
            'btn_start_capture': 'Start',
            'btn_stop_capture': 'Stop',
            'btn_single_capture': 'Single Capture',
            'label_region': 'Screen Region',
            'label_region_not_selected': 'No region selected',
            'label_interval': 'Interval (s)',
            'label_sensitivity': 'Sensitivity',
            'label_confidence': 'Min. Confidence',
            'label_max_pokemon': 'Max Pokémon',
            'label_preview': 'Preview',
            'label_history': 'History',
            'label_form': 'Form',
            
            # GroupBox titles
            'group_controls': 'Controls',
            'group_analysis': 'Type Analysis',
            'group_preview': 'Preview',
            'group_history': 'History',
            'group_pokemon': 'Pokémon(s)',
            'group_search': 'Search by name',
            'group_filters': 'Filters',
            'group_results': 'Results',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'Pokémon Count:',
            'label_interval_full': 'Interval (s):',
            'label_confidence_full': 'Confidence:',
            'label_consecutive': 'Consecutive:',
            
            # Battle modes
            'battle_solo': 'Solo (1)',
            'battle_duo': 'Duo (2)',
            'battle_trio': 'Trio (3)',
            
            # Analysis table headers
            'header_weaknesses': 'Weaknesses',
            'header_resistances': 'Resistances',
            'header_immunities': 'Immunities',
            'header_vulnerabilities': 'Super effective',
            'label_analyze': 'Analyze:',
            
            # Preview/Capture
            'no_capture': 'No capture',
            'save_short': 'Save',
            'load_short': 'Load',
            
            # Search Tab
            'search_title': 'Pokémon Search',
            'search_placeholder': 'Search for a Pokémon...',
            'btn_search': 'Search',
            'btn_clear': 'Clear',
            'label_filters': 'Filters',
            'label_type': 'Type',
            'label_generation': 'Generation',
            'filter_all_types': 'All types',
            'filter_all_generations': 'All generations',
            
            # Analysis Table
            'analysis_title': 'Type Analysis',
            'analysis_type': 'Type',
            'analysis_multiplier': 'Multiplier',
            
            # Status Messages
            'status_ready': 'Ready',
            'status_capturing': 'Capturing...',
            'status_stopped': 'Capture stopped',
            'status_region_selected': 'Region selected',
            'status_pokemon_detected': 'Pokémon detected',
            'status_error': 'Error',
            'status_language_changed': 'Language changed',
            'word_detected': 'detected',
            'word_battle': 'Battle',
            'word_history': 'History',
            
            # Messages
            'msg_no_region': 'Please select a screen region first',
            'msg_region_saved': 'Region configuration saved!',
            'msg_region_loaded': 'Region configuration loaded!',
            'msg_no_config': 'No region configuration found',
            'msg_capture_started': 'Automatic capture started',
            'msg_no_pokemon': 'No Pokémon detected',
            'msg_pokemon_not_found': 'Pokémon not found in database',
            
            # Pokemon Info
            'info_number': 'No.',
            'info_generation': 'Generation',
            'info_type': 'Type',
            'info_form': 'Form',

            # Pokemon Details Dialog
            'label_talents': 'Abilities',
            'label_description': 'Description',
            'label_hidden': '(Hidden)',
            'label_height': 'Height',
            'label_weight': 'Weight',
            'btn_close': 'Close',
            'tooltip_click_details': 'Click to see details',
        },

        'de': {
            # Application
            'app_title': 'Pokémon-Analysator',
            
            # Tabs
            'tab_capture': 'Live-Aufnahme',
            'tab_search': 'Suche',
            
            # Live Capture Tab
            'capture_title': 'Echtzeit-Aufnahme',
            'btn_select_region': 'Region wählen',
            'btn_save_region': 'Konfiguration speichern',
            'btn_load_region': 'Konfiguration laden',
            'btn_start_capture': 'Starten',
            'btn_stop_capture': 'Stoppen',
            'btn_single_capture': 'Einzelaufnahme',
            'label_region': 'Bildschirmbereich',
            'label_region_not_selected': 'Keine Region ausgewählt',
            'label_interval': 'Intervall (s)',
            'label_sensitivity': 'Empfindlichkeit',
            'label_confidence': 'Min. Vertrauen',
            'label_max_pokemon': 'Max Pokémon',
            'label_preview': 'Vorschau',
            'label_history': 'Verlauf',
            'label_form': 'Form',
            
            # GroupBox titles
            'group_controls': 'Steuerung',
            'group_analysis': 'Typ-Analyse',
            'group_preview': 'Vorschau',
            'group_history': 'Verlauf',
            'group_pokemon': 'Pokémon',
            'group_search': 'Suche nach Name',
            'group_filters': 'Filter',
            'group_results': 'Ergebnisse',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'Pokémon-Anzahl:',
            'label_interval_full': 'Intervall (s):',
            'label_confidence_full': 'Vertrauen:',
            'label_consecutive': 'Aufeinanderfolgend:',
            
            # Battle modes
            'battle_solo': 'Solo (1)',
            'battle_duo': 'Duo (2)',
            'battle_trio': 'Trio (3)',
            
            # Analysis table headers
            'header_weaknesses': 'Schwächen',
            'header_resistances': 'Widerstände',
            'header_immunities': 'Immunitäten',
            'header_vulnerabilities': 'Sehr effektiv',
            'label_analyze': 'Analysieren:',
            
            # Preview/Capture
            'no_capture': 'Keine Aufnahme',
            'save_short': 'Speichern',
            'load_short': 'Laden',
            
            # Search Tab
            'search_title': 'Pokémon-Suche',
            'search_placeholder': 'Pokémon suchen...',
            'btn_search': 'Suchen',
            'btn_clear': 'Löschen',
            'label_filters': 'Filter',
            'label_type': 'Typ',
            'label_generation': 'Generation',
            'filter_all_types': 'Alle Typen',
            'filter_all_generations': 'Alle Generationen',
            
            # Analysis Table
            'analysis_title': 'Typ-Analyse',
            'analysis_type': 'Typ',
            'analysis_multiplier': 'Multiplikator',
            
            # Status Messages
            'status_ready': 'Bereit',
            'status_capturing': 'Aufnahme läuft...',
            'status_stopped': 'Aufnahme gestoppt',
            'status_region_selected': 'Region ausgewählt',
            'status_pokemon_detected': 'Pokémon erkannt',
            'status_error': 'Fehler',
            'status_language_changed': 'Sprache geändert',
            'word_detected': 'erkannt',
            'word_battle': 'Kampf',
            'word_history': 'Verlauf',
            
            # Messages
            'msg_no_region': 'Bitte wählen Sie zuerst einen Bildschirmbereich',
            'msg_region_saved': 'Regionskonfiguration gespeichert!',
            'msg_region_loaded': 'Regionskonfiguration geladen!',
            'msg_no_config': 'Keine Regionskonfiguration gefunden',
            'msg_capture_started': 'Automatische Aufnahme gestartet',
            'msg_no_pokemon': 'Kein Pokémon erkannt',
            'msg_pokemon_not_found': 'Pokémon nicht in der Datenbank gefunden',
            
            # Pokemon Info
            'info_number': 'Nr.',
            'info_generation': 'Generation',
            'info_type': 'Typ',
            'info_form': 'Form',

            # Pokemon Details Dialog
            'label_talents': 'Fähigkeiten',
            'label_description': 'Beschreibung',
            'label_hidden': '(Versteckt)',
            'label_height': 'Größe',
            'label_weight': 'Gewicht',
            'btn_close': 'Schließen',
            'tooltip_click_details': 'Klicken Sie, um Details anzuzeigen',
        },

        'es': {
            # Application
            'app_title': 'Analizador Pokémon',
            
            # Tabs
            'tab_capture': 'Captura en Vivo',
            'tab_search': 'Búsqueda',
            
            # Live Capture Tab
            'capture_title': 'Captura en Tiempo Real',
            'btn_select_region': 'Seleccionar Región',
            'btn_save_region': 'Guardar Configuración',
            'btn_load_region': 'Cargar Configuración',
            'btn_start_capture': 'Iniciar',
            'btn_stop_capture': 'Detener',
            'btn_single_capture': 'Captura Única',
            'label_region': 'Región de Pantalla',
            'label_region_not_selected': 'No hay región seleccionada',
            'label_interval': 'Intervalo (s)',
            'label_sensitivity': 'Sensibilidad',
            'label_confidence': 'Confianza Mín.',
            'label_max_pokemon': 'Máx. Pokémon',
            'label_preview': 'Vista Previa',
            'label_history': 'Historial',
            'label_form': 'Forma',
            
            # GroupBox titles
            'group_controls': 'Controles',
            'group_analysis': 'Análisis de Tipos',
            'group_preview': 'Vista Previa',
            'group_history': 'Historial',
            'group_pokemon': 'Pokémon',
            'group_search': 'Buscar por nombre',
            'group_filters': 'Filtros',
            'group_results': 'Resultados',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'Cantidad de Pokémon:',
            'label_interval_full': 'Intervalo (s):',
            'label_confidence_full': 'Confianza:',
            'label_consecutive': 'Consecutivas:',
            
            # Battle modes
            'battle_solo': 'Solo (1)',
            'battle_duo': 'Dúo (2)',
            'battle_trio': 'Trío (3)',
            
            # Analysis table headers
            'header_weaknesses': 'Debilidades',
            'header_resistances': 'Resistencias',
            'header_immunities': 'Inmunidades',
            'header_vulnerabilities': 'Super eficaz',
            'label_analyze': 'Analizar:',
            
            # Preview/Capture
            'no_capture': 'Sin captura',
            'save_short': 'Guardar',
            'load_short': 'Cargar',
            
            # Search Tab
            'search_title': 'Búsqueda de Pokémon',
            'search_placeholder': 'Buscar un Pokémon...',
            'btn_search': 'Buscar',
            'btn_clear': 'Limpiar',
            'label_filters': 'Filtros',
            'label_type': 'Tipo',
            'label_generation': 'Generación',
            'filter_all_types': 'Todos los tipos',
            'filter_all_generations': 'Todas las generaciones',
            
            # Analysis Table
            'analysis_title': 'Análisis de Tipos',
            'analysis_type': 'Tipo',
            'analysis_multiplier': 'Multiplicador',
            
            # Status Messages
            'status_ready': 'Listo',
            'status_capturing': 'Capturando...',
            'status_stopped': 'Captura detenida',
            'status_region_selected': 'Región seleccionada',
            'status_pokemon_detected': 'Pokémon detectado',
            'status_error': 'Error',
            'status_language_changed': 'Idioma cambiado',
            'word_detected': 'detectado',
            'word_battle': 'Combate',
            'word_history': 'Historial',
            
            # Messages
            'msg_no_region': 'Primero selecciona una región de pantalla',
            'msg_region_saved': '¡Configuración de región guardada!',
            'msg_region_loaded': '¡Configuración de región cargada!',
            'msg_no_config': 'No se encontró configuración de región',
            'msg_capture_started': 'Captura automática iniciada',
            'msg_no_pokemon': 'No se detectó ningún Pokémon',
            'msg_pokemon_not_found': 'Pokémon no encontrado en la base de datos',
            
            # Pokemon Info
            'info_number': 'N°',
            'info_generation': 'Generación',
            'info_type': 'Tipo',
            'info_form': 'Forma',

            # Pokemon Details Dialog
            'label_talents': 'Habilidades',
            'label_description': 'Descripción',
            'label_hidden': '(Oculto)',
            'label_height': 'Altura',
            'label_weight': 'Peso',
            'btn_close': 'Cerrar',
            'tooltip_click_details': 'Haz clic para ver los detalles',
        },

        'it': {
            # Application
            'app_title': 'Analizzatore Pokémon',
            
            # Tabs
            'tab_capture': 'Cattura Live',
            'tab_search': 'Ricerca',
            
            # Live Capture Tab
            'capture_title': 'Cattura in Tempo Reale',
            'btn_select_region': 'Seleziona Regione',
            'btn_save_region': 'Salva Configurazione',
            'btn_load_region': 'Carica Configurazione',
            'btn_start_capture': 'Avvia',
            'btn_stop_capture': 'Ferma',
            'btn_single_capture': 'Cattura Singola',
            'label_region': 'Regione Schermo',
            'label_region_not_selected': 'Nessuna regione selezionata',
            'label_interval': 'Intervallo (s)',
            'label_sensitivity': 'Sensibilità',
            'label_confidence': 'Confidenza Min.',
            'label_max_pokemon': 'Max Pokémon',
            'label_preview': 'Anteprima',
            'label_history': 'Cronologia',
            'label_form': 'Forma',
            
            # GroupBox titles
            'group_controls': 'Controlli',
            'group_analysis': 'Analisi dei Tipi',
            'group_preview': 'Anteprima',
            'group_history': 'Cronologia',
            'group_pokemon': 'Pokémon',
            'group_search': 'Cerca per nome',
            'group_filters': 'Filtri',
            'group_results': 'Risultati',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'Numero di Pokémon:',
            'label_interval_full': 'Intervallo (s):',
            'label_confidence_full': 'Confidenza:',
            'label_consecutive': 'Consecutive:',
            
            # Battle modes
            'battle_solo': 'Singolo (1)',
            'battle_duo': 'Duo (2)',
            'battle_trio': 'Trio (3)',
            
            # Analysis table headers
            'header_weaknesses': 'Debolezze',
            'header_resistances': 'Resistenze',
            'header_immunities': 'Immunità',
            'header_vulnerabilities': 'Super efficace',
            'label_analyze': 'Analizza:',
            
            # Preview/Capture
            'no_capture': 'Nessuna cattura',
            'save_short': 'Salva',
            'load_short': 'Carica',
            
            # Search Tab
            'search_title': 'Ricerca Pokémon',
            'search_placeholder': 'Cerca un Pokémon...',
            'btn_search': 'Cerca',
            'btn_clear': 'Cancella',
            'label_filters': 'Filtri',
            'label_type': 'Tipo',
            'label_generation': 'Generazione',
            'filter_all_types': 'Tutti i tipi',
            'filter_all_generations': 'Tutte le generazioni',
            
            # Analysis Table
            'analysis_title': 'Analisi dei Tipi',
            'analysis_type': 'Tipo',
            'analysis_multiplier': 'Moltiplicatore',
            
            # Status Messages
            'status_ready': 'Pronto',
            'status_capturing': 'Catturando...',
            'status_stopped': 'Cattura fermata',
            'status_region_selected': 'Regione selezionata',
            'status_pokemon_detected': 'Pokémon rilevato',
            'status_error': 'Errore',
            'status_language_changed': 'Lingua cambiata',
            'word_detected': 'rilevato',
            'word_battle': 'Battaglia',
            'word_history': 'Cronologia',
            
            # Messages
            'msg_no_region': 'Seleziona prima una regione dello schermo',
            'msg_region_saved': 'Configurazione della regione salvata!',
            'msg_region_loaded': 'Configurazione della regione caricata!',
            'msg_no_config': 'Nessuna configurazione di regione trovata',
            'msg_capture_started': 'Cattura automatica avviata',
            'msg_no_pokemon': 'Nessun Pokémon rilevato',
            'msg_pokemon_not_found': 'Pokémon non trovato nel database',
            
            # Pokemon Info
            'info_number': 'N°',
            'info_generation': 'Generazione',
            'info_type': 'Tipo',
            'info_form': 'Forma',

            # Pokemon Details Dialog
            'label_talents': 'Abilità',
            'label_description': 'Descrizione',
            'label_hidden': '(Nascosta)',
            'label_height': 'Altezza',
            'label_weight': 'Peso',
            'btn_close': 'Chiudi',
            'tooltip_click_details': 'Clicca per vedere i dettagli',
        },

        'jp': {
            # Application
            'app_title': 'ポケモンアナライザー',
            
            # Tabs
            'tab_capture': 'ライブキャプチャ',
            'tab_search': '検索',
            
            # Live Capture Tab
            'capture_title': 'リアルタイムキャプチャ',
            'btn_select_region': '領域を選択',
            'btn_save_region': '設定を保存',
            'btn_load_region': '設定を読み込む',
            'btn_start_capture': '開始',
            'btn_stop_capture': '停止',
            'btn_single_capture': '単一キャプチャ',
            'label_region': '画面領域',
            'label_region_not_selected': '領域が選択されていません',
            'label_interval': '間隔（秒）',
            'label_sensitivity': '感度',
            'label_confidence': '最小信頼度',
            'label_max_pokemon': '最大ポケモン数',
            'label_preview': 'プレビュー',
            'label_history': '履歴',
            'label_form': 'フォーム',
            
            # GroupBox titles
            'group_controls': 'コントロール',
            'group_analysis': 'タイプ分析',
            'group_preview': 'プレビュー',
            'group_history': '履歴',
            'group_pokemon': 'ポケモン',
            'group_search': '名前で検索',
            'group_filters': 'フィルター',
            'group_results': '結果',
            
            # Parameter labels (detailed)
            'label_pokemon_count': 'ポケモン数:',
            'label_interval_full': '間隔（秒）:',
            'label_confidence_full': '信頼度:',
            'label_consecutive': '連続:',
            
            # Battle modes
            'battle_solo': 'ソロ (1)',
            'battle_duo': 'デュオ (2)',
            'battle_trio': 'トリオ (3)',
            
            # Analysis table headers
            'header_weaknesses': '弱点',
            'header_resistances': '耐性',
            'header_immunities': '無効',
            'header_vulnerabilities': 'こうかばつぐん',
            'label_analyze': '分析:',
            
            # Preview/Capture
            'no_capture': 'キャプチャなし',
            'save_short': '保存',
            'load_short': '読み込み',
            
            # Search Tab
            'search_title': 'ポケモン検索',
            'search_placeholder': 'ポケモンを検索...',
            'btn_search': '検索',
            'btn_clear': 'クリア',
            'label_filters': 'フィルター',
            'label_type': 'タイプ',
            'label_generation': '世代',
            'filter_all_types': 'すべてのタイプ',
            'filter_all_generations': 'すべての世代',
            
            # Analysis Table
            'analysis_title': 'タイプ分析',
            'analysis_type': 'タイプ',
            'analysis_multiplier': '倍率',
            
            # Status Messages
            'status_ready': '準備完了',
            'status_capturing': 'キャプチャ中...',
            'status_stopped': 'キャプチャ停止',
            'status_region_selected': '領域が選択されました',
            'status_pokemon_detected': 'ポケモンを検出',
            'status_error': 'エラー',
            'status_language_changed': '言語が変更されました',
            'word_detected': '検出',
            'word_battle': 'バトル',
            'word_history': '履歴',
            
            # Messages
            'msg_no_region': 'まず画面領域を選択してください',
            'msg_region_saved': '領域設定を保存しました！',
            'msg_region_loaded': '領域設定を読み込みました！',
            'msg_no_config': '領域設定が見つかりません',
            'msg_capture_started': '自動キャプチャを開始しました',
            'msg_no_pokemon': 'ポケモンが検出されませんでした',
            'msg_pokemon_not_found': 'ポケモンがデータベースに見つかりません',
            
            # Pokemon Info
            'info_number': '番号',
            'info_generation': '世代',
            'info_type': 'タイプ',
            'info_form': 'フォーム',

            # Pokemon Details Dialog
            'label_talents': 'とくせい',
            'label_description': 'せつめい',
            'label_hidden': '(かくされた)',
            'label_height': 'たかさ',
            'label_weight': 'おもさ',
            'btn_close': 'とじる',
            'tooltip_click_details': 'クリックして詳細を表示',
        }
    }
    
    # Instance singleton
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_language = 'fr'
            cls._instance._type_translations = cls._load_type_translations()
        return cls._instance

    @staticmethod
    def _load_type_translations():
        """Charge les traductions de types depuis le fichier JSON"""
        try:
            # Utilise get_resource_path pour fonctionner en dev et avec PyInstaller
            json_path = get_resource_path('infrastructure/api/type_translations.json')

            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de type_translations.json: {e}")
            return {}
    
    def set_language(self, language_code: str):
        """
        Change la langue courante
        
        Args:
            language_code: Code de langue ('fr', 'en', 'de', 'es', 'it', 'jp')
        """
        if language_code in self.TRANSLATIONS:
            self._current_language = language_code
    
    def get_current_language(self) -> str:
        """Retourne le code de la langue courante"""
        return self._current_language
    
    def t(self, key: str, default: str = None) -> str:
        """
        Récupère une traduction pour la clé donnée

        Args:
            key: Clé de traduction
            default: Valeur par défaut si la traduction n'existe pas

        Returns:
            Texte traduit ou valeur par défaut
        """
        lang_dict = self.TRANSLATIONS.get(self._current_language, {})
        return lang_dict.get(key, default or key)

    def translate_type(self, type_name: str) -> str:
        """
        Traduit un nom de type Pokémon dans la langue courante

        Args:
            type_name: Nom du type en anglais (ex: 'fire', 'water', etc.)

        Returns:
            Nom du type traduit ou nom original si non trouvé
        """
        # Conversion du type en minuscules pour la recherche
        type_key = type_name.lower()

        # Récupération des traductions pour ce type
        type_data = self._type_translations.get(type_key, {})

        # Mapping des codes de langue
        lang_map = {
            'fr': 'fr',
            'en': 'en',
            'de': 'de',
            'es': 'es',
            'it': 'it',
            'jp': 'jp'
        }

        # Récupération de la traduction dans la langue courante
        lang_key = lang_map.get(self._current_language, 'en')
        translated = type_data.get(lang_key, type_name)

        return translated


    def format_form_name(self, pokemon_name: str, form_name: str, translated_pokemon_name: str = None) -> str:
        """
        Formate le nom d'une forme de manière lisible (ex: 'mega-x' -> 'Méga-X')
        Prend en compte la langue actuelle.
        
        Args:
            pokemon_name: Nom API du Pokémon (ex: 'charizard') ou Nom affiché
            form_name: Nom API de la forme (ex: 'charizard-mega-x')
            translated_pokemon_name: Nom traduit du Pokémon (ex: 'Dracaufeu'). Si None, utilise pokemon_name.
            
        Returns:
            Nom formaté
        """
        # Normalisation pour comparaison
        p_name = pokemon_name.lower()
        f_name = form_name.lower()

        # Si c'est la forme de base (nom identique), retourner "Normal" ou similaire
        if f_name == p_name:
            if self._current_language == 'jp' or self._current_language == 'ja':
                 return "もと"
            return "Base"

        display_name = translated_pokemon_name if translated_pokemon_name else pokemon_name.title()

        # Extrait la partie spécifique de la forme
        # ex: 'charizard-mega-x' -> 'mega-x'
        if f_name.startswith(p_name + "-"):
            specific_part = f_name[len(p_name) + 1:]
        else:
            specific_part = f_name
            
        # Si specific_part est vide (cas rare), on retourne Normal
        if not specific_part:
            return "Normal"

        # Dictionnaire de traduction des termes de forme
        form_terms = {
            'fr': {
                'mega': 'Méga',
                'gmax': 'Gigamax',
                'alola': 'd\'Alola',
                'galar': 'de Galar',
                'hisui': 'de Hisui',
                'paldea': 'de Paldea',
                'shiny': 'Chromatique',
                'female': 'Femelle',
                'male': 'Mâle',
                'plant': 'Plante',
                'sandy': 'Sable',
                'trash': 'Déchet',
                'attack': 'Attaque',
                'defense': 'Défense',
                'speed': 'Vitesse',
                'origin': 'Originelle',
                'altered': 'Alternative',
                'incarnate': 'Avatar',
                'therian': 'Totémique',
                'average': 'Moyenne',
                'small': 'Petite',
                'large': 'Grande',
                'super': 'Super',
                'white': 'Blanc',
                'black': 'Noir',
                'sun': 'Solaire',
                'moon': 'Lunaire',
                'ultra': 'Ultra',
                'dusk': 'Crépusculaire',
                'dawn': 'Aurore',
                'roaming': 'Vagabond',
                'crowned': 'Couronné',
                'hero': 'Héros',
                'single': 'Poing Final',
                'rapid': 'Mille Poings',
                'low': 'Basse',
                'key': 'Clé',
            },
            'en': {
                'mega': 'Mega',
                'gmax': 'Gigamax',
                'alola': 'Alolan',
                'galar': 'Galarian',
                'hisui': 'Hisuian',
                'paldea': 'Paldean',
                'altered': 'Altered',
                'origin': 'Origin',
                'incarnate': 'Incarnate',
                'therian': 'Therian',
            },
            'jp': {
                'mega': 'メガ',
                'gmax': 'キョダイマックス', # Kyodaimax
                'altered': 'アナザー',
                'origin': 'オリジン',
                'incarnate': 'けしん',
                'therian': 'れいじゅう',
            }
        }
        
        lang = self._current_language
        terms = form_terms.get(lang, form_terms['en'])
        
        # Sépare les morceaux (ex: 'mega-x' -> ['mega', 'x'])
        parts = specific_part.split('-')
        formatted_parts = []
        
        for part in parts:
            # Traduit si connu, sinon met en majuscule
            translated = terms.get(part.lower(), part.upper() if len(part) <= 2 else part.title())
            formatted_parts.append(translated)
        
        # Logique spécifique : Méga nom suffixe
        if parts[0] in ['mega', 'primal']:
            prefix = formatted_parts[0]
            suffix = " ".join(formatted_parts[1:])
            
            if lang == 'fr':
                return f"{prefix} {display_name} {suffix}".strip()
            elif lang == 'jp':
                 return f"{prefix} {display_name} {suffix}".strip() # Ajuster spacing pour JP si besoin
            else:
                return f"{prefix} {display_name} {suffix}".strip()
                
        # Logique spécifique : Gigamax
        if parts[0] == 'gmax':
            prefix = formatted_parts[0]
            if lang == 'fr':
                return f"{display_name} {prefix}" # Dracaufeu Gigamax ? Ou Gigamax Dracaufeu ? Souvent Gigamax Dracaufeu dans les jeux ?
                # Vérification: dans épée/bouclier c'est souvent "Dracaufeu Gigamax"
                return f"{display_name} {prefix}"
            return f"{prefix} {display_name}"

        # Autres formes (Alola, Galar...) -> Souvent "Dracaufeu d'Alola"
        # formatted_parts contient ["d'Alola"]

        # Si le terme traduit commence par "de " ou "d'", on le met après le nom
        first_term = formatted_parts[0]
        if lang == 'fr' and (first_term.startswith("de ") or first_term.startswith("d'")):
             return f"{display_name} {first_term}"

        # Par défaut : affiche le nom du Pokémon suivi de la forme (ex: "Giratina Alternative")
        form_suffix = " ".join(formatted_parts)
        return f"{display_name} {form_suffix}"


# Instance globale pour accès facile
_translator = TranslationManager()

def t(key: str, default: str = None) -> str:
    """
    Fonction raccourci pour accéder aux traductions
    
    Args:
        key: Clé de traduction
        default: Valeur par défaut si la traduction n'existe pas
        
    Returns:
        Texte traduit
    """
    return _translator.t(key, default)

def set_language(language_code: str):
    """
    Change la langue de l'application
    
    Args:
        language_code: Code de langue ('fr', 'en', 'de', 'jp')
    """
    _translator.set_language(language_code)

def get_translator() -> TranslationManager:
    """Retourne l'instance du gestionnaire de traductions"""
    return _translator

def translate_type(type_name: str) -> str:
    """
    Fonction raccourci pour traduire un type Pokémon

    Args:
        type_name: Nom du type en anglais

    Returns:
        Nom du type traduit
    """
    return _translator.translate_type(type_name)

def format_form_name(pokemon_name: str, form_name: str, translated_pokemon_name: str = None) -> str:
    """
    Fonction raccourci pour formater un nom de forme
    """
    return _translator.format_form_name(pokemon_name, form_name, translated_pokemon_name)

