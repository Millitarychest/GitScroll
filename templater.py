class staticTemplater:
    def template_load_set(key, value, template):
        """Set a template variable to a value"""
        with open(template, "r") as f:
            raw_template = f.read()
            masked_template = raw_template.replace("{{" + key + "}}", value)
        return masked_template

    def template_set(key, value, templateString):
        """Set a template variable to a value"""
        masked_template = templateString.replace("{{" + key + "}}", value)
        return masked_template