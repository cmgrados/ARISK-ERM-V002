"""Advanced validators for ARISK ERM - Fase 3c."""

from typing import Any
from rest_framework import serializers
from decimal import Decimal


# ============================================================================
# CREDIT RISK VALIDATORS
# ============================================================================

def validate_dni_peru(value: str) -> str:
    """Validate Peruvian DNI format (8 digits)."""
    if not value or not value.isdigit():
        raise serializers.ValidationError("DNI debe contener solo dígitos.")
    if len(value) != 8:
        raise serializers.ValidationError("DNI peruano debe tener exactamente 8 dígitos.")
    return value


def validate_ruc_peru(value: str) -> str:
    """Validate Peruvian RUC format (11 digits)."""
    if not value or not value.isdigit():
        raise serializers.ValidationError("RUC debe contener solo dígitos.")
    if len(value) != 11:
        raise serializers.ValidationError("RUC peruano debe tener exactamente 11 dígitos.")
    return value


def validate_rate_percentage(value: Decimal) -> Decimal:
    """Validate that rate is between 0 and 100."""
    if value < 0 or value > 100:
        raise serializers.ValidationError("La tasa debe estar entre 0 y 100%.")
    return value


def validate_currency_code(value: str) -> str:
    """Validate currency code is valid (PEN, USD, EUR, etc)."""
    valid_currencies = ['PEN', 'USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD']
    if value not in valid_currencies:
        raise serializers.ValidationError(
            f"Moneda no válida. Opciones: {', '.join(valid_currencies)}"
        )
    return value


def validate_portfolio_balance(current: Decimal, past_due: Decimal, total: Decimal) -> bool:
    """Validate that portfolio balances sum correctly."""
    calculated_total = current + past_due
    if calculated_total != total:
        raise serializers.ValidationError(
            f"Portfolio total ({total}) no coincide con suma de vigente ({current}) + vencido ({past_due}) = {calculated_total}"
        )
    return True


# ============================================================================
# RISK VALIDATORS
# ============================================================================

def validate_risk_score(value: int) -> int:
    """Validate risk score is between 1 and 25."""
    if value < 1 or value > 25:
        raise serializers.ValidationError("Risk score debe estar entre 1 y 25.")
    return value


def validate_probability_value(value: int) -> int:
    """Validate probability scale value is between 1 and 5."""
    if value < 1 or value > 5:
        raise serializers.ValidationError("Valor de probabilidad debe estar entre 1 y 5.")
    return value


def validate_impact_value(value: int) -> int:
    """Validate impact scale value is between 1 and 5."""
    if value < 1 or value > 5:
        raise serializers.ValidationError("Valor de impacto debe estar entre 1 y 5.")
    return value


# ============================================================================
# FINANCIAL VALIDATORS
# ============================================================================

def validate_positive_amount(value: Decimal) -> Decimal:
    """Validate that amount is positive."""
    if value < 0:
        raise serializers.ValidationError("El monto debe ser positivo.")
    return value


def validate_non_negative_amount(value: Decimal) -> Decimal:
    """Validate that amount is non-negative."""
    if value < 0:
        raise serializers.ValidationError("El monto no puede ser negativo.")
    return value


def validate_provision_percentage(value: Decimal) -> Decimal:
    """Validate that provision is between 0 and 100%."""
    if value < 0 or value > 100:
        raise serializers.ValidationError("La provisión debe estar entre 0% y 100%.")
    return value


def validate_pd_percentage(value: Decimal) -> Decimal:
    """Validate Probability of Default is between 0 and 100%."""
    if value < 0 or value > 100:
        raise serializers.ValidationError("PD (Probability of Default) debe estar entre 0% y 100%.")
    return value


def validate_lgd_percentage(value: Decimal) -> Decimal:
    """Validate Loss Given Default is between 0 and 100%."""
    if value < 0 or value > 100:
        raise serializers.ValidationError("LGD (Loss Given Default) debe estar entre 0% y 100%.")
    return value


# ============================================================================
# ORGANIZATION VALIDATORS
# ============================================================================

def validate_organization_name(value: str) -> str:
    """Validate organization name is not empty and reasonable length."""
    if not value or len(value.strip()) < 3:
        raise serializers.ValidationError("Nombre de organización debe tener al menos 3 caracteres.")
    if len(value) > 200:
        raise serializers.ValidationError("Nombre de organización no puede exceder 200 caracteres.")
    return value.strip()


# ============================================================================
# AUTHENTICATION VALIDATORS
# ============================================================================

def validate_password_strength(value: str) -> str:
    """Validate password meets minimum security requirements."""
    if len(value) < 8:
        raise serializers.ValidationError("Contraseña debe tener al menos 8 caracteres.")
    if not any(char.isupper() for char in value):
        raise serializers.ValidationError("Contraseña debe contener al menos una mayúscula.")
    if not any(char.isdigit() for char in value):
        raise serializers.ValidationError("Contraseña debe contener al menos un número.")
    return value


def validate_email_format(value: str) -> str:
    """Validate email format and prevent disposable emails."""
    if "@" not in value or "." not in value.split("@")[1]:
        raise serializers.ValidationError("Formato de email inválido.")

    # Block common disposable email domains
    disposable_domains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
    domain = value.split("@")[1].lower()
    if domain in disposable_domains:
        raise serializers.ValidationError("No se permiten direcciones de email temporales.")

    return value.lower()


# ============================================================================
# DATE/TIME VALIDATORS
# ============================================================================

def validate_disbursement_before_maturity(disbursement_date, maturity_date) -> bool:
    """Validate that disbursement date is before maturity date."""
    if disbursement_date >= maturity_date:
        raise serializers.ValidationError(
            "Fecha de desembolso debe ser anterior a fecha de vencimiento."
        )
    return True
