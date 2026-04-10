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

if __name__ == "__main__":
    # American
    print(OddsConverter.american_to_decimal(150))    # expect 2.5
    print(OddsConverter.american_to_decimal(-110))   # expect 1.909091
    print(OddsConverter.american_to_decimal(-200))   # expect 1.5

    # Fractional
    print(OddsConverter.fractional_to_decimal(5, 2)) # expect 3.5

    # parse_and_normalize
    print(OddsConverter.parse_and_normalize("+150", OddsFormat.AMERICAN))  # 2.5
    print(OddsConverter.parse_and_normalize("EVEN", OddsFormat.AMERICAN))  # 2.0
    print(OddsConverter.parse_and_normalize("5/2", OddsFormat.FRACTIONAL)) # 3.5
    print(OddsConverter.parse_and_normalize("2.50", OddsFormat.DECIMAL))   # 2.5
