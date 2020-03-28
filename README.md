# Model Generator

Generate models to different languages based on Doctype.

## Motive

During development, the doctypes are defined usually by the backend team. Front-end development teams will require to write the models for these doctypes in the front-end as models which usually counts much as manual and repetitive task.

Since it's repetitive and somewhat an annoying task, I saw an oppurtunity to some extent automate this task with some minor configurations in the doctype and refactoring in the frontend which will hopefully reduce the time wasted achieving this task.

### Doctypes included

- Language Model Configuration
- Model Generator

#### Language Model Configuration

A doctype to configure the templates and data types for each language. By default, there are two fixtures defined:
- Dart/Flutter
- TS/JS

Configurations include:

- **Data Type Map**. For instance, `Data` fieldtype is a `String` in Dart/Flutter.
- Variable and type template. For instance for *Dart*:
  ```
  {{fieldtype}} {{fieldname}};
  ```
  which results in:
  ```dart
  String fullName;
  ```
- **Signature Start** which indicates the beginning of the model like *class* or *interface*.
- **Signature End** which indicates the end of the model of a *class* or *interface*.
- **Child Doctype Template** which indicates the representation of a child doctype in a model. For instance in *Dart*:
   ```
   List<{{child_doctype}}>
   ```
   which results in:
   ```dart
   List<Role> roles;
   ```
- **To Camel Case** which converts the field names from the standard naming in Frappé, snake-case, to camel-case which is the convention, *Dart*, for instance.
- **Decorator (Only used if To Camel Case is checked** where this is used for languages (Dart or C#, for instance), to convert the naming between backend and frontend.

## Contribution
Contributions in all shapes, forms and sizes are welcome :)

## License

MIT
