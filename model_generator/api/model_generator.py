import json

import frappe


@frappe.whitelist(allow_guest=True)
def generate_model(fields, lang_config) -> str:
  if isinstance(fields, str):
    fields_dict: dict = json.loads(fields)
  else:
    fields_dict: dict = frappe._dict(fields)

  doctype: str = list(fields_dict.keys())[0]

  if not doctype or doctype is '':
    frappe.throw('Doctype is not specified')

  if frappe.model.db_exists('Language Model Configuration', lang_config):
    language_config = frappe.get_doc('Language Model Configuration', lang_config).as_dict()
  else:
    frappe.throw('Language Model Configuration: {0} does not exist'.format(lang_config))

  fields: list = [field for field in fields_dict[doctype] if field.get('doctype') is None]

  # TODO: Handle child doctypes
  child_doctypes: list = [child_doctype for child_doctype in fields_dict[doctype] if child_doctype.get('doctype')]

  final_string: str = begin_file(doctype, 'class {{doctype}} {\n\n')

  fields_parsed: str = ''
  for field in fields:
    fields_parsed += parse_field_with_type(field, language_config)

  final_string += fields_parsed
  final_string += end_file()

  return final_string


def begin_file(doctype: str, header: str) -> str:
  return header.replace('{{doctype}}', doctype)


def end_file() -> str:
  return '\n}'


def parse_field_with_type(field: dict, lang_config: dict) -> str:
  _fieldtype = field.get('fieldtype')
  fieldtype = get_type_from_lang_config(_fieldtype, lang_config)
  fieldname = field.get('fieldname')
  return fieldtype + ' ' + fieldname + ';\n'


def get_type_from_lang_config(field_type: str, lang_config: dict) -> str:
  data_type_map: list = lang_config.get('data_type_map')
  existing_data_type = list(filter(lambda data_type: data_type.get('field_type') == field_type, data_type_map))

  if len(existing_data_type):
    _fieldtype = existing_data_type[0].get('data_type')
  else:
    _fieldtype = lang_config.get('default_type')

  return _fieldtype


# TODO:
def snake_to_camel(snake_string: str) -> str:
  pass
