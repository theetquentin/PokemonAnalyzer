"""
Styles et utilitaires d'affichage pour l'interface
"""

# Emojis par type (clé = nom anglais)
TYPE_EMOJIS = {
    "normal": "⚪",
    "fire": "🔥",
    "water": "💧",
    "electric": "⚡",
    "grass": "🌿",
    "ice": "❄️",
    "fighting": "👊",
    "poison": "☠️",
    "ground": "🏜️",
    "flying": "🦅",
    "psychic": "🔮",
    "bug": "🐛",
    "rock": "🪨",
    "ghost": "👻",
    "dragon": "🐉",
    "dark": "🌑",
    "steel": "⚙️",
    "fairy": "✨"
}

# Mapping inversé : traduit → anglais (pour toutes les langues)
TYPE_NAME_TO_ENGLISH = {
    # Français
    "Normal": "normal", "Feu": "fire", "Eau": "water", "Électrik": "electric",
    "Plante": "grass", "Glace": "ice", "Combat": "fighting", "Poison": "poison",
    "Sol": "ground", "Vol": "flying", "Psy": "psychic", "Insecte": "bug",
    "Roche": "rock", "Spectre": "ghost", "Dragon": "dragon", "Ténèbres": "dark",
    "Acier": "steel", "Fée": "fairy",

    # English
    "Normal": "normal", "Fire": "fire", "Water": "water", "Electric": "electric",
    "Grass": "grass", "Ice": "ice", "Fighting": "fighting", "Poison": "poison",
    "Ground": "ground", "Flying": "flying", "Psychic": "psychic", "Bug": "bug",
    "Rock": "rock", "Ghost": "ghost", "Dragon": "dragon", "Dark": "dark",
    "Steel": "steel", "Fairy": "fairy",

    # Deutsch
    "Kampf": "fighting", "Gift": "poison", "Boden": "ground", "Flug": "flying",
    "Psycho": "psychic", "Käfer": "bug", "Gestein": "rock", "Geist": "ghost",
    "Drache": "dragon", "Unlicht": "dark", "Stahl": "steel", "Fee": "fairy",
    "Feuer": "fire", "Wasser": "water", "Elektro": "electric", "Pflanze": "grass",
    "Eis": "ice",

    # Español
    "Lucha": "fighting", "Veneno": "poison", "Tierra": "ground", "Volador": "flying",
    "Psíquico": "psychic", "Bicho": "bug", "Roca": "rock", "Fantasma": "ghost",
    "Dragón": "dragon", "Siniestro": "dark", "Acero": "steel", "Hada": "fairy",
    "Fuego": "fire", "Agua": "water", "Eléctrico": "electric", "Planta": "grass",
    "Hielo": "ice",

    # Italiano
    "Normale": "normal", "Lotta": "fighting", "Veleno": "poison", "Terra": "ground",
    "Volante": "flying", "Psico": "psychic", "Coleottero": "bug", "Roccia": "rock",
    "Spettro": "ghost", "Drago": "dragon", "Buio": "dark", "Acciaio": "steel",
    "Folletto": "fairy", "Fuoco": "fire", "Acqua": "water", "Elettro": "electric",
    "Erba": "grass", "Ghiaccio": "ice",

    # 日本語
    "ノーマル": "normal", "かくとう": "fighting", "どく": "poison", "じめん": "ground",
    "ひこう": "flying", "エスパー": "psychic", "むし": "bug", "いわ": "rock",
    "ゴースト": "ghost", "ドラゴン": "dragon", "あく": "dark", "はがね": "steel",
    "フェアリー": "fairy", "ほのお": "fire", "みず": "water", "でんき": "electric",
    "くさ": "grass", "こおり": "ice"
}

