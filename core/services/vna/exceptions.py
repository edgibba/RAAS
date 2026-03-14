class CalculadoraVNAError(Exception):
    pass


class IndiceNaoEncontradoError(CalculadoraVNAError):
    pass


class SerieMensalNaoEncontradaError(CalculadoraVNAError):
    pass


class CalendarioIncompletoError(CalculadoraVNAError):
    pass


class ParametroInvalidoError(CalculadoraVNAError):
    pass