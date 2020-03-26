import json

import frappe


@frappe.whitelist(allow_guest=True)
def generate_model(fields, lang_config) -> str:
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
  return header.replace('{{doctype}}', doctype.replace(' ', ''))


def parse_field_with_type(field: dict, lang_config: dict) -> str:
  _fieldtype = field.get('fieldtype')
  fieldtype = get_type_from_lang_config(_fieldtype, lang_config)
  fieldname = field.get('fieldname')
  child_doc_type: str = lang_config.get('child_doc_type')

  print(child_doc_type)
  if lang_config.get('to_camel_case'):
    decorator: str = lang_config.get('decorator')
    field_parsed = decorator.replace('{{fieldname}}', fieldname) + '\n'
    if field.get('doctype') is None:
      field_parsed += fieldtype + ' ' + snake_to_camel(fieldname) + ';\n'
    else:
      field_parsed += child_doc_type.replace('{{child_doctype}}',
                                             field.get('doctype').replace(' ', '')) + ' ' + snake_to_camel(
          fieldname) + ';\n'
  else:
    if lang_config.get('to_camel_case'):
      field_parsed = child_doc_type.replace('{{child_doctype}}', field.get('doctype')) + ' ' + fieldname + ';\n'
    else:
      field_parsed = fieldtype + ' ' + fieldname + ';\n'

  return field_parsed


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
