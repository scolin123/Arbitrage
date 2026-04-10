from models.odds import OddsFormat

class OddsConverter:
    @staticmethod
    def american_to_decimal(american:int) -> float:
        if american > 0:
            return round(american/100 + 1, 6)
        else:
            return round(100/abs(american) + 1 ,6)
    
    @staticmethod
    def fractional_to_decimal(numerator:int, denominator: int) -> float:
        return round(numerator/ denominator + 1, 6)

    @staticmethod
    def parse_and_normalize(raw: str,fmt: OddsFormat) -> float:
        raw = raw.strip()

        if fmt == OddsFormat.DECIMAL:
            return round(float(raw),6)

        if fmt == OddsFormat.AMERICAN:
            if raw.upper() == "EVEN":
                return 2.0
            return OddsConverter.american_to_decimal(int(raw))
        
        if fmt == OddsFormat.FRACTIONAL:
            numerator, denominator = raw.split("/")
            return OddsConverter.fractional_to_decimal(int(numerator), int(denominator))


