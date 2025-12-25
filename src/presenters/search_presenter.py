"""
Presenter pour l'onglet de recherche
Gère la logique de recherche et de filtrage
"""
from PySide6.QtCore import QObject

class SearchPresenter(QObject):
    """
    Presenter pour la recherche
    """
    
    def __init__(self, view, pokemon_database, type_calculator):
        super().__init__()
        self.view = view
        self.db = pokemon_database
        self.calc = type_calculator
        
        self._connect_signals()
        
    def _connect_signals(self):
        """Connecte les signaux de la vue"""
        # Connect to new search_requested signal (after debounce)
        self.view.search_requested.connect(self.filter_pokemon)
        # Connect to pokemon selection
        self.view.pokemon_selected.connect(self.on_pokemon_selected)
        
    def on_pokemon_selected(self, pokemon_name):
        """Called when a Pokemon is selected from dropdown"""
        # Optionally show details or do something with selection
        pass
        
    def filter_pokemon(self):
        """Filtre les Pokémon selon les critères"""
        filters = self.view.get_filters()
        type_filter = filters['type']
        gen_filter = filters['gen']
        search_text = filters['text']
        
        results = []
        
        # Stratégie de recherche :
        # 1. Si texte : recherche par nom
        # 2. Sinon si type : recherche par type
        # 3. Sinon si génération : recherche par génération
        # 4. Sinon : rien (ou top 50 ?)
        
        if search_text:
            # Recherche par nom (retourne des dicts)
            results = self.db.search_pokemon(search_text, limit=20)
            
            # Applique les autres filtres en mémoire sur les résultats
            if type_filter != "all":
                results = [p for p in results if type_filter in p['types']]
            if gen_filter != "Toutes":
                results = [p for p in results if str(p['generation']) == gen_filter]
                
        elif type_filter != "all":
            # Recherche par type
            results = self.db.get_pokemon_by_type(type_filter)
            
            # Filtre par génération
            if gen_filter != "Toutes":
                results = [p for p in results if str(p['generation']) == gen_filter]
                
        elif gen_filter != "Toutes":
            # Recherche par génération
            results = self.db.get_pokemon_by_generation(int(gen_filter))
            
        else:
            # Aucun filtre : on ne charge rien pour éviter de spammer l'API
            # Ou on pourrait afficher les premiers du Pokédex si on avait un cache
            results = []

        # Formatage pour la vue : liste de tuples (nom, data)
        matches = [(p['name'], p) for p in results]

        # Met à jour la vue (limite à 20 résultats max)
        self.view.display_results(matches[:20])
        
    def refresh_results(self):
        """Rafra îchit les résultats (utile lors du changement de langue)"""
        # On réapplique simplement les filtres, ce qui va retraduire les résultats
        self.filter_pokemon()
