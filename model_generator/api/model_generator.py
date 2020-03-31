import json

import frappe
from frappe.utils import cint

# Constants used in the Language Model Configuration
FIELD_TYPE = '{{fieldtype}}'
FIELD_NAME = '{{fieldname}}'
CHILD_DOCTYPE = '{{child_doctype}}'
DOCTYPE = '{{doctype}}'
STD_FIELDS = [
    {'fieldname': 'name', 'fieldtype': 'Link'},
    {'fieldname': 'owner', 'fieldtype': 'Link'},
    {'fieldname': 'idx', 'fieldtype': 'Int'},
    {'fieldname': 'creation', 'fieldtype': 'Date'},
    {'fieldname': 'modified', 'fieldtype': 'Date'},
    {'fieldname': 'modified_by', 'fieldtype': 'Data'},
    {'fieldname': '_user_tags', 'fieldtype': 'Data'},
    {'fieldname': '_liked_by', 'fieldtype': 'Data'},
    {'fieldname': '_comments', 'fieldtype': 'Text'},
    {'fieldname': '_assign', 'fieldtype': 'Text'},
    {'fieldname': 'docstatus', 'fieldtype': 'Int'},
    {'fieldname': 'parent', 'fieldtype': 'Data'},
    {'fieldname': 'parenttype', 'fieldtype': 'Data'},
    {'fieldname': 'parentfield', 'fieldtype': 'Data'}
]


@frappe.whitelist(allow_guest=True)
def generate_model(fields, lang_config, include_std_fields=None) -> str:
  if frappe.model.db_exists('Language Model Configuration', lang_config):
    language_config = frappe.get_doc('Language Model Configuration', lang_config).as_dict()
  else:
    frappe.throw('Language Model Configuration: {0} does not exist'.format(lang_config))

  if isinstance(fields, str):
    fields_dict: dict = json.loads(fields)
  else:
    fields_dict: dict = frappe._dict(fields)

  doctype: str = list(fields_dict.keys())[0]

  if not doctype or doctype is '':
    frappe.throw('Doctype is not specified')

  fields: list = [field for field in fields_dict[doctype]]
  child_doctypes: list = [child_doctype for child_doctype in fields_dict[doctype] if child_doctype.get('doctype')]

  if include_std_fields:
    # Parse to int
    if isinstance(include_std_fields, str):
      include_std_fields = cint(include_std_fields)
    if include_std_fields:
      fields = STD_FIELDS + fields
      for child_doctype in child_doctypes:
        child_doctype['fields'] = STD_FIELDS + child_doctype['fields']

  model = create_model(doctype, fields, language_config)
  for child_doctype in child_doctypes:
    model += create_model(child_doctype.get('doctype'), child_doctype.get('fields'), language_config)

  return model


def create_model(doctype: str, fields: list, language_config: dict) -> str:
  final_string: str = begin_file(doctype, language_config.get('signature_start'))

  fields_parsed: str = ''
  for field in fields:
    fields_parsed += parse_field_with_type(field, language_config)

  final_string += fields_parsed
  final_string += language_config.get('signature_end')
  return final_string


def begin_file(doctype: str, header: str) -> str:
  return header.replace(DOCTYPE, doctype.replace(' ', ''))


def parse_field_with_type(field: dict, lang_config: dict) -> str:
  _fieldtype = field.get('fieldtype')
  fieldtype = get_type_from_lang_config(_fieldtype, lang_config)
  fieldname = field.get('fieldname')
  child_doctype_template: str = lang_config.get('child_doctype_template') or ''

  if lang_config.get('to_camel_case'):
    decorator: str = lang_config.get('decorator') or ''
    field_parsed = decorator.replace(FIELD_NAME, fieldname) + '\n'

    field_parsed += apply_variable_and_type_template(fieldname, fieldtype,
                                                     lang_config.get('type_and_variable_template'),
                                                     True,
                                                     field.get('doctype'), child_doctype_template)
  else:
    field_parsed = apply_variable_and_type_template(fieldname, fieldtype,
                                                    lang_config.get('type_and_variable_template'),
                                                    False,
                                                    field.get('doctype'), child_doctype_template)

  return field_parsed


def apply_variable_and_type_template(fieldname: str, fieldtype: str, template: str, is_snake_to_camel=False,
                                     child_doctype=None, child_doc_template=None):
  if is_snake_to_camel:
    if child_doctype:
      print(child_doc_template)
      _fieldtype = child_doc_template.replace(CHILD_DOCTYPE, child_doctype.replace(' ', ''))
      print(_fieldtype)
      return template.replace(FIELD_TYPE, _fieldtype).replace(FIELD_NAME, snake_to_camel(fieldname))
    else:
      return template.replace(FIELD_TYPE, fieldtype).replace(FIELD_NAME, snake_to_camel(fieldname))
  else:
    if child_doctype:

      _fieldtype = child_doc_template.replace(CHILD_DOCTYPE, child_doctype.replace(' ', ''))

      return template.replace(FIELD_TYPE, _fieldtype).replace(FIELD_NAME, fieldname)
    else:
      return template.replace(FIELD_TYPE, fieldtype).replace(FIELD_NAME, fieldname)


def get_type_from_lang_config(field_type: str, lang_config: dict) -> str:
  data_type_map: list = lang_config.get('data_type_map')
  existing_data_type = list(filter(lambda data_type: data_type.get('field_type') == field_type, data_type_map))

  if len(existing_data_type):
    _fieldtype = existing_data_type[0].get('data_type')
  else:
    _fieldtype = lang_config.get('default_type')

  return _fieldtype


def snake_to_camel(snake_string: str) -> str:
  components = snake_string.split('_')
  return components[0] + ''.join(x.title() for x in components[1:])
