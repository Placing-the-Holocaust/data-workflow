import spacy
from spacy.language import Language
import json
import folium
from folium import plugins
from spacy.tokens import Doc, Span

Span.set_extension("coordinates", default=None, force=True)
Span.set_extension("maps", default=None)

@Language.factory("spancat_to_ner")
class SpancatToNER:
    def __init__(self, nlp, name):
        self.nlp = nlp

    def __call__(self, doc):
        # Convert spancat spans to NER spans
        ents = []
        for span in doc.spans["sc"]:
            # Take first label if multiple exist
            label = span.label_.split("|")[0]
            ent = Span(doc, span.start, span.end, label=label)
            ents.append(ent)
        
        # Set entities on doc
        doc.ents = spacy.util.filter_spans(ents)
        return doc


@Language.factory("entity_geo_locator")
class EntityGeoLocator:
    def __init__(self, nlp, name, coordinates_json, mappings_json):
        self.nlp = nlp
        self.coordinates = self.load_mappings(coordinates_json)
        self.mappings = self.load_mappings(mappings_json)

    def map_entities(self, doc):
        for ent in doc.ents:
            lowered_ent = ent.text.lower()
            normalized_ent = ''.join([char for char in lowered_ent if char.isalpha() or char.isspace()]).strip()
            if normalized_ent in self.mappings:
                ent._.maps = self.mappings[normalized_ent]
                # print(ent)
                # print(ent._.maps)
        return doc

    def load_mappings(self, path):
        with open(path, 'r') as file:
            return json.load(file)

    def __call__(self, doc):
        for ent in doc.ents:
            if ent.text in self.coordinates:
                ent._.set('coordinates', self.coordinates[ent.text])
        doc = self.map_entities(doc)
        return doc

    def visualize(self, doc, style='pin'):
        m = folium.Map(location=[52.434455, 10.782223], zoom_start=4)

        if style == 'pin':
            for ent in doc.ents:
                coordinates = getattr(ent._, 'coordinates', None)
                if coordinates and len(coordinates) == 2:
                    try:
                        lat, lon = coordinates
                        folium.Marker(
                            location=[lat, lon],
                            popup=ent.text
                        ).add_to(m)
                    except Exception as e:
                        print(f"Error adding marker for {ent.text}: {e}")

        elif style == 'density':
            # Collect all coordinates
            points = [getattr(ent._, 'coordinates', None) for ent in doc.ents
                      if getattr(ent._, 'coordinates', None) is not None]
            # Add heatmap
            m.add_child(plugins.HeatMap(points, radius=15))

        return m


class GeoPipeline:
    def __init__(self, model="ph-trf", coordinates_json='./assets/coords_map.json', mappings_json='./assets/mapping.json'):
        mapping_data_config = {"coordinates_json": "./assets/coords_map.json", "mappings_json": "./assets/mapping.json"}

        nlp = spacy.load("/Users/wjbmattingly/projects/placing-holocaust-trf/ph-trf")
        # nlp = spacy.blank("en")
        # nlp.add_pipe("gliner_spacy", config=gliner_config)
        
        self.nlp = nlp
        self.nlp.add_pipe("spancat_to_ner")
        self.coordinates_json = coordinates_json
        self.mappings_json = mappings_json
        self.nlp.add_pipe("entity_geo_locator", last=True, config={"coordinates_json": self.coordinates_json, "mappings_json": self.mappings_json})
        

    def process(self, text):
        return self.nlp(text)

    def visualize(self, doc, style='pin'):
        entity_geo_locator = self.nlp.get_pipe("entity_geo_locator")
        return entity_geo_locator.visualize(doc, style=style)
    