def get_type_emoji(type_name):
    """
    Retourne l'emoji correspondant au type
    Accepte les noms de types dans toutes les langues
    """
    # D'abord essaye de trouver dans le mapping
    if type_name in TYPE_NAME_TO_ENGLISH:
        type_en = TYPE_NAME_TO_ENGLISH[type_name]
        return TYPE_EMOJIS.get(type_en, "❓")

    # Sinon essaye en minuscules (pour les noms anglais directs)
    type_lower = type_name.lower()
    if type_lower in TYPE_EMOJIS:
        return TYPE_EMOJIS[type_lower]

    # Debug: affiche le type non trouvé
    print(f"[WARN] Type emoji non trouvé pour: '{type_name}'")
    return "❓"

# Couleurs des types (fournies par l'utilisateur)
TYPE_COLORS = {
    "normal": "#9FA19F",
    "fighting": "#FF8000",
    "flying": "#81B9EF",
    "poison": "#9141CB",
    "ground": "#915121",
    "rock": "#AFA981",
    "bug": "#91A119",
    "ghost": "#704170",
    "steel": "#60A1B8",
    "fire": "#E62829",
    "water": "#2980EF",
    "grass": "#3FA129",
    "electric": "#FAC000",
    "psychic": "#EF4179",
    "ice": "#3DCEF3",
    "dragon": "#5060E1",
    "dark": "#624D4E",
    "fairy": "#EF70EF"
}

def get_type_badge_html(type_name_en, type_name_translated):
    """
    Génère le HTML pour un badge de type avec icône et couleur
    """
    color = TYPE_COLORS.get(type_name_en.lower(), "#777777")
    
    # Chemin vers l'icône
    import os
    from core.utils import get_resource_path
    icon_path = get_resource_path(f"assets/types/{type_name_en.lower()}.png")
    # Convertit en chemin absolu avec forward slashes pour HTML/Qt
    icon_path_str = str(icon_path).replace(os.sep, '/')
    
    html = f"""
    <span style="
        background-color: {color};
        color: white;
        border-radius: 4px;
        padding: 10px 8px;
        font-weight: bold;
        font-size: 14px;
        vertical-align: middle;
    ">
        <img src="{icon_path_str}" width="20" height="20" style="vertical-align: middle;" />
        <span style="color: white; font-weight: bold; font-size: 12px; vertical-align: middle; margin-left: 4px; margin-top: 12px;">
            {type_name_translated.upper()}
        </span>
    </span>
    """
    return html

def get_analysis_badge_html(type_name_en, type_name_translated, multiplier):
    """
    Génère le HTML pour un badge de type dans le tableau d'analyse
    Utilise un tableau HTML pour garantir l'alignement vertical dans Qt
    """
    color = TYPE_COLORS.get(type_name_en.lower(), "#777777")
    
    # Chemin vers l'icône
    import os
    from core.utils import get_resource_path
    icon_path = get_resource_path(f"assets/types/{type_name_en.lower()}.png")
    icon_path_str = str(icon_path).replace(os.sep, '/')
    
    # On utilise un tableau pour l'alignement vertical parfait entre l'icône et le texte
    # et pour l'espacement avec le multiplicateur
    # Note: Qt RichText ne supporte pas flexbox, on utilise vertical-align: middle sur img et span
    html = f"""
    <table cellspacing="0" cellpadding="0" style="margin-left: auto; margin-right: auto;">
        <tr>
            <td valign="middle">
                <span style="
                    background-color: {color};
                    border-radius: 4px;
                    padding: 4px 8px 4px 4px;
                ">
                    <img src="{icon_path_str}" width="20" height="20" style="vertical-align: middle;" />
                    <span style="color: white; font-weight: bold; font-size: 12px; vertical-align: middle; margin-left: 4px;">
                        {type_name_translated.upper()}
                    </span>
                </span>
            </td>
            <td width="20"></td>
            <td valign="middle" style="font-weight: bold; color: #333; font-size: 12px;">
                (×{multiplier})
            </td>
        </tr>
    </table>
    """
    return html
