import copy
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import hypothesis_jsonschema

from .base import Base

# TODO: use these
# import subprocess
# import tempfile
# import hypothesis
# from pathlib import Path
# import jinja2
# import jsonschema
# from hypothesis import assume, given, settings


@dataclass
class SpecValidator(Base):
    feature_strategies: Optional[Any] = None
    raw_schema: Optional[Dict[Any, Any]] = None
    cleaned_schema: Optional[Dict[Any, Any]] = None

    def validate(self) -> int:
        self.load_schema()
        self.clean_schema()
        self.make_strategies()
        return 1

    def load_schema(self):
        schema_path = next(self.output.glob("lsp*synthetic.schema.json"))
        self.raw_schema = json.loads(schema_path.read_text())

    def clean_schema(self):
        """ at present, we can't merge `description` properties: this brute
            forces all string descriptions
        """
        assert self.raw_schema

        def _strip_desc(schema) -> Any:
            if isinstance(schema, dict):
                val = schema.get("description")
                if isinstance(val, str):
                    schema.pop("description")
                return {k: _strip_desc(v) for k, v in schema.items()}
            elif isinstance(schema, list):
                return [_strip_desc(v) for v in schema]
            else:
                return schema

        self.cleaned_schema = _strip_desc(copy.deepcopy(self.raw_schema))

    def make_strategies(self):
        """ make strategies for each feature

            We don't want, and can't, use _AnyFeature as a baseline for the strategy:
            - it's too big
            - it has some circular references, apparently
        """
        assert self.cleaned_schema
        schema = self.cleaned_schema
        defs = schema["definitions"]
        features = defs["_AnyFeature"]["anyOf"]
        strats = self.feature_strategies = {}

        for feature in features:
            feature_ref = feature["$ref"].split("/")[-1]
            feature_name = feature_ref.replace("Feature", "")
            feature_schema = {k: v for k, v in schema.items() if k not in ["$ref"]}
            feature_schema.update(defs[feature_ref])
            strat = None
            try:
                strat = hypothesis_jsonschema.from_schema(feature_schema)
            except Exception as err:
                self.log.warn(str(err)[:64])
            strats[feature_name] = strat
