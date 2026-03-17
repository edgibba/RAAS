from django import template

register = template.Library()


@register.filter
def br_num(value):
    """
    Formata número no padrão pt-BR: ponto como separador de milhar,
    vírgula como separador decimal.
    Ex: 1111.84703223 → 1.111,84703223
    """
    try:
        s = str(value).strip()
        if not s or s in ("-", "None"):
            return value

        negative = s.startswith("-")
        if negative:
            s = s[1:]

        integer_part, _, decimal_part = s.partition(".")

        # Adiciona ponto a cada 3 dígitos na parte inteira
        groups = []
        while len(integer_part) > 3:
            groups.insert(0, integer_part[-3:])
            integer_part = integer_part[:-3]
        groups.insert(0, integer_part)
        formatted_int = ".".join(groups)

        result = ("-" if negative else "") + formatted_int
        if decimal_part:
            result += "," + decimal_part

        return result
    except (ValueError, TypeError, AttributeError):
        return value
