from decimal import Decimal

class BalanceValidationService:
    @staticmethod
    def validate_accounting_equation(detalles_procesados):
        """
        Recibe una lista de diccionarios extraída del Excel/CSV:
        [{'tipo': 'ACTIVO', 'nivel': 1, 'monto': 100000}, {'tipo': 'PASIVO', 'nivel': 1, 'monto': 60000}, ...]
        Y asegura que Activo = Pasivo + Patrimonio.
        """
        total_activo = Decimal('0.00')
        total_pasivo = Decimal('0.00')
        total_patrimonio = Decimal('0.00')

        # Acumular según las cuentas contables de Nivel 1 (Las agrupadoras principales)
        for row in detalles_procesados:
            if row.get('nivel') == 1:
                tipo = row.get('tipo', '').upper()
                monto = Decimal(str(row.get('monto', 0)))
                
                if tipo == 'ACTIVO':
                    total_activo += monto
                elif tipo == 'PASIVO':
                    total_pasivo += monto
                elif tipo == 'PATRIMONIO':
                    total_patrimonio += monto

        total_fuentes = total_pasivo + total_patrimonio
        
        # Validación con tolerancia por posibles pequeños redondeos de centavos en Excel
        diferencia = abs(total_activo - total_fuentes)
        
        if diferencia > Decimal('0.01'):
            raise ValueError(
                f"Error de Ecuación Contable: Activos ({total_activo}) no cuadra con "
                f"Pasivos + Patrimonio ({total_fuentes}). Diferencia: {diferencia}"
            )
        
        return True
