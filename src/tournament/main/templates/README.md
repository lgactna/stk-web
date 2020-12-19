There are some differences between these template files and the BSS exports:
- All references to `assets/` need to be changed to a static file.
- `{% load static %}` must be present.
- Certain characters need to be unescaped (stuff like `&gt` from `>`).

Unfortunately, these need to be done manually at the moment. Fortunately, there aren't too many changes that need to be made for each scenario.