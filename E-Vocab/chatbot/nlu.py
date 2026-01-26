from pathlib import Path

import joblib
import spacy


class NLUProcessor:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        intent_model_path = base_dir / "intent_model.joblib"
        entity_model_path = base_dir / "entity_model"

        self.intent_model = joblib.load(intent_model_path)
        self.entity_model = spacy.load(entity_model_path)

    def parse(self, text: str):
        predicted_intent = self.intent_model.predict([text])[0]
        intent_confidence = self.intent_model.predict_proba([text]).max()

        doc = self.entity_model(text)
        entities = [
            {"entity": ent.label_, "value": ent.text}
            for ent in doc.ents
        ]

        return {
            "intent": {"name": predicted_intent, "confidence": intent_confidence},
            "entities": entities,
        }


nlu_processor = NLUProcessor()


