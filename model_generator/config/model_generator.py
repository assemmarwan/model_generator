from __future__ import unicode_literals
from frappe import _


def get_data():
  data = [
    {
      "label": _("Model Generator"),
      "icon": "fa fa-wrench",
      "items": [
        {
          "type": "doctype",
          "name": "Model Generator",
          "label": _("Model Generator"),
          "onboard": 1,
          "description": _("Generate Models for target language")
        },
        {
          "type": "doctype",
          "name": "Language Model Configuration",
          "label": _("Language Model Configuration"),
          "onboard": 1,
          "description": _("Configure language settings for model generator")
        }
      ]
    }

  ]
  return data